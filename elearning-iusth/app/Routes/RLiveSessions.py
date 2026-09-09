import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Course, Section
from app.Models.MLiveSession import LiveSession, LiveSessionAttendance
from app.Models.MEnrollment import Enrollment, CourseRole, EnrollmentStatus
from app.Models.MUser import User, SystemRole
from app.Models.MCompletion import CompletionItemType
from app.Models.MNotification import NotificationKind
from app.Schemas.SLiveSession import (
    LiveSessionCreate, LiveSessionUpdate, LiveSessionOut, LiveSessionDetailOut,
    LiveSessionJoinOut, LiveSessionAttendanceRowOut,
)
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.access_conditions import is_item_accessible
from app.Helper.live_sessions import build_jitsi_jwt, is_session_joinable, record_join, record_leave
from app.Helper.notifications import notify
from app.Helper.email import send_live_session_email
from app.config.Config import settings

router = APIRouter(tags=["live-sessions"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_session_and_course(db: Session, session_id: str) -> tuple[LiveSession, str]:
    session = db.query(LiveSession).filter(LiveSession.id == session_id).first()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session en direct introuvable")
    section = db.query(Section).filter(Section.id == session.section_id).first()
    return session, section.course_id


def _is_teaching(db: Session, current_user: User, course_id: str) -> bool:
    if current_user.system_role == SystemRole.admin:
        return True
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    return enrollment is not None and enrollment.role_in_course in _TEACHING_ROLES


@router.post("/sections/{section_id}/live-sessions", response_model=LiveSessionOut, status_code=status.HTTP_201_CREATED)
def create_live_session(
    section_id: str, data: LiveSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    session = LiveSession(section_id=section_id, room_name=secrets.token_hex(16), **data.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)

    _notify_enrolled_students(db, section.course_id, session)
    return session


def _notify_enrolled_students(db: Session, course_id: str, session: LiveSession) -> None:
    """Notification in-app + email à la création d'une session en direct
    (voir plan Épic 17) — déclenchée une seule fois, à la création,
    jamais un rappel périodique (aucun scheduler dans ce projet)."""
    course = db.query(Course).filter(Course.id == course_id).first()
    students = (
        db.query(User)
        .join(Enrollment, Enrollment.user_id == User.id)
        .filter(Enrollment.course_id == course_id, Enrollment.role_in_course == CourseRole.student,
                Enrollment.status == EnrollmentStatus.active)
        .all()
    )
    link_url = f"{settings.FRONTEND_BASE_URL}/student/live-sessions/{session.id}"
    for student in students:
        notify(db, student.id, NotificationKind.new_live_session,
               title=f"Nouvelle session en direct : {session.title}",
               body=course.full_name, link_url=link_url)
        try:
            send_live_session_email(student.email, student.first_name, course.full_name, session.title,
                                     session.scheduled_start, link_url)
        except Exception as exc:
            # L'envoi d'email est un effet secondaire de la création de la
            # session, pas l'action elle-même (contrairement à la
            # réinitialisation de mot de passe) — un incident SMTP ne doit
            # jamais faire échouer la création de la session ni bloquer la
            # notification des autres étudiants. Toujours visible dans les
            # logs du conteneur, jamais silencieux.
            print(f"[live_sessions] échec d'envoi d'email à {student.email} : {exc}")


@router.get("/live-sessions/{session_id}", response_model=LiveSessionDetailOut)
def get_live_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    session, course_id = _get_session_and_course(db, session_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    is_teaching = _is_teaching(db, current_user, course_id)
    joinable, reason = is_session_joinable(session, is_teaching)
    return LiveSessionDetailOut(
        id=session.id, section_id=session.section_id, title=session.title, description=session.description,
        is_visible=session.is_visible, room_name=session.room_name,
        scheduled_start=session.scheduled_start, scheduled_end=session.scheduled_end,
        join_window_minutes_before=session.join_window_minutes_before,
        is_joinable=joinable, not_joinable_reason=reason,
    )


@router.patch("/live-sessions/{session_id}", response_model=LiveSessionOut)
def update_live_session(
    session_id: str, data: LiveSessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    session, course_id = _get_session_and_course(db, session_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    return session


@router.delete("/live-sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_live_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    session, course_id = _get_session_and_course(db, session_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if db.query(LiveSessionAttendance).filter(LiveSessionAttendance.session_id == session_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Cette session a déjà de la présence enregistrée — suppression bloquée pour préserver l'historique")

    db.delete(session)
    db.commit()


@router.post("/live-sessions/{session_id}/join", response_model=LiveSessionJoinOut)
def join_live_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    session, course_id = _get_session_and_course(db, session_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    is_teaching = _is_teaching(db, current_user, course_id)
    joinable, reason = is_session_joinable(session, is_teaching)
    if not joinable:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)

    accessible, reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.live_session, session_id)
    if not accessible:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="; ".join(reasons))

    if not is_teaching:
        record_join(db, session_id, current_user.id)

    jwt_token = build_jitsi_jwt(session, current_user, is_moderator=is_teaching)
    return LiveSessionJoinOut(jitsi_base_url=settings.JITSI_BASE_URL, room_name=session.room_name, jwt=jwt_token)


@router.post("/live-sessions/{session_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_live_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    session, course_id = _get_session_and_course(db, session_id)
    is_teaching = _is_teaching(db, current_user, course_id)
    if not is_teaching:
        record_leave(db, session_id, current_user.id)


@router.get("/live-sessions/{session_id}/attendance", response_model=list[LiveSessionAttendanceRowOut])
def get_attendance(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    session, course_id = _get_session_and_course(db, session_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    rows = (
        db.query(LiveSessionAttendance)
        .filter(LiveSessionAttendance.session_id == session_id)
        .order_by(LiveSessionAttendance.joined_at)
        .all()
    )
    by_student: dict[str, list[LiveSessionAttendance]] = {}
    for row in rows:
        by_student.setdefault(row.student_id, []).append(row)

    result = []
    for student_id, entries in by_student.items():
        student = db.query(User).filter(User.id == student_id).first()
        result.append(LiveSessionAttendanceRowOut(
            student_id=student_id,
            student_name=f"{student.first_name} {student.last_name}" if student else "?",
            first_joined_at=entries[0].joined_at,
            last_left_at=entries[-1].left_at,
            is_currently_in_session=any(e.left_at is None for e in entries),
            join_count=len(entries),
        ))
    return result
