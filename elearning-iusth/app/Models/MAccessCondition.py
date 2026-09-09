import enum

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum as SAEnum

from app.database import Base, generate_uuid
from app.Models.MCompletion import CompletionItemType

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class AccessConditionType(str, enum.Enum):
    date = "date"
    grade = "grade"
    activity_completion = "activity_completion"
    group = "group"


class AccessLogic(str, enum.Enum):
    and_ = "and"
    or_ = "or"


class AccessCondition(Base):
    """Une ligne = une condition d'accès sur UNE activité précise
    (item_type/item_id, polymorphe comme ActivityCompletion — pas de FK
    possible vers 3+ tables différentes). `logic` est répété sur chaque
    ligne d'une même activité plutôt que stocké une fois ailleurs — évite
    un join, une seule requête suffit à tout récupérer et toutes les
    lignes d'une même activité sont censées porter la même valeur
    (garanti par la route de création, voir RAccessConditions.py)."""

    __tablename__ = "access_conditions"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_type = Column(SAEnum(CompletionItemType), nullable=False)
    item_id = Column(String(36), nullable=False)
    condition_type = Column(SAEnum(AccessConditionType), nullable=False)
    logic = Column(SAEnum(AccessLogic), nullable=False, default=AccessLogic.and_)

    # condition_type == date
    available_from = Column(DateTime, nullable=True)
    available_until = Column(DateTime, nullable=True)

    # condition_type == grade
    grade_item_id = Column(String(36), ForeignKey("grade_items.id"), nullable=True)
    min_percent = Column(Numeric(5, 2), nullable=True)

    # condition_type == activity_completion
    required_item_type = Column(SAEnum(CompletionItemType), nullable=True)
    required_item_id = Column(String(36), nullable=True)

    # condition_type == group
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=True)
