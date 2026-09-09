import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class NotificationKind(str, enum.Enum):
    new_grade = "new_grade"
    new_forum_post = "new_forum_post"
    new_message = "new_message"
    # Ajouté en Épic 17 — élargissement manuel de l'ENUM MySQL requis dans
    # la migration (même technique que les précédents épics).
    new_live_session = "new_live_session"
    # "due_soon" volontairement absent — rien ne le déclenche en Phase 4
    # (nécessiterait un scheduler, explicitement écarté, voir plan).


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    kind = Column(SAEnum(NotificationKind), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    link_url = Column(String(500), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
