import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Text, ForeignKey,
    Enum as SAEnum, Numeric,
)
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class LessonPageType(str, enum.Enum):
    content = "content"
    true_false = "true_false"
    multiple_choice = "multiple_choice"
    short_answer = "short_answer"
    numerical = "numerical"
    essay = "essay"


class LessonJumpType(str, enum.Enum):
    next_page = "next_page"
    previous_page = "previous_page"
    specific_page = "specific_page"
    end_of_lesson = "end_of_lesson"


class LessonAttemptStatus(str, enum.Enum):
    in_progress = "in_progress"
    pending_manual_grading = "pending_manual_grading"
    completed = "completed"


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    password = Column(String(255), nullable=True)  # null = aucun mot de passe requis
    max_attempts_per_question = Column(Integer, nullable=True)  # null = illimité
    time_limit_minutes = Column(Integer, nullable=True)  # null = pas de limite
    allow_retake = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="lessons")
    pages = relationship("LessonPage", back_populates="lesson", cascade="all, delete-orphan", order_by="LessonPage.sort_order")
    attempts = relationship("LessonAttempt", back_populates="lesson", cascade="all, delete-orphan")
    grade_item = relationship("GradeItem", back_populates="lesson", uselist=False, cascade="all, delete-orphan")

    @property
    def course_id(self) -> str:
        return self.section.course_id

    @property
    def has_password(self) -> bool:
        return self.password is not None


class LessonPage(Base):
    __tablename__ = "lesson_pages"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    lesson_id = Column(String(36), ForeignKey("lessons.id"), nullable=False)
    page_type = Column(SAEnum(LessonPageType), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    # Ignoré pour `content` ; sert de note max pour `essay` en attente de
    # correction manuelle, ou de points gagnés si correct pour les autres.
    points = Column(Numeric(6, 2), nullable=False, default=1)
    sort_order = Column(Integer, nullable=False, default=0)

    lesson = relationship("Lesson", back_populates="pages")
    answers = relationship(
        "LessonAnswer", back_populates="page", cascade="all, delete-orphan",
        order_by="LessonAnswer.sort_order", foreign_keys="LessonAnswer.page_id",
    )


class LessonAnswer(Base):
    """Libellé de bouton pour `content` ; texte d'option pour
    `true_false`/`multiple_choice` ; valeur/texte candidat pour
    `short_answer`/`numerical` ; nullable pour `essay` (un seul saut par
    défaut, pas de choix). Voir plan Épic 9 : pour `short_answer`/
    `numerical`, la DERNIÈRE réponse (tri par sort_order) sert de réponse
    par défaut/générique si aucune ne correspond — comportement réel de
    Moodle, pas une invention."""

    __tablename__ = "lesson_answers"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    page_id = Column(String(36), ForeignKey("lesson_pages.id"), nullable=False)
    answer_text = Column(String(1000), nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)  # ignoré pour content/essay
    tolerance = Column(Numeric(10, 4), nullable=True)  # numerical uniquement
    jump_type = Column(SAEnum(LessonJumpType), nullable=False, default=LessonJumpType.next_page)
    jump_to_page_id = Column(String(36), ForeignKey("lesson_pages.id"), nullable=True)  # si jump_type == specific_page
    sort_order = Column(Integer, nullable=False, default=0)

    page = relationship("LessonPage", back_populates="answers", foreign_keys=[page_id])


class LessonAttempt(Base):
    __tablename__ = "lesson_attempts"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    lesson_id = Column(String(36), ForeignKey("lessons.id"), nullable=False)
    student_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(LessonAttemptStatus), nullable=False, default=LessonAttemptStatus.in_progress)
    # Page à afficher au prochain chargement — mise à jour à chaque
    # réponse, mise à null une fois end_of_lesson atteint (voir plan Épic 9).
    current_page_id = Column(String(36), ForeignKey("lesson_pages.id"), nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    deadline_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Numeric(6, 2), nullable=True)
    max_score = Column(Numeric(6, 2), nullable=True)
    graded_at = Column(DateTime, nullable=True)

    lesson = relationship("Lesson", back_populates="attempts")
    page_attempts = relationship("LessonPageAttempt", back_populates="attempt", cascade="all, delete-orphan")


class LessonPageAttempt(Base):
    """Pas de contrainte unique — plusieurs essais par page autorisés à
    l'intérieur d'une même tentative (plafonnés par
    Lesson.max_attempts_per_question, vérifié en route)."""

    __tablename__ = "lesson_page_attempts"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("lesson_attempts.id"), nullable=False)
    page_id = Column(String(36), ForeignKey("lesson_pages.id"), nullable=False)
    try_number = Column(Integer, nullable=False, default=1)
    answer_id = Column(String(36), ForeignKey("lesson_answers.id"), nullable=True)  # null seulement pour essay
    answer_text = Column(Text, nullable=True)  # texte libre brut (short_answer/numerical/essay)
    is_correct = Column(Boolean, nullable=True)  # non applicable à content/essay
    points_awarded = Column(Numeric(6, 2), nullable=True)  # reste null pour essay tant que non corrigé
    feedback = Column(Text, nullable=True)
    graded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    attempt = relationship("LessonAttempt", back_populates="page_attempts")
    page = relationship("LessonPage", foreign_keys=[page_id])
    answer = relationship("LessonAnswer", foreign_keys=[answer_id])
