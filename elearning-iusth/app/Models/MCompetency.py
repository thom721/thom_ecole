import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid
from app.Models.MCompletion import CompletionItemType

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class CompetencyRuleType(str, enum.Enum):
    none = "none"
    all = "all"
    any = "any"


class CompetencyRuleOutcome(str, enum.Enum):
    none = "none"
    evidence = "evidence"
    complete = "complete"


class UserCompetencyStatus(str, enum.Enum):
    idle = "idle"
    waiting_for_review = "waiting_for_review"
    in_review = "in_review"


class PlanStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    complete = "complete"
    waiting_for_review = "waiting_for_review"
    in_review = "in_review"


class EvidenceAction(str, enum.Enum):
    log = "log"
    complete = "complete"
    override = "override"


class CompetencyFramework(Base):
    __tablename__ = "competency_frameworks"
    __table_args__ = (
        UniqueConstraint("idnumber", name="uq_competency_frameworks_idnumber"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    idnumber = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    scale_id = Column(String(36), ForeignKey("scales.id"), nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    competencies = relationship("Competency", back_populates="framework", cascade="all, delete-orphan")


class Competency(Base):
    __tablename__ = "competencies"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    framework_id = Column(String(36), ForeignKey("competency_frameworks.id"), nullable=False)
    parent_id = Column(String(36), ForeignKey("competencies.id"), nullable=True)
    name = Column(String(255), nullable=False)
    idnumber = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    scale_id = Column(String(36), ForeignKey("scales.id"), nullable=True)  # remplace celle du référentiel si renseignée
    proficient_min_rank = Column(Integer, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    rule_type = Column(SAEnum(CompetencyRuleType), nullable=False, default=CompetencyRuleType.none)
    rule_outcome = Column(SAEnum(CompetencyRuleOutcome), nullable=False, default=CompetencyRuleOutcome.none)

    framework = relationship("CompetencyFramework", back_populates="competencies")
    children = relationship("Competency", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("Competency", remote_side=[id], back_populates="children")
    module_links = relationship("ModuleCompetency", back_populates="competency", cascade="all, delete-orphan")


class CourseCompetency(Base):
    __tablename__ = "course_competencies"
    __table_args__ = (
        UniqueConstraint("course_id", "competency_id", name="uq_course_competencies_course_competency"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    competency = relationship("Competency")


class ModuleCompetency(Base):
    """Lie une compétence à UNE activité précise (item_type/item_id,
    réutilise `CompletionItemType` — même polymorphisme que
    `ActivityCompletion`/`AccessCondition`/`BadgeCriterion`)."""

    __tablename__ = "module_competencies"
    __table_args__ = (
        UniqueConstraint("item_type", "item_id", "competency_id", name="uq_module_competencies_item_competency"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    item_type = Column(SAEnum(CompletionItemType), nullable=False)
    item_id = Column(String(36), nullable=False)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False)

    competency = relationship("Competency", back_populates="module_links")


class UserCompetency(Base):
    """État GLOBAL, tous cours confondus — distinct de
    `UserCompetencyCourse` (voir plan Épic 13)."""

    __tablename__ = "user_competencies"
    __table_args__ = (
        UniqueConstraint("user_id", "competency_id", name="uq_user_competencies_user_competency"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False)
    status = Column(SAEnum(UserCompetencyStatus), nullable=False, default=UserCompetencyStatus.idle)
    proficiency = Column(Boolean, nullable=True)
    grade_rank = Column(Integer, nullable=True)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    evidence = relationship("CompetencyEvidence", back_populates="user_competency", cascade="all, delete-orphan")


class UserCompetencyCourse(Base):
    """État PAR COURS — même compétence transversale, évaluation
    potentiellement différente d'un cours à l'autre."""

    __tablename__ = "user_competency_courses"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", "competency_id", name="uq_user_competency_courses_user_course_competency"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False)
    proficiency = Column(Boolean, nullable=True)
    grade_rank = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class CompetencyEvidence(Base):
    """Journal d'audit — toujours rattaché à l'enregistrement GLOBAL
    (`UserCompetency`), même quand déclenché depuis un cours précis, pour
    un historique centralisé (voir plan Épic 13)."""

    __tablename__ = "competency_evidence"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_competency_id = Column(String(36), ForeignKey("user_competencies.id"), nullable=False)
    action = Column(SAEnum(EvidenceAction), nullable=False)
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # null = déclenché automatiquement par une règle
    note = Column(Text, nullable=True)
    grade_rank = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_competency = relationship("UserCompetency", back_populates="evidence")


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(PlanStatus), nullable=False, default=PlanStatus.draft)
    due_date = Column(DateTime, nullable=True)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    competencies = relationship("PlanCompetency", back_populates="plan", cascade="all, delete-orphan")


class PlanCompetency(Base):
    __tablename__ = "plan_competencies"
    __table_args__ = (
        UniqueConstraint("plan_id", "competency_id", name="uq_plan_competencies_plan_competency"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=False)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    plan = relationship("Plan", back_populates="competencies")
    competency = relationship("Competency")
