from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section, Course
from app.Models.MCalendar import CalendarEvent
from app.Models.MAssignment import Assignment
from app.Models.MQuiz import Quiz
from app.Models.MLiveSession import LiveSession
from app.Models.MEnrollment import Enrollment, CourseRole, EnrollmentStatus
from app.Models.MUser import User, SystemRole
from app.Schemas.SCalendar import CalendarEventCreate, CalendarEventUpdate, CalendarEventOut
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role

router = APIRouter(tags=["calendar"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _virtual_events_for_course(db: Session, course_id: str, date_from: datetime, date_to: datetime) -> list[CalendarEventOut]:
    """Calculés en direct — jamais stockés (voir plan Phase 4)."""
    events = []

    assignments = (
        db.query(Assignment)
        .join(Section, Section.id == Assignment.section_id)
        .filter(Section.course_id == course_id, Assignment.due_date.isnot(None),
                Assignment.due_date >= date_from, Assignment.due_date <= date_to)
        .all()
    )
    for a in assignments:
        events.append(CalendarEventOut(
            id=f"assignment:{a.id}", course_id=course_id, title=f"Échéance : {a.title}",
            description=a.description, start_at=a.due_date, end_at=None,
            event_type="assignment_due", source_id=a.id,
        ))

    quizzes = (
        db.query(Quiz)
        .join(Section, Section.id == Quiz.section_id)
        .filter(Section.course_id == course_id)
        .filter((Quiz.opens_at.isnot(None)) | (Quiz.closes_at.isnot(None)))
        .all()
    )
    for q in quizzes:
        start = q.opens_at or q.closes_at
        end = q.closes_at
        if start > date_to or (end and end < date_from):
            continue
        events.append(CalendarEventOut(
            id=f"quiz:{q.id}", course_id=course_id, title=f"Quiz : {q.title}",
            description=q.description, start_at=start, end_at=end,
            event_type="quiz_window", source_id=q.id,
        ))

    live_sessions = (
        db.query(LiveSession)
        .join(Section, Section.id == LiveSession.section_id)
        .filter(Section.course_id == course_id, LiveSession.scheduled_start.isnot(None),
                LiveSession.scheduled_start >= date_from, LiveSession.scheduled_start <= date_to)
        .all()
    )
    for ls in live_sessions:
        events.append(CalendarEventOut(
            id=f"live_session:{ls.id}", course_id=course_id, title=f"En direct : {ls.title}",
            description=ls.description, start_at=ls.scheduled_start, end_at=ls.scheduled_end,
            event_type="live_session", source_id=ls.id,
        ))

    return events


@router.get("/calendar", response_model=list[CalendarEventOut])
def get_calendar(
    course_id: str | None = Query(None),
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if course_id:
        if current_user.system_role != SystemRole.admin:
            if get_enrollment_or_none(db, course_id, current_user.id) is None:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
        course_ids = [course_id]
    else:
        course_ids = [
            e.course_id for e in
            db.query(Enrollment).filter(Enrollment.user_id == current_user.id, Enrollment.status == EnrollmentStatus.active).all()
        ]

    manual_query = db.query(CalendarEvent).filter(
        CalendarEvent.start_at >= from_, CalendarEvent.start_at <= to,
    )
    if course_id:
        manual_query = manual_query.filter((CalendarEvent.course_id == course_id) | (CalendarEvent.course_id.is_(None)))
    else:
        manual_query = manual_query.filter((CalendarEvent.course_id.in_(course_ids)) | (CalendarEvent.course_id.is_(None))) \
            if course_ids else manual_query.filter(CalendarEvent.course_id.is_(None))
    manual_events = [
        CalendarEventOut(id=e.id, course_id=e.course_id, title=e.title, description=e.description,
                          start_at=e.start_at, end_at=e.end_at, event_type="manual", source_id=None)
        for e in manual_query.all()
    ]

    virtual_events = []
    for cid in course_ids:
        virtual_events.extend(_virtual_events_for_course(db, cid, from_, to))

    return manual_events + virtual_events


@router.post("/calendar/events", response_model=CalendarEventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    data: CalendarEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if data.course_id is None:
        if current_user.system_role != SystemRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Réservé à l'admin pour un événement site")
    else:
        if db.query(Course).filter(Course.id == data.course_id).first() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")
        assert_course_role(db, current_user, data.course_id, _TEACHING_ROLES)

    event = CalendarEvent(created_by=current_user.id, **data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return CalendarEventOut(id=event.id, course_id=event.course_id, title=event.title,
                             description=event.description, start_at=event.start_at, end_at=event.end_at,
                             event_type="manual", source_id=None)


def _get_manual_event_or_404(db: Session, event_id: str) -> CalendarEvent:
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Événement introuvable")
    return event


def _assert_event_edit_role(db: Session, current_user: User, event: CalendarEvent) -> None:
    if event.course_id is None:
        if current_user.system_role != SystemRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Réservé à l'admin")
    else:
        assert_course_role(db, current_user, event.course_id, _TEACHING_ROLES)


@router.patch("/calendar/events/{event_id}", response_model=CalendarEventOut)
def update_event(
    event_id: str, data: CalendarEventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    event = _get_manual_event_or_404(db, event_id)
    _assert_event_edit_role(db, current_user, event)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return CalendarEventOut(id=event.id, course_id=event.course_id, title=event.title,
                             description=event.description, start_at=event.start_at, end_at=event.end_at,
                             event_type="manual", source_id=None)


@router.delete("/calendar/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    event = _get_manual_event_or_404(db, event_id)
    _assert_event_edit_role(db, current_user, event)
    db.delete(event)
    db.commit()
