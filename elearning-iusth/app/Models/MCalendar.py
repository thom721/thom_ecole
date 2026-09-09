from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class CalendarEvent(Base):
    """Événements MANUELS uniquement — jamais de copie d'une échéance de
    devoir ou d'une fenêtre de quiz (voir plan Phase 4 : calculées en
    direct à la lecture, jamais dupliquées ici)."""

    __tablename__ = "calendar_events"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=True)  # null = site
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
