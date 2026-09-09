import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SAEnum, Numeric
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class QuestionType(str, enum.Enum):
    multiple_choice = "multiple_choice"
    true_false = "true_false"
    short_answer = "short_answer"
    essay = "essay"
    matching = "matching"
    # Ajoutés en épic "Types de question supplémentaires" (calque des vrais
    # qtype_* installés sur moodle-iusth, confirmés via mdl_config_plugins).
    numerical = "numerical"
    calculated = "calculated"
    multianswer = "multianswer"
    ordering = "ordering"
    drag_and_drop = "drag_and_drop"


class QuestionCategory(Base):
    __tablename__ = "question_categories"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    name = Column(String(200), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    questions = relationship("Question", back_populates="category")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("question_categories.id"), nullable=True)
    question_type = Column(SAEnum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    default_points = Column(Numeric(6, 2), nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    # calculated uniquement : question_text reste le texte affiché (avec
    # placeholders "{x}" substitués pour affichage — voir _rendered_text),
    # calculated_formula est l'expression arithmétique évaluée pour la
    # correction (ex. "{x}+{y}"), distincte comme dans le vrai Moodle
    # (qtype_calculated sépare aussi texte affiché et formule de réponse).
    calculated_formula = Column(Text, nullable=True)
    calculated_tolerance = Column(Numeric(10, 4), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    category = relationship("QuestionCategory", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.sort_order")
    accepted_answers = relationship("QuestionAcceptedAnswer", back_populates="question", cascade="all, delete-orphan")
    calculated_datasets = relationship("QuestionCalculatedDataset", back_populates="question", cascade="all, delete-orphan")
    cloze_parts = relationship("QuestionClozePart", back_populates="question", cascade="all, delete-orphan", order_by="QuestionClozePart.position")


class QuestionOption(Base):
    """Couvre QCM, vrai/faux et appariement uniformément (voir
    Resource/ResourceFile pour le même principe une-question-N-lignes)."""

    __tablename__ = "question_options"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    match_text = Column(Text, nullable=True)  # matching uniquement : réponse appariée
    is_correct = Column(Boolean, nullable=False, default=False)  # MCQ/true_false uniquement
    sort_order = Column(Integer, nullable=False, default=0)

    question = relationship("Question", back_populates="options")


class QuestionAcceptedAnswer(Base):
    __tablename__ = "question_accepted_answers"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    answer_text = Column(String(500), nullable=False)
    # numerical uniquement : tolérance ± appliquée à cette réponse acceptée
    # (short_answer laisse cette colonne nulle — comparaison textuelle exacte).
    tolerance = Column(Numeric(10, 4), nullable=True)

    question = relationship("Question", back_populates="accepted_answers")
