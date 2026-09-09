from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MQuiz import Quiz, QuizQuestion, QuizDrawRule, QuizAttempt
from app.Models.MQuestion import Question
from app.Models.MGrade import GradeItem, GradeItemKind
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Models.MAccessLog import AccessItemType
from app.Helper.access_log import log_access
from app.Schemas.SQuiz import (
    QuizCreate, QuizUpdate, QuizOut, QuizConfigOut,
    QuizQuestionCreate, QuizQuestionOut, QuizDrawRuleCreate, QuizDrawRuleOut,
)
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role

router = APIRouter(tags=["quizzes"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_quiz_and_course(db: Session, quiz_id: str) -> tuple[Quiz, str]:
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz introuvable")
    section = db.query(Section).filter(Section.id == quiz.section_id).first()
    return quiz, section.course_id


@router.post("/sections/{section_id}/quizzes", response_model=QuizOut, status_code=status.HTTP_201_CREATED)
def create_quiz(
    section_id: str, data: QuizCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    quiz = Quiz(section_id=section_id, **data.model_dump())
    db.add(quiz)
    db.flush()

    # Auto-enregistrement au carnet de notes (voir plan Phase 3) — non
    # catégorisé par défaut, le professeur l'assigne ensuite via PATCH.
    db.add(GradeItem(course_id=section.course_id, quiz_id=quiz.id, kind=GradeItemKind.quiz))

    db.commit()
    db.refresh(quiz)
    return quiz


@router.get("/quizzes/{quiz_id}", response_model=QuizOut)
def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    quiz, course_id = _get_quiz_and_course(db, quiz_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    log_access(db, current_user, course_id, AccessItemType.quiz, quiz_id)
    return quiz


@router.get("/quizzes/{quiz_id}/config", response_model=QuizConfigOut)
def get_quiz_config(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    quiz, course_id = _get_quiz_and_course(db, quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    quiz_questions = []
    for qq in quiz.quiz_questions:
        quiz_questions.append({
            "id": qq.id, "question_id": qq.question_id, "points": qq.points,
            "sort_order": qq.sort_order, "question_text": qq.question.question_text,
            "question_type": qq.question.question_type,
        })

    return QuizConfigOut(
        id=quiz.id, section_id=quiz.section_id, course_id=course_id, title=quiz.title, description=quiz.description,
        time_limit_minutes=quiz.time_limit_minutes, max_attempts=quiz.max_attempts,
        shuffle_questions=quiz.shuffle_questions, is_visible=quiz.is_visible,
        opens_at=quiz.opens_at, closes_at=quiz.closes_at,
        quiz_questions=quiz_questions,
        draw_rules=[QuizDrawRuleOut.model_validate(r) for r in quiz.draw_rules],
    )


@router.patch("/quizzes/{quiz_id}", response_model=QuizOut)
def update_quiz(
    quiz_id: str, data: QuizUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    quiz, course_id = _get_quiz_and_course(db, quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(quiz, field, value)
    db.commit()
    db.refresh(quiz)
    return quiz


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    quiz, course_id = _get_quiz_and_course(db, quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Ce quiz a déjà des tentatives — suppression bloquée pour préserver l'historique des notes")

    db.delete(quiz)
    db.commit()


@router.post("/quizzes/{quiz_id}/questions", response_model=QuizQuestionOut, status_code=status.HTTP_201_CREATED)
def add_quiz_question(
    quiz_id: str, data: QuizQuestionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    quiz, course_id = _get_quiz_and_course(db, quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    question = db.query(Question).filter(Question.id == data.question_id).first()
    if question is None or question.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question invalide pour ce cours")

    qq = QuizQuestion(quiz_id=quiz_id, **data.model_dump())
    db.add(qq)
    db.commit()
    db.refresh(qq)
    return qq


@router.delete("/quiz-questions/{quiz_question_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_quiz_question(
    quiz_question_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    qq = db.query(QuizQuestion).filter(QuizQuestion.id == quiz_question_id).first()
    if qq is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrée introuvable")
    _quiz, course_id = _get_quiz_and_course(db, qq.quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    db.delete(qq)
    db.commit()


@router.post("/quizzes/{quiz_id}/draw-rules", response_model=QuizDrawRuleOut, status_code=status.HTTP_201_CREATED)
def add_draw_rule(
    quiz_id: str, data: QuizDrawRuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    quiz, course_id = _get_quiz_and_course(db, quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    pool_query = db.query(Question).filter(Question.category_id == data.category_id, Question.is_active.is_(True))
    if data.question_type:
        pool_query = pool_query.filter(Question.question_type == data.question_type)
    pool_size = pool_query.count()
    if pool_size < data.count:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f"Seulement {pool_size} question(s) disponible(s) dans cette catégorie pour {data.count} demandée(s)")

    rule = QuizDrawRule(quiz_id=quiz_id, **data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/draw-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_draw_rule(
    rule_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rule = db.query(QuizDrawRule).filter(QuizDrawRule.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Règle introuvable")
    _quiz, course_id = _get_quiz_and_course(db, rule.quiz_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    db.delete(rule)
    db.commit()
