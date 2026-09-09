import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MQuiz import Quiz, QuizQuestion, QuizDrawRule, QuizAttempt, QuizResponse, QuizAttemptStatus
from app.Models.MQuestion import Question, QuestionType
from app.Helper.question_grading import auto_grade
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Models.MNotification import NotificationKind
from app.Models.MCompletion import CompletionItemType
from app.Schemas.SQuiz import (
    QuizAttemptOut, QuizAttemptSummaryOut, QuizResponseAnswerIn, QuizResponseGrade,
)
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.notifications import notify
from app.Helper.completion import mark_complete_if_absent

router = APIRouter(tags=["quiz-attempts"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_quiz_and_course(db: Session, quiz_id: str) -> tuple[Quiz, str]:
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz introuvable")
    section = db.query(Section).filter(Section.id == quiz.section_id).first()
    return quiz, section.course_id


def _get_attempt_or_404(db: Session, attempt_id: str) -> QuizAttempt:
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tentative introuvable")
    return attempt


@router.post("/quizzes/{quiz_id}/attempts", response_model=QuizAttemptOut, status_code=status.HTTP_201_CREATED)
def start_attempt(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    quiz, course_id = _get_quiz_and_course(db, quiz_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    if not quiz.is_visible:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz introuvable")

    now = datetime.now(timezone.utc)
    if quiz.opens_at and now < quiz.opens_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce quiz n'est pas encore ouvert")
    if quiz.closes_at and now > quiz.closes_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce quiz est fermé")

    existing_count = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == current_user.id)
        .count()
    )
    if quiz.max_attempts is not None and existing_count >= quiz.max_attempts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre maximum de tentatives atteint")

    in_progress = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == current_user.id,
                QuizAttempt.status == QuizAttemptStatus.in_progress)
        .first()
    )
    if in_progress is not None:
        return in_progress

    # Résolution du contenu : entrées fixes + tirage aléatoire par règle,
    # dédoublonné contre les entrées fixes.
    selected = []  # list[(Question, points_override, sort_order)]
    fixed_ids = set()
    for qq in quiz.quiz_questions:
        selected.append((qq.question, qq.points, qq.sort_order))
        fixed_ids.add(qq.question_id)

    for rule in quiz.draw_rules:
        pool_query = db.query(Question).filter(
            Question.category_id == rule.category_id, Question.is_active.is_(True),
        )
        if fixed_ids:
            pool_query = pool_query.filter(~Question.id.in_(fixed_ids))
        if rule.question_type:
            pool_query = pool_query.filter(Question.question_type == rule.question_type)
        pool = pool_query.all()
        if len(pool) < rule.count:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Pas assez de questions disponibles pour le tirage aléatoire")
        drawn = random.sample(pool, rule.count)
        for q in drawn:
            selected.append((q, rule.points, rule.sort_order))
            fixed_ids.add(q.id)

    if not selected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce quiz n'a aucune question configurée")

    if quiz.shuffle_questions:
        random.shuffle(selected)
        selected = [(q, pts, i) for i, (q, pts, _old_order) in enumerate(selected)]
    else:
        selected.sort(key=lambda t: t[2])

    started_at = datetime.now(timezone.utc)
    deadline_at = started_at + timedelta(minutes=quiz.time_limit_minutes) if quiz.time_limit_minutes else None

    attempt = QuizAttempt(
        quiz_id=quiz_id, student_id=current_user.id, status=QuizAttemptStatus.in_progress,
        started_at=started_at, deadline_at=deadline_at,
        max_score=sum((pts if pts is not None else q.default_points) for q, pts, _ in selected),
    )
    db.add(attempt)
    db.flush()

    for order, (question, pts, _orig_order) in enumerate(selected):
        resolved_data = None
        if question.question_type == QuestionType.calculated and question.calculated_datasets:
            # Un seul index tiré, partagé par toutes les variables de la
            # question (validé à la création : même longueur pour toutes) —
            # figé ici, jamais recalculé après coup (voir plan Épic 1).
            dataset_length = len(question.calculated_datasets[0].values)
            picked_index = random.randrange(dataset_length)
            resolved_data = {ds.variable_name: ds.values[picked_index] for ds in question.calculated_datasets}

        db.add(QuizResponse(
            attempt_id=attempt.id, question_id=question.id, sort_order=order,
            points=pts if pts is not None else question.default_points,
            resolved_data=resolved_data,
        ))

    db.commit()
    db.refresh(attempt)
    return attempt


