import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Text, ForeignKey,
    Enum as SAEnum, Numeric, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class WorkshopPhase(str, enum.Enum):
    setup = "setup"
    submission = "submission"
    assessment = "assessment"
    evaluation = "evaluation"
    closed = "closed"


class WorkshopStrategy(str, enum.Enum):
    accumulative = "accumulative"
    comments = "comments"
    numerrors = "numerrors"
    rubric = "rubric"


class Workshop(Base):
    __tablename__ = "workshops"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    phase = Column(SAEnum(WorkshopPhase), nullable=False, default=WorkshopPhase.setup)
    grade = Column(Numeric(6, 2), nullable=False, default=80)  # note max de soumission
    gradinggrade = Column(Numeric(6, 2), nullable=False, default=20)  # note max de qualité d'évaluation
    strategy = Column(SAEnum(WorkshopStrategy), nullable=False, default=WorkshopStrategy.accumulative)
    use_peer_assessment = Column(Boolean, nullable=False, default=True)
    use_self_assessment = Column(Boolean, nullable=False, default=False)
    submission_start = Column(DateTime, nullable=True)
    submission_end = Column(DateTime, nullable=True)
    assessment_start = Column(DateTime, nullable=True)
    assessment_end = Column(DateTime, nullable=True)
    comparison = Column(Integer, nullable=False, default=5)  # sévérité eval_best
    conclusion = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="workshops")
    dimensions = relationship("WorkshopDimension", back_populates="workshop", cascade="all, delete-orphan", order_by="WorkshopDimension.sort_order")
    numerrors_map = relationship("WorkshopNumerrorsMap", back_populates="workshop", cascade="all, delete-orphan", order_by="WorkshopNumerrorsMap.error_count")
    submissions = relationship("WorkshopSubmission", back_populates="workshop", cascade="all, delete-orphan")

    @property
    def course_id(self) -> str:
        return self.section.course_id


class WorkshopDimension(Base):
    """Une seule table pour accumulative/numerrors/comments (formes assez
    proches) — `grade` (points max) et `weight` ne servent qu'à
    accumulative/numerrors ; `label_no`/`label_yes` ne servent qu'à
    numerrors. `levels` ne sert qu'à rubric (voir plan Épic 10)."""

    __tablename__ = "workshop_dimensions"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workshop_id = Column(String(36), ForeignKey("workshops.id"), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=False)
    grade = Column(Numeric(6, 2), nullable=True)  # accumulative uniquement (points max)
    weight = Column(Integer, nullable=False, default=1)  # accumulative/numerrors
    label_no = Column(String(50), nullable=True)  # numerrors uniquement
    label_yes = Column(String(50), nullable=True)  # numerrors uniquement

    workshop = relationship("Workshop", back_populates="dimensions")
    levels = relationship("WorkshopRubricLevel", back_populates="dimension", cascade="all, delete-orphan", order_by="WorkshopRubricLevel.sort_order")


class WorkshopRubricLevel(Base):
    __tablename__ = "workshop_rubric_levels"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dimension_id = Column(String(36), ForeignKey("workshop_dimensions.id"), nullable=False)
    grade = Column(Numeric(6, 2), nullable=False)
    definition = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    dimension = relationship("WorkshopDimension", back_populates="levels")


class WorkshopNumerrorsMap(Base):
    """Table de correspondance nombre d'erreurs -> % propre au cours (voir
    `errors_to_grade()` du vrai Moodle) — 0 erreur vaut toujours 100%,
    jamais stocké ici (comportement fixe, pas une ligne de plus)."""

    __tablename__ = "workshop_numerrors_map"
    __table_args__ = (
        UniqueConstraint("workshop_id", "error_count", name="uq_workshop_numerrors_map_workshop_count"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workshop_id = Column(String(36), ForeignKey("workshops.id"), nullable=False)
    error_count = Column(Integer, nullable=False)
    grade_percent = Column(Numeric(6, 2), nullable=False)

    workshop = relationship("Workshop", back_populates="numerrors_map")


class WorkshopSubmission(Base):
    __tablename__ = "workshop_submissions"
    __table_args__ = (
        UniqueConstraint("workshop_id", "author_id", name="uq_workshop_submissions_workshop_author"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workshop_id = Column(String(36), ForeignKey("workshops.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(1000), nullable=True)
    grade_override = Column(Numeric(6, 2), nullable=True)
    feedback_author = Column(Text, nullable=True)
    graded_at = Column(DateTime, nullable=True)
    published = Column(Boolean, nullable=False, default=False)
    late = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workshop = relationship("Workshop", back_populates="submissions")
    assessments = relationship("WorkshopAssessment", back_populates="submission", cascade="all, delete-orphan")


class WorkshopAssessment(Base):
    __tablename__ = "workshop_assessments"
    __table_args__ = (
        UniqueConstraint("submission_id", "reviewer_id", name="uq_workshop_assessments_submission_reviewer"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(String(36), ForeignKey("workshop_submissions.id"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    weight = Column(Integer, nullable=False, default=1)
    gradinggrade_override = Column(Numeric(6, 2), nullable=True)
    feedback_author = Column(Text, nullable=True)
    feedback_reviewer = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    submission = relationship("WorkshopSubmission", back_populates="assessments")
    grades = relationship("WorkshopGrade", back_populates="assessment", cascade="all, delete-orphan")


class WorkshopGrade(Base):
    __tablename__ = "workshop_grades"
    __table_args__ = (
        UniqueConstraint("assessment_id", "dimension_id", name="uq_workshop_grades_assessment_dimension"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assessment_id = Column(String(36), ForeignKey("workshop_assessments.id"), nullable=False)
    dimension_id = Column(String(36), ForeignKey("workshop_dimensions.id"), nullable=False)
    grade = Column(Numeric(6, 2), nullable=True)
    peer_comment = Column(Text, nullable=True)

    assessment = relationship("WorkshopAssessment", back_populates="grades")
    dimension = relationship("WorkshopDimension")
