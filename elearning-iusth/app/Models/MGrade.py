import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SAEnum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class GradeItemKind(str, enum.Enum):
    assignment = "assignment"
    quiz = "quiz"
    lesson = "lesson"
    manual = "manual"
    # Ajoutés en Épic 10 — un atelier produit DEUX GradeItem distincts
    # partageant le même workshop_id (voir MWorkshop.py / plan Épic 10).
    workshop_submission = "workshop_submission"
    workshop_grading = "workshop_grading"
    # Ajouté en Épic 18, même patron que lesson_id (un seul GradeItem par
    # vidéo, tentative unique donc max_points canonique).
    interactive_video = "interactive_video"


class GradeCategory(Base):
    __tablename__ = "grade_categories"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    name = Column(String(200), nullable=False)
    weight_percent = Column(Numeric(5, 2), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    items = relationship("GradeItem", back_populates="category")


class GradeItem(Base):
    """`course_id` stocké directement (pas dérivé via une section) car les
    items manuels n'ont pas de section. `title`/`max_points` ne servent que
    pour kind=manual — pour assignment/quiz, ces valeurs sont lues en
    direct via la relation pour ne jamais devenir périmées."""

    __tablename__ = "grade_items"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    grade_category_id = Column(String(36), ForeignKey("grade_categories.id"), nullable=True)
    assignment_id = Column(String(36), ForeignKey("assignments.id"), unique=True, nullable=True)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), unique=True, nullable=True)
    lesson_id = Column(String(36), ForeignKey("lessons.id"), unique=True, nullable=True)
    # PAS unique — un atelier a 2 GradeItem (submission + grading)
    # discriminés par `kind`, contrairement à assignment/quiz/lesson.
    workshop_id = Column(String(36), ForeignKey("workshops.id"), nullable=True)
    interactive_video_id = Column(String(36), ForeignKey("interactive_videos.id"), unique=True, nullable=True)
    kind = Column(SAEnum(GradeItemKind), nullable=False)
    title = Column(String(255), nullable=True)  # manual uniquement
    max_points = Column(Numeric(6, 2), nullable=True)  # manual uniquement
    # manual uniquement — si renseigné, ManualGrade.points porte le rang du
    # niveau choisi (1..N) au lieu de points libres (voir plan Épic 8).
    scale_id = Column(String(36), ForeignKey("scales.id"), nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    category = relationship("GradeCategory", back_populates="items")
    assignment = relationship("Assignment", back_populates="grade_item")
    quiz = relationship("Quiz", back_populates="grade_item")
    lesson = relationship("Lesson", back_populates="grade_item")
    interactive_video = relationship("InteractiveVideo", back_populates="grade_item")
    manual_grades = relationship("ManualGrade", back_populates="grade_item", cascade="all, delete-orphan")


class ManualGrade(Base):
    """Équivalent de Submission sans contenu soumis : uniquement une note
    saisie par le professeur. Créé paresseusement (upsert) à la première
    note, pas de pré-création côté étudiant."""

    __tablename__ = "manual_grades"
    __table_args__ = (
        UniqueConstraint("grade_item_id", "student_id", name="uq_manual_grades_item_student"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    grade_item_id = Column(String(36), ForeignKey("grade_items.id"), nullable=False)
    student_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    points = Column(Numeric(6, 2), nullable=True)
    feedback = Column(Text, nullable=True)
    graded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime, nullable=True)

    grade_item = relationship("GradeItem", back_populates="manual_grades")
    student = relationship("User", foreign_keys=[student_id])
