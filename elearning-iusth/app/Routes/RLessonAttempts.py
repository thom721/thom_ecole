from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MLesson import (
    Lesson, LessonPage, LessonPageType, LessonAttempt, LessonAttemptStatus, LessonPageAttempt,
)
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Models.MNotification import NotificationKind
from app.Models.MCompletion import CompletionItemType
from app.Models.MAccessLog import AccessItemType
from app.Schemas.SLesson import LessonAttemptStartIn, LessonAttemptOut, LessonAnswerIn, LessonAnswerResultOut
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.completion import mark_complete_if_absent
from app.Helper.access_conditions import is_item_accessible
from app.Helper.access_log import log_access
from app.Helper.notifications import notify
from app.Helper.lesson_engine import resolve_answer, resolve_next_page, compute_score

router = APIRouter(tags=["lesson-attempts"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_lesson_and_course(db: Session, lesson_id: str) -> tuple[Lesson, str]:
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leçon introuvable")
    section = db.query(Section).filter(Section.id == lesson.section_id).first()
    return lesson, section.course_id


def _get_attempt_or_404(db: Session, attempt_id: str) -> LessonAttempt:
    attempt = db.query(LessonAttempt).filter(LessonAttempt.id == attempt_id).first()
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tentative introuvable")
    return attempt


def _serialize_page_for_student(page: LessonPage) -> dict:
    """Rendu étudiant — jamais is_correct/jump_type/jump_to_page_id. Les
    réponses ne sont listées (comme des choix) que pour content/
    true_false/multiple_choice ; short_answer/numerical/essay ne montrent
    aucune réponse (l'étudiant tape un texte libre, voir plan Épic 9)."""
    show_answers = page.page_type in (LessonPageType.content, LessonPageType.true_false, LessonPageType.multiple_choice)
    return {
        "id": page.id, "page_type": page.page_type, "title": page.title, "content": page.content,
        "answers": (
            [{"id": a.id, "answer_text": a.answer_text, "sort_order": a.sort_order}
             for a in sorted(page.answers, key=lambda a: a.sort_order)]
            if show_answers else []
        ),
    }


@router.post("/lessons/{lesson_id}/attempts", response_model=LessonAttemptOut, status_code=status.HTTP_201_CREATED)
def start_attempt(
    lesson_id: str, data: LessonAttemptStartIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    lesson, course_id = _get_lesson_and_course(db, lesson_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    if not lesson.is_visible:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leçon introuvable")

    accessible, reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.lesson, lesson_id)
    if not accessible:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="; ".join(reasons) or "Accès restreint")

    if lesson.password and data.password != lesson.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mot de passe incorrect")

    in_progress = (
        db.query(LessonAttempt)
        .filter(LessonAttempt.lesson_id == lesson_id, LessonAttempt.student_id == current_user.id,
                LessonAttempt.status == LessonAttemptStatus.in_progress)
        .first()
    )
    if in_progress is not None:
        return in_progress

    if not lesson.allow_retake:
        completed_before = (
            db.query(LessonAttempt)
            .filter(LessonAttempt.lesson_id == lesson_id, LessonAttempt.student_id == current_user.id,
                    LessonAttempt.status != LessonAttemptStatus.in_progress)
            .first()
        )
        if completed_before is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette leçon ne peut être refaite")

    pages = sorted(lesson.pages, key=lambda p: p.sort_order)
    if not pages:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette leçon n'a aucune page configurée")

    started_at = datetime.now(timezone.utc)
    deadline_at = started_at + timedelta(minutes=lesson.time_limit_minutes) if lesson.time_limit_minutes else None
    max_score = sum((p.points for p in pages if p.page_type != LessonPageType.content), Decimal("0"))

    attempt = LessonAttempt(
        lesson_id=lesson_id, student_id=current_user.id, status=LessonAttemptStatus.in_progress,
        current_page_id=pages[0].id, started_at=started_at, deadline_at=deadline_at, max_score=max_score,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    log_access(db, current_user, course_id, AccessItemType.lesson, lesson_id)
    return attempt


@router.get("/lesson-attempts/{attempt_id}")
def get_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    lesson, course_id = _get_lesson_and_course(db, attempt.lesson_id)

    is_owner = attempt.student_id == current_user.id
    if not is_owner:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    total_gradable = sum(1 for p in lesson.pages if p.page_type != LessonPageType.content)
    seen_pages = {pa.page_id for pa in attempt.page_attempts if pa.page.page_type != LessonPageType.content}
    progress_percent = (len(seen_pages) / total_gradable * 100) if total_gradable else 0.0

    current_page = None
    if attempt.current_page_id:
        page = db.query(LessonPage).filter(LessonPage.id == attempt.current_page_id).first()
        if page is not None:
            current_page = _serialize_page_for_student(page)

    return {
        "id": attempt.id, "lesson_id": attempt.lesson_id, "student_id": attempt.student_id,
        "status": attempt.status, "started_at": attempt.started_at, "deadline_at": attempt.deadline_at,
        "completed_at": attempt.completed_at, "score": attempt.score, "max_score": attempt.max_score,
        "graded_at": attempt.graded_at, "progress_percent": progress_percent, "current_page": current_page,
    }


@router.post("/lesson-attempts/{attempt_id}/pages/{page_id}/answer", response_model=LessonAnswerResultOut)
def answer_page(
    attempt_id: str, page_id: str, data: LessonAnswerIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette tentative ne vous appartient pas")
    if attempt.status != LessonAttemptStatus.in_progress:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette tentative n'est plus modifiable")
    if attempt.current_page_id != page_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette page n'est pas la page courante de la tentative")
    if attempt.deadline_at and datetime.now(timezone.utc) > attempt.deadline_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Temps écoulé")

    page = db.query(LessonPage).filter(LessonPage.id == page_id).first()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page introuvable")

    lesson = page.lesson
    existing_tries = db.query(LessonPageAttempt).filter(
        LessonPageAttempt.attempt_id == attempt_id, LessonPageAttempt.page_id == page_id,
    ).count()
    if lesson.max_attempts_per_question is not None and existing_tries >= lesson.max_attempts_per_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nombre maximum de tentatives atteint pour cette question")

    matched_answer, is_correct, points_awarded, stored_text = resolve_answer(page, data.answer_id, data.answer_text)

    db.add(LessonPageAttempt(
        attempt_id=attempt_id, page_id=page_id, try_number=existing_tries + 1,
        answer_id=matched_answer.id if matched_answer else None, answer_text=stored_text,
        is_correct=is_correct, points_awarded=points_awarded if page.page_type != LessonPageType.essay else None,
    ))

    next_page_id, end_of_lesson = resolve_next_page(page, matched_answer)
    attempt.current_page_id = None if end_of_lesson else next_page_id
    db.commit()

    return LessonAnswerResultOut(
        is_correct=is_correct, points_awarded=points_awarded if page.page_type != LessonPageType.essay else None,
        next_page_id=None if end_of_lesson else next_page_id, end_of_lesson=end_of_lesson,
    )


@router.post("/lesson-attempts/{attempt_id}/complete", response_model=LessonAttemptOut)
def complete_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette tentative ne vous appartient pas")
    if attempt.status != LessonAttemptStatus.in_progress:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette tentative est déjà terminée")

    lesson, _course_id = _get_lesson_and_course(db, attempt.lesson_id)
    score, has_pending_essay = compute_score(attempt)
    attempt.completed_at = datetime.now(timezone.utc)

    if has_pending_essay:
        attempt.status = LessonAttemptStatus.pending_manual_grading
        attempt.score = None
    else:
        attempt.status = LessonAttemptStatus.completed
        attempt.score = score
        attempt.graded_at = attempt.completed_at

    db.commit()
    db.refresh(attempt)

    if attempt.status == LessonAttemptStatus.completed:
        mark_complete_if_absent(db, attempt.student_id, CompletionItemType.lesson, lesson.id)
        notify(db, attempt.student_id, NotificationKind.new_grade,
               title=f"Leçon notée : {lesson.title}", body=f"Score : {attempt.score}/{attempt.max_score}",
               link_url=f"/student/lessons/{lesson.id}")

    return attempt


@router.get("/lessons/{lesson_id}/attempts/mine", response_model=list[LessonAttemptOut])
def list_my_attempts(
    lesson_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _lesson, course_id = _get_lesson_and_course(db, lesson_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return (
        db.query(LessonAttempt)
        .filter(LessonAttempt.lesson_id == lesson_id, LessonAttempt.student_id == current_user.id)
        .order_by(LessonAttempt.started_at.desc())
        .all()
    )
