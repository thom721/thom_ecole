from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class StaffMeeting(Base):
    """Réunion du personnel, indépendante de tout cours (voir plan Épic
    21) — contrairement à LiveSession (Épic 17), volontairement lié à
    une Section/un cours. Réutilise directement l'infra Jitsi déjà
    construite (Helper/live_sessions.py::build_jitsi_jwt, duck-typing sur
    .room_name)."""

    __tablename__ = "staff_meetings"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    room_name = Column(String(64), unique=True, nullable=False)
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    invitees = relationship("StaffMeetingInvitee", back_populates="meeting", cascade="all, delete-orphan")


class StaffMeetingInvitee(Base):
    __tablename__ = "staff_meeting_invitees"
    __table_args__ = (
        UniqueConstraint("meeting_id", "user_id", name="uq_staff_meeting_invitees_meeting_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("staff_meetings.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    meeting = relationship("StaffMeeting", back_populates="invitees")
