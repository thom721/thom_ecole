import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class GroupMode(str, enum.Enum):
    """Réutilisé par toute activité qui adopte le mode de groupe (Forum,
    Choice pour l'instant — voir plan Épic 5). `no_groups` et
    `visible_groups` affichent tous les deux l'intégralité du contenu ;
    seul `separate_groups` filtre réellement (simplification assumée et
    documentée, voir plan)."""
    no_groups = "no_groups"
    separate_groups = "separate_groups"
    visible_groups = "visible_groups"


class Group(Base):
    __tablename__ = "groups"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    grouping_links = relationship("GroupingGroup", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_members_group_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    group = relationship("Group", back_populates="members")


class Grouping(Base):
    __tablename__ = "groupings"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    group_links = relationship("GroupingGroup", back_populates="grouping", cascade="all, delete-orphan")


class GroupingGroup(Base):
    __tablename__ = "grouping_groups"
    __table_args__ = (
        UniqueConstraint("grouping_id", "group_id", name="uq_grouping_groups_grouping_group"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    grouping_id = Column(String(36), ForeignKey("groupings.id"), nullable=False)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)

    grouping = relationship("Grouping", back_populates="group_links")
    group = relationship("Group", back_populates="grouping_links")
