import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class CompletionItemType(str, enum.Enum):
    resource = "resource"
    assignment = "assignment"
    quiz = "quiz"
    # Ajoutés en Épic 7 — élargissement manuel de l'ENUM MySQL requis dans
    # la migration (non détecté par l'autogenerate, même limitation que
    # QuestionType en Épic 1).
    forum = "forum"
    choice = "choice"
    # Ajouté en Épic 9, même technique.
    lesson = "lesson"
    # Ajouté en Épic 10, même technique.
    workshop = "workshop"
    # Ajouté en Épic 17, même technique.
    live_session = "live_session"
    # Ajouté en Épic 18, même technique.
    interactive_video = "interactive_video"


class CompletionMode(str, enum.Enum):
    none = "none"
    manual = "manual"
    automatic = "automatic"


class ActivityCompletion(Base):
    """`item_id` sans contrainte FK — ne peut pas cibler 3 tables
    différentes avec une seule FK. Une ligne orpheline (item supprimé) est
    inoffensive : le pourcentage se calcule contre les items ACTUELLEMENT
    visibles, jamais contre l'historique (voir plan Phase 5)."""

    __tablename__ = "activity_completions"
    __table_args__ = (
        UniqueConstraint("student_id", "item_type", "item_id", name="uq_activity_completions_student_item"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    item_type = Column(SAEnum(CompletionItemType), nullable=False)
    item_id = Column(String(36), nullable=False)
    completed_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class ActivityCompletionConfig(Base):
    """Mode d'achèvement configuré pour UNE activité précise (pas par
    type) — absence de ligne = comportement par défaut du type, voir
    Helper/completion_config.py::get_completion_mode (rétrocompatibilité
    Phase 5 obligatoire, voir plan Épic 7)."""

    __tablename__ = "activity_completion_configs"
    __table_args__ = (
        UniqueConstraint("item_type", "item_id", name="uq_activity_completion_configs_item"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_type = Column(SAEnum(CompletionItemType), nullable=False)
    item_id = Column(String(36), nullable=False)
    mode = Column(SAEnum(CompletionMode), nullable=False, default=CompletionMode.none)
