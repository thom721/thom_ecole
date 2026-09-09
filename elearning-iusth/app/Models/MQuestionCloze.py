from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Numeric, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid
from app.Models.MQuestion import QuestionType

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

# Sous-types valides pour une sous-question cloze — restreint en
# application (pas de contrainte DB), pas de sens à embarquer un essai ou
# un autre multianswer dans un multianswer.
CLOZE_SUB_TYPES = (QuestionType.multiple_choice, QuestionType.short_answer, QuestionType.numerical)


class QuestionClozePart(Base):
    """Une sous-question embarquée dans le texte d'une question
    `multianswer` (calque qtype_multianswer / Cloze). `correct_answers` a
    une forme différente selon `sub_type` :
    - multiple_choice : {"options": [str, ...], "correct_index": int}
    - short_answer     : {"accepted": [str, ...]}
    - numerical        : {"value": float, "tolerance": float}
    """

    __tablename__ = "question_cloze_parts"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    position = Column(Integer, nullable=False, default=0)
    sub_type = Column(SAEnum(QuestionType), nullable=False)
    correct_answers = Column(JSON, nullable=False)
    points = Column(Numeric(6, 2), nullable=False, default=1)

    question = relationship("Question", back_populates="cloze_parts")