def _rendered_text(question: Question, response: QuizResponse) -> str:
    """`calculated` uniquement : substitue les variables tirées
    (`response.resolved_data`) dans les placeholders `{x}` de l'énoncé.
    Toute autre question renvoie son texte tel quel."""
    if question.question_type == QuestionType.calculated and response.resolved_data:
        try:
            return question.question_text.format(**response.resolved_data)
        except (KeyError, ValueError, IndexError):
            return question.question_text
    return question.question_text


def _serialize_question_for_student(question: Question, response: QuizResponse) -> dict:
    return {
        "response_id": response.id,
        "question_id": question.id,
        "question_type": question.question_type,
        "question_text": _rendered_text(question, response),
        "points": response.points,
        "sort_order": response.sort_order,
        "answer_data": response.answer_data,
        "options": [
            {"id": o.id, "option_text": o.option_text, "sort_order": o.sort_order}
            for o in question.options
        ],
        # multianswer : sous-questions sans leurs bonnes réponses (les
        # options de QCM embarqué restent visibles, il faut bien choisir
        # parmi elles — seul `correct_answers`/l'index correct est masqué).
        "cloze_parts": [
            {
                "position": p.position, "sub_type": p.sub_type,
                "options": (p.correct_answers or {}).get("options") if p.sub_type == QuestionType.multiple_choice else None,
                "points": p.points,
            }
            for p in question.cloze_parts
        ],
    }


def _serialize_question_for_review(question: Question, response: QuizResponse) -> dict:
    base = _serialize_question_for_student(question, response)
    base["is_correct"] = response.is_correct
    base["points_awarded"] = response.points_awarded
    base["feedback"] = response.feedback
    base["options"] = [
        {"id": o.id, "option_text": o.option_text, "match_text": o.match_text, "is_correct": o.is_correct, "sort_order": o.sort_order}
        for o in question.options
    ]
    base["accepted_answers"] = [a.answer_text for a in question.accepted_answers if a.tolerance is None]
    base["numerical_answers"] = [
        {"value": a.answer_text, "tolerance": a.tolerance} for a in question.accepted_answers if a.tolerance is not None
    ]
    base["cloze_parts"] = [
        {"position": p.position, "sub_type": p.sub_type, "correct_answers": p.correct_answers, "points": p.points}
        for p in question.cloze_parts
    ]
    return base


@router.get("/quiz-attempts/{attempt_id}")
def get_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    _quiz, course_id = _get_quiz_and_course(db, attempt.quiz_id)

    is_owner = attempt.student_id == current_user.id
    if not is_owner:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    reveal = attempt.status != QuizAttemptStatus.in_progress
    responses = sorted(attempt.responses, key=lambda r: r.sort_order)
    questions = [
        (_serialize_question_for_review(r.question, r) if reveal else _serialize_question_for_student(r.question, r))
        for r in responses
    ]

    return {
        "id": attempt.id, "quiz_id": attempt.quiz_id, "student_id": attempt.student_id,
        "status": attempt.status, "started_at": attempt.started_at, "deadline_at": attempt.deadline_at,
        "submitted_at": attempt.submitted_at, "score": attempt.score, "max_score": attempt.max_score,
        "graded_at": attempt.graded_at, "questions": questions,
    }


