import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Text, ForeignKey,
    Enum as SAEnum, Numeric, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS_BASE = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class SubmissionType(str, enum.Enum):
    file = "file"
    text = "text"
    both = "both"


class SubmissionStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    graded = "graded"


class Assignment(Base):
    __tablename__ = "assignments"
    __table_args__ = _TABLE_ARGS_BASE

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    allow_late_submissions = Column(Boolean, nullable=False, default=True)
    submission_type = Column(SAEnum(SubmissionType), nullable=False, default=SubmissionType.both)
    max_points = Column(Numeric(6, 2), nullable=False, default=100)
    is_visible = Column(Boolean, nullable=False, default=True)
    # Si renseigné, la notation utilise les niveaux de cette échelle au lieu
    # de max_points en points libres (voir plan Épic 8) — Submission.grade
    # porte alors le rang du niveau choisi (1..N), pas des points bruts.
    scale_id = Column(String(36), ForeignKey("scales.id"), nullable=True)
    # Devoir noté par groupe (voir plan Épic 24) : la notation se fait une
    # fois par Group (groups.id), puis est recopiée sur chaque membre —
    # Submission reste 1 ligne par étudiant (student_id porte toujours la
    # clé de calcul du carnet de notes), group_id n'est là que pour la
    # traçabilité/l'affichage groupé côté notation.
    group_mode = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    grade_item = relationship("GradeItem", back_populates="assignment", uselist=False, cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("assignment_id", "student_id", name="uq_submissions_assignment_student"),
        _TABLE_ARGS_BASE,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    assignment_id = Column(String(36), ForeignKey("assignments.id"), nullable=False)
    student_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    # Renseigné uniquement quand cette ligne provient d'une notation de
    # groupe (Assignment.group_mode) — voir RSubmissions.py::grade_group.
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=True)
    submitted_text = Column(Text, nullable=True)
    file_path = Column(String(1000), nullable=True)
    status = Column(SAEnum(SubmissionStatus), nullable=False, default=SubmissionStatus.draft)
    submitted_at = Column(DateTime, nullable=True)

    grade = Column(Numeric(6, 2), nullable=True)
    feedback = Column(Text, nullable=True)
    graded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime, nullable=True)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", foreign_keys=[student_id])
