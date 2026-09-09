import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SAEnum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid
from app.Models.MCompletion import CompletionItemType

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class BadgeStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class BadgeCriteriaType(str, enum.Enum):
    activity = "activity"
    course = "course"
    grade = "grade"
    cohort = "cohort"


class BadgeCriteriaLogic(str, enum.Enum):
    and_ = "and"
    or_ = "or"


class Badge(Base):
    __tablename__ = "badges"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=True)  # null = badge "site"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_emoji = Column(String(8), nullable=True)
    status = Column(SAEnum(BadgeStatus), nullable=False, default=BadgeStatus.draft)
    criteria_logic = Column(SAEnum(BadgeCriteriaLogic), nullable=False, default=BadgeCriteriaLogic.and_)
    expire_days = Column(Integer, nullable=True)  # null = jamais
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    criteria = relationship("BadgeCriterion", back_populates="badge", cascade="all, delete-orphan")
    issued = relationship("BadgeIssued", back_populates="badge", cascade="all, delete-orphan")


class BadgeCriterion(Base):
    """Une seule table polymorphe pour les 4 types de critère retenus —
    même patron que `AccessCondition` (Épic 7). `logic` répété sur chaque
    ligne d'un même badge (toutes censées porter la même valeur, imposé en
    route, comme `AccessCondition.logic`)."""

    __tablename__ = "badge_criteria"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    badge_id = Column(String(36), ForeignKey("badges.id"), nullable=False)
    criteria_type = Column(SAEnum(BadgeCriteriaType), nullable=False)
    logic = Column(SAEnum(BadgeCriteriaLogic), nullable=False, default=BadgeCriteriaLogic.and_)

    # criteria_type == activity
    required_item_type = Column(SAEnum(CompletionItemType), nullable=True)
    required_item_id = Column(String(36), nullable=True)

    # criteria_type == grade
    min_percent = Column(Numeric(5, 2), nullable=True)

    # criteria_type == cohort
    cohort_id = Column(String(36), ForeignKey("cohorts.id"), nullable=True)

    badge = relationship("Badge", back_populates="criteria")
    met_rows = relationship("BadgeCriterionMet", back_populates="criterion", cascade="all, delete-orphan")


class BadgeCriterionMet(Base):
    """Suivi de progression PAR critère, PAR utilisateur — nécessaire à
    l'agrégation `and` (savoir lesquels sont déjà acquis avant que tous le
    soient), jamais réinitialisé une fois posé."""

    __tablename__ = "badge_criteria_met"
    __table_args__ = (
        UniqueConstraint("criterion_id", "user_id", name="uq_badge_criteria_met_criterion_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    criterion_id = Column(String(36), ForeignKey("badge_criteria.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    met_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    criterion = relationship("BadgeCriterion", back_populates="met_rows")


class BadgeIssued(Base):
    __tablename__ = "badge_issued"
    __table_args__ = (
        UniqueConstraint("badge_id", "user_id", name="uq_badge_issued_badge_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    badge_id = Column(String(36), ForeignKey("badges.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    unique_hash = Column(String(64), nullable=False)
    awarded_manually = Column(Boolean, nullable=False, default=False)

    badge = relationship("Badge", back_populates="issued")
