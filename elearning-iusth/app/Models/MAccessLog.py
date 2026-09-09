import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class AccessItemType(str, enum.Enum):
    course = "course"
    resource = "resource"
    assignment = "assignment"
    quiz = "quiz"
    # Ajouté en Épic 7 pour déclencher l'achèvement automatique "vue" sur
    # un forum (élargissement d'ENUM MySQL manuel dans la migration).
    forum = "forum"
    # Ajouté en Épic 9, même technique.
    lesson = "lesson"
    # Ajouté en Épic 10, même technique.
    workshop = "workshop"
    # Ajouté en Épic 17, même technique.
    live_session = "live_session"
    # Ajouté en Épic 18, même technique.
    interactive_video = "interactive_video"


class AccessLog(Base):
    """Une ligne par vue — pas une table d'état comme ForumReadState, donc
    pas de contrainte unique. Pas de purge automatique (voir plan Phase 5,
    acceptable pour une fonctionnalité qualifiée de "basique")."""

    __tablename__ = "access_logs"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    item_type = Column(SAEnum(AccessItemType), nullable=False)
    item_id = Column(String(36), nullable=True)  # null si item_type == course
    accessed_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
