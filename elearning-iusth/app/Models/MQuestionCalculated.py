from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class QuestionCalculatedDataset(Base):
    """Une variable de la formule portée par Question.question_text (ex.
    "{x}") et son jeu de valeurs candidates. Toutes les variables d'une même
    question doivent avoir des listes `values` de même longueur — un index
    est tiré au hasard et partagé entre variables à chaque tentative (voir
    RQuizAttempts.py::start_attempt), jamais recalculé après coup."""

    __tablename__ = "question_calculated_datasets"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    variable_name = Column(String(50), nullable=False)
    values = Column(JSON, nullable=False)  # list[float]

    question = relationship("Question", back_populates="calculated_datasets")
