from datetime import datetime, timedelta, timezone

import jwt
from sqlalchemy.orm import Session

from app.config.Config import settings
from app.Models.MLiveSession import LiveSession, LiveSessionAttendance
from app.Models.MUser import User
from app.Models.MCompletion import CompletionItemType
from app.Helper.completion import mark_complete_if_absent


def build_jitsi_jwt(session: LiveSession, user: User, is_moderator: bool) -> str:
    """Signe un JWT accepté par le plugin prosody `token_affiliation` du
    serveur Jitsi self-hébergé (voir plan Épic 17) — `context.user.moderator`
    est le champ que ce plugin lit pour distinguer animateur/participant,
    pas un claim de premier niveau."""
    now = datetime.now(timezone.utc)
    payload = {
        "aud": settings.JITSI_JWT_APP_ID,
        "iss": settings.JITSI_JWT_APP_ID,
        "sub": "*",
        "room": session.room_name,
        "iat": now,
        "exp": now + timedelta(hours=2),
        "context": {
            "user": {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "moderator": is_moderator,
            },
            "features": {"recording": False, "livestreaming": False},
        },
    }
    return jwt.encode(payload, settings.JITSI_JWT_APP_SECRET, algorithm="HS256")


def is_session_joinable(session: LiveSession, is_teaching: bool) -> tuple[bool, str | None]:
    if is_teaching:
        return True, None
    now = datetime.now(timezone.utc)
    if session.scheduled_start is not None:
        window_start = session.scheduled_start.replace(tzinfo=timezone.utc) - timedelta(minutes=session.join_window_minutes_before)
        if now < window_start:
            return False, f"La session n'est pas encore ouverte (ouverture {session.join_window_minutes_before} min avant le début programmé)"
    if session.scheduled_end is not None:
        window_end = session.scheduled_end.replace(tzinfo=timezone.utc)
        if now > window_end:
            return False, "La session est terminée"
    return True, None


def record_join(db: Session, session_id: str, student_id: str) -> None:
    open_attendance = (
        db.query(LiveSessionAttendance)
        .filter(LiveSessionAttendance.session_id == session_id, LiveSessionAttendance.student_id == student_id,
                LiveSessionAttendance.left_at.is_(None))
        .first()
    )
    if open_attendance is None:
        db.add(LiveSessionAttendance(session_id=session_id, student_id=student_id))
        db.commit()


def record_leave(db: Session, session_id: str, student_id: str) -> None:
    open_attendance = (
        db.query(LiveSessionAttendance)
        .filter(LiveSessionAttendance.session_id == session_id, LiveSessionAttendance.student_id == student_id,
                LiveSessionAttendance.left_at.is_(None))
        .order_by(LiveSessionAttendance.joined_at.desc())
        .first()
    )
    if open_attendance is not None:
        open_attendance.left_at = datetime.now(timezone.utc)
        db.commit()

    # Déclencheur unique, fixe (voir plan Épic 17, décision de périmètre 2) :
    # quitter la session au moins une fois compte comme "a assisté".
    mark_complete_if_absent(db, student_id, CompletionItemType.live_session, session_id)
