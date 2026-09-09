import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid
from app.Models.MGroup import GroupMode

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class ChoiceResultsDisplay(str, enum.Enum):
    never = "never"
    after_answering = "after_answering"
    after_close = "after_close"
    always = "always"


class Choice(Base):
    """Sondage (calque mdl_choice) — s'attache à une Section comme Forum."""

    __tablename__ = "choices"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    allow_multiple = Column(Boolean, nullable=False, default=False)
    allow_update = Column(Boolean, nullable=False, default=False)
    limit_answers = Column(Boolean, nullable=False, default=False)
    results_display = Column(SAEnum(ChoiceResultsDisplay), nullable=False, default=ChoiceResultsDisplay.never)
    # True = comptes seuls ; False = les noms des répondants sont exposés
    # dans les résultats quand ceux-ci sont par ailleurs visibles.
    anonymous_results = Column(Boolean, nullable=False, default=True)
    # Expose côté étudiant une option explicite "aucune réponse" pour
    # annuler un vote — n'a d'effet que si allow_update est vrai.
    show_unanswered = Column(Boolean, nullable=False, default=False)
    opens_at = Column(DateTime, nullable=True)
    closes_at = Column(DateTime, nullable=True)
    group_mode = Column(SAEnum(GroupMode), nullable=False, default=GroupMode.no_groups)
    grouping_id = Column(String(36), ForeignKey("groupings.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="choices")
    options = relationship("ChoiceOption", back_populates="choice", cascade="all, delete-orphan", order_by="ChoiceOption.sort_order")
    answers = relationship("ChoiceAnswer", back_populates="choice", cascade="all, delete-orphan")


class ChoiceOption(Base):
    __tablename__ = "choice_options"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    choice_id = Column(String(36), ForeignKey("choices.id"), nullable=False)
    option_text = Column(String(500), nullable=False)
    # null = illimité — utilisée seulement si Choice.limit_answers est vrai.
    max_answers = Column(Integer, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    choice = relationship("Choice", back_populates="options")


class ChoiceAnswer(Base):
    __tablename__ = "choice_answers"
    __table_args__ = (
        UniqueConstraint("choice_id", "option_id", "user_id", name="uq_choice_answers_choice_option_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    choice_id = Column(String(36), ForeignKey("choices.id"), nullable=False)
    option_id = Column(String(36), ForeignKey("choice_options.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    choice = relationship("Choice", back_populates="answers")
    option = relationship("ChoiceOption")
