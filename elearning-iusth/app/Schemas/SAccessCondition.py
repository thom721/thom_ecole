from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.Models.MAccessCondition import AccessConditionType, AccessLogic
from app.Models.MCompletion import CompletionItemType


class AccessConditionCreate(BaseModel):
    condition_type: AccessConditionType
    logic: AccessLogic = AccessLogic.and_
    available_from: datetime | None = None
    available_until: datetime | None = None
    grade_item_id: str | None = None
    min_percent: Decimal | None = None
    required_item_type: CompletionItemType | None = None
    required_item_id: str | None = None
    group_id: str | None = None


class AccessConditionOut(AccessConditionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    item_type: CompletionItemType
    item_id: str


class AccessCheckOut(BaseModel):
    accessible: bool
    reasons: list[str] = []
