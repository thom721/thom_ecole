import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SAEnum

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class BlockType(str, enum.Enum):
    my_courses = "my_courses"
    calendar = "calendar"
    recent_activity = "recent_activity"
    grades_overview = "grades_overview"
    badges = "badges"
    messages = "messages"
    online_users = "online_users"
    html = "html"


class BlockRegion(str, enum.Enum):
    main = "main"
    side = "side"


class UserBlockInstance(Base):
    """Un seul contexte : le tableau de bord personnel de l'utilisateur —
    pas le système de contexte générique site/catégorie/cours/page du vrai
    Moodle (voir plan Épic 15)."""

    __tablename__ = "user_block_instances"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    block_type = Column(SAEnum(BlockType), nullable=False)
    region = Column(SAEnum(BlockRegion), nullable=False, default=BlockRegion.side)
    weight = Column(Integer, nullable=False, default=0)
    is_visible = Column(Boolean, nullable=False, default=True)
    config_json = Column(Text, nullable=True)  # {"title", "content"} pour html uniquement

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
