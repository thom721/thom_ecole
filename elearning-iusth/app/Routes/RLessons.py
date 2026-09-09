from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MLesson import Lesson, LessonPage, LessonAnswer, LessonAttempt, LessonAttemptStatus, LessonPageAttempt, LessonPageType
from app.Models.MGrade import GradeItem, GradeItemKind
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Models.MNotification import NotificationKind
from app.Models.MCompletion import CompletionItemType
from app.Schemas.SLesson import (
    LessonCreate, LessonUpdate, LessonOut, LessonConfigOut, LessonPageConfigOut,
    LessonPageCreate, LessonPageUpdate, LessonAnswerConfigOut, LessonPageAttemptGrade,
)
from app.dependencies.auth import get_current_active_user, assert_course_role
from app.Helper.completion import mark_complete_if_absent
from app.Helper.lesson_engine import compute_score
from app.Helper.notifications import notify

router = APIRouter(tags=["lessons"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_lesson_and_course(db: Session, lesson_id: str) -> tuple[Lesson, str]:
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leçon introuvable")
    section = db.query(Section).filter(Section.id == lesson.section_id).first()
    return lesson, section.course_id


def _get_page_and_course(db: Session, page_id: str) -> tuple[LessonPage, str]:
    page = db.query(LessonPage).filter(LessonPage.id == page_id).first()
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page introuvable")
    _lesson, course_id = _get_lesson_and_course(db, page.lesson_id)
    return page, course_id


@router.post("/sections/{section_id}/lessons", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
def create_lesson(
    section_id: str, data: LessonCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    lesson = Lesson(section_id=section_id, **data.model_dump())
    db.add(lesson)
    db.flush()

    # Auto-enregistrement au carnet de notes (voir plan Épic 9, même patron
    # qu'Assignment/Quiz en Phase 3) — non catégorisé par défaut.
    db.add(GradeItem(course_id=section.course_id, lesson_id=lesson.id, kind=GradeItemKind.lesson))

    db.commit()
    db.refresh(lesson)
    return lesson


@router.get("/lessons/{lesson_id}/config", response_model=LessonConfigOut)
def get_lesson_config(
    lesson_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    lesson, course_id = _get_lesson_and_course(db, lesson_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    pages = [
        LessonPageConfigOut(
            id=p.id, lesson_id=p.lesson_id, page_type=p.page_type, title=p.title, content=p.content,
            points=p.points, sort_order=p.sort_order,
            answers=[LessonAnswerConfigOut.model_validate(a) for a in p.answers],
        )
        for p in lesson.pages
    ]
    return LessonConfigOut(
        id=lesson.id, section_id=lesson.section_id, course_id=course_id,
        title=lesson.title, description=lesson.description, is_visible=lesson.is_visible,
        has_password=lesson.has_password, max_attempts_per_question=lesson.max_attempts_per_question,
        time_limit_minutes=lesson.time_limit_minutes, allow_retake=lesson.allow_retake, pages=pages,
    )


@router.patch("/lessons/{lesson_id}", response_model=LessonOut)
def update_lesson(
    lesson_id: str, data: LessonUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    lesson, course_id = _get_lesson_and_course(db, lesson_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    lesson, course_id = _get_lesson_and_course(db, lesson_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if db.query(LessonAttempt).filter(LessonAttempt.lesson_id == lesson_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Cette leçon a déjà des tentatives — suppression bloquée pour préserver l'historique des notes")

    db.delete(lesson)
    db.commit()


@router.post("/lessons/{lesson_id}/pages", response_model=LessonPageConfigOut, status_code=status.HTTP_201_CREATED)
def add_lesson_page(
    lesson_id: str, data: LessonPageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _lesson, course_id = _get_lesson_and_course(db, lesson_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    page = LessonPage(
        lesson_id=lesson_id, page_type=data.page_type, title=data.title, content=data.content,
        points=data.points, sort_order=data.sort_order,
    )
    db.add(page)
    db.flush()
    for a in data.answers:
        db.add(LessonAnswer(page_id=page.id, **a.model_dump()))
    db.commit()
    db.refresh(page)
    return LessonPageConfigOut(
        id=page.id, lesson_id=page.lesson_id, page_type=page.page_type, title=page.title, content=page.content,
        points=page.points, sort_order=page.sort_order,
        answers=[LessonAnswerConfigOut.model_validate(a) for a in page.answers],
    )


@router.patch("/lesson-pages/{page_id}", response_model=LessonPageConfigOut)
def update_lesson_page(
    page_id: str, data: LessonPageUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    page, course_id = _get_page_and_course(db, page_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    update_data = data.model_dump(exclude_unset=True, exclude={"answers"})
    for field, value in update_data.items():
        setattr(page, field, value)

    if data.answers is not None:
        for existing in list(page.answers):
            db.delete(existing)
        db.flush()
        for a in data.answers:
            db.add(LessonAnswer(page_id=page.id, **a.model_dump()))

    db.commit()
    db.refresh(page)
    return LessonPageConfigOut(
        id=page.id, lesson_id=page.lesson_id, page_type=page.page_type, title=page.title, content=page.content,
        points=page.points, sort_order=page.sort_order,
        answers=[LessonAnswerConfigOut.model_validate(a) for a in page.answers],
    )


@router.delete("/lesson-pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson_page(
    page_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    page, course_id = _get_page_and_course(db, page_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if db.query(LessonPageAttempt).filter(LessonPageAttempt.page_id == page_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Cette page a déjà des réponses enregistrées — suppression bloquée")

    db.delete(page)
    db.commit()


@router.get("/lessons/{lesson_id}/essay-grading")
def list_essay_grading_queue(
    lesson_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    lesson, course_id = _get_lesson_and_course(db, lesson_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    essay_page_ids = [p.id for p in lesson.pages if p.page_type == LessonPageType.essay]
    pending = (
        db.query(LessonPageAttempt)
        .join(LessonAttempt, LessonAttempt.id == LessonPageAttempt.attempt_id)
        .filter(LessonPageAttempt.page_id.in_(essay_page_ids), LessonPageAttempt.points_awarded.is_(None))
        .all()
        if essay_page_ids else []
    )
    return [
        {
            "id": pa.id, "attempt_id": pa.attempt_id, "page_id": pa.page_id,
            "page_title": pa.page.title, "student_id": pa.attempt.student_id,
            "answer_text": pa.answer_text, "answered_at": pa.answered_at,
        }
        for pa in pending
    ]


@router.patch("/lesson-page-attempts/{page_attempt_id}/grade")
def grade_essay_page_attempt(
    page_attempt_id: str, data: LessonPageAttemptGrade,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    page_attempt = db.query(LessonPageAttempt).filter(LessonPageAttempt.id == page_attempt_id).first()
    if page_attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réponse introuvable")
    attempt = page_attempt.attempt
    lesson, course_id = _get_lesson_and_course(db, attempt.lesson_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    page_attempt.points_awarded = data.points_awarded
    page_attempt.feedback = data.feedback
    page_attempt.graded_by = current_user.id
    page_attempt.graded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(attempt)

    score, has_pending_essay = compute_score(attempt)
    if not has_pending_essay:
        attempt.status = LessonAttemptStatus.completed
        attempt.score = score
        attempt.graded_at = page_attempt.graded_at
        db.commit()
        db.refresh(attempt)
        mark_complete_if_absent(db, attempt.student_id, CompletionItemType.lesson, lesson.id)
        notify(db, attempt.student_id, NotificationKind.new_grade,
               title=f"Leçon notée : {lesson.title}", body=f"Score : {attempt.score}/{attempt.max_score}",
               link_url=f"/student/lessons/{lesson.id}")

    return {
        "id": attempt.id, "status": attempt.status, "score": attempt.score,
        "max_score": attempt.max_score, "graded_at": attempt.graded_at,
    }
