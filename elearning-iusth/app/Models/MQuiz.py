import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Text, ForeignKey,
    Enum as SAEnum, Numeric, UniqueConstraint, JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid
from app.Models.MQuestion import QuestionType

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class QuizAttemptStatus(str, enum.Enum):
    in_progress = "in_progress"
    submitted = "submitted"
    pending_manual_grading = "pending_manual_grading"
    graded = "graded"


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    time_limit_minutes = Column(Integer, nullable=True)  # null = pas de limite
    max_attempts = Column(Integer, nullable=True)  # null = illimité
    shuffle_questions = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=True)
    # Fenêtre d'ouverture du quiz (Phase 4, pour le calendrier) — distincte
    # de time_limit_minutes qui est la durée d'UNE tentative, pas la
    # période pendant laquelle le quiz est accessible.
    opens_at = Column(DateTime, nullable=True)
    closes_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="quizzes")
    quiz_questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.sort_order")
    draw_rules = relationship("QuizDrawRule", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizDrawRule.sort_order")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
    grade_item = relationship("GradeItem", back_populates="quiz", uselist=False, cascade="all, delete-orphan")

    @property
    def course_id(self) -> str:
        """Pratique pour le frontend (SQuiz.QuizOut.course_id) — évite un
        aller-retour supplémentaire pour retrouver le cours d'un quiz."""
        return self.section.course_id


class QuizQuestion(Base):
    """Entrée fixe : cette question précise apparaît dans le quiz."""

    __tablename__ = "quiz_questions"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    points = Column(Numeric(6, 2), nullable=True)  # null = points par défaut de la question
    sort_order = Column(Integer, nullable=False, default=0)

    quiz = relationship("Quiz", back_populates="quiz_questions")
    question = relationship("Question")


class QuizDrawRule(Base):
    """Règle de tirage aléatoire : N questions de la catégorie X."""

    __tablename__ = "quiz_draw_rules"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("question_categories.id"), nullable=False)
    question_type = Column(SAEnum(QuestionType), nullable=True)  # null = tous types
    count = Column(Integer, nullable=False)
    points = Column(Numeric(6, 2), nullable=True)  # null = points par défaut de chaque question tirée
    sort_order = Column(Integer, nullable=False, default=0)

    quiz = relationship("Quiz", back_populates="draw_rules")
    category = relationship("QuestionCategory")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False)
    student_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(QuizAttemptStatus), nullable=False, default=QuizAttemptStatus.in_progress)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    deadline_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    score = Column(Numeric(6, 2), nullable=True)
    max_score = Column(Numeric(6, 2), nullable=True)
    graded_at = Column(DateTime, nullable=True)

    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User", foreign_keys=[student_id])
    responses = relationship("QuizResponse", back_populates="attempt", cascade="all, delete-orphan", order_by="QuizResponse.sort_order")


class QuizResponse(Base):
    """Fusion instantané + réponse : une ligne par question dès le début de
    la tentative (voir plan Phase 2 pour la justification de ne pas
    séparer en deux tables)."""

    __tablename__ = "quiz_responses"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_quiz_responses_attempt_question"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    points = Column(Numeric(6, 2), nullable=False)

    answer_data = Column(JSON, nullable=True)
    # calculated uniquement : valeurs de variables tirées au hasard et
    # figées au démarrage de la tentative (voir start_attempt) — jamais
    # écrit par l'étudiant (contrairement à answer_data, remplacé en
    # intégralité à chaque sauvegarde de réponse), jamais recalculé après
    # coup à la correction.
    resolved_data = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    points_awarded = Column(Numeric(6, 2), nullable=True)
    feedback = Column(Text, nullable=True)
    graded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, nullable=True)

    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("Question")