@router.patch("/quiz-attempts/{attempt_id}/responses/{question_id}", response_model=None)
def save_response(
    attempt_id: str, question_id: str, data: QuizResponseAnswerIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette tentative ne vous appartient pas")
    if attempt.status != QuizAttemptStatus.in_progress:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette tentative n'est plus modifiable")
    if attempt.deadline_at and datetime.now(timezone.utc) > attempt.deadline_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Temps écoulé")

    response = (
        db.query(QuizResponse)
        .filter(QuizResponse.attempt_id == attempt_id, QuizResponse.question_id == question_id)
        .first()
    )
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question hors de cette tentative")

    response.answer_data = data.answer_data
    response.answered_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}


@router.post("/quiz-attempts/{attempt_id}/submit", response_model=QuizAttemptOut)
def submit_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette tentative ne vous appartient pas")
    if attempt.status != QuizAttemptStatus.in_progress:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette tentative a déjà été soumise")

    has_essay = False
    for response in attempt.responses:
        if response.question.question_type == QuestionType.essay:
            has_essay = True
            continue
        auto_grade(response.question, response)

    attempt.submitted_at = datetime.now(timezone.utc)
    if has_essay:
        attempt.status = QuizAttemptStatus.pending_manual_grading
        attempt.score = None
    else:
        attempt.status = QuizAttemptStatus.graded
        attempt.score = sum((r.points_awarded or 0) for r in attempt.responses)
        attempt.graded_at = attempt.submitted_at

    db.commit()
    db.refresh(attempt)

    if attempt.status == QuizAttemptStatus.graded:
        quiz, _course_id = _get_quiz_and_course(db, attempt.quiz_id)
        mark_complete_if_absent(db, attempt.student_id, CompletionItemType.quiz, quiz.id)
        notify(db, attempt.student_id, NotificationKind.new_grade,
               title=f"Quiz noté : {quiz.title}", body=f"Score : {attempt.score}/{attempt.max_score}",
               link_url=f"/student/quizzes/{quiz.id}")

    return attempt


@router.get("/quizzes/{quiz_id}/attempts", response_model=list[QuizAttemptSummaryOut])
def list_attempts(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _quiz, course_id = _get_quiz_and_course(db, quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()


@router.get("/quizzes/{quiz_id}/attempts/mine", response_model=list[QuizAttemptSummaryOut])
def list_my_attempts(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Permet à l'étudiant de retrouver ses tentatives passées (et leur
    note) une fois `max_attempts` atteint — même logique que
    Submission, toujours consultable par son propriétaire."""
    _quiz, course_id = _get_quiz_and_course(db, quiz_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == current_user.id)
        .order_by(QuizAttempt.started_at.desc())
        .all()
    )


@router.patch("/quiz-attempts/{attempt_id}/responses/{question_id}/grade", response_model=QuizAttemptOut)
def grade_response(
    attempt_id: str, question_id: str, data: QuizResponseGrade,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    _quiz, course_id = _get_quiz_and_course(db, attempt.quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    response = (
        db.query(QuizResponse)
        .filter(QuizResponse.attempt_id == attempt_id, QuizResponse.question_id == question_id)
        .first()
    )
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réponse introuvable")

    response.points_awarded = data.points_awarded
    response.feedback = data.feedback
    response.graded_by = current_user.id
    response.graded_at = datetime.now(timezone.utc)

    all_graded = all(r.points_awarded is not None for r in attempt.responses)
    if all_graded:
        attempt.status = QuizAttemptStatus.graded
        attempt.score = sum((r.points_awarded or 0) for r in attempt.responses)
        attempt.graded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(attempt)

    if all_graded:
        quiz, _course_id = _get_quiz_and_course(db, attempt.quiz_id)
        mark_complete_if_absent(db, attempt.student_id, CompletionItemType.quiz, quiz.id)
        notify(db, attempt.student_id, NotificationKind.new_grade,
               title=f"Quiz noté : {quiz.title}", body=f"Score : {attempt.score}/{attempt.max_score}",
               link_url=f"/student/quizzes/{quiz.id}")

    return attempt
