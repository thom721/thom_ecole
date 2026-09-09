from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class LiveSession(Base):
    __tablename__ = "live_sessions"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    # Généré (secrets.token_hex), jamais dérivé du titre — un nom de salle
    # Jitsi doit être unique sur toute l'instance, pas seulement ce cours.
    room_name = Column(String(64), unique=True, nullable=False)
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    join_window_minutes_before = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="live_sessions")
    attendance = relationship("LiveSessionAttendance", back_populates="session", cascade="all, delete-orphan")


class LiveSessionAttendance(Base):
    __tablename__ = "live_session_attendance"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("live_sessions.id"), nullable=False)
    student_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    left_at = Column(DateTime, nullable=True)

    session = relationship("LiveSession", back_populates="attendance")
