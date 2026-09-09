from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.Models.MBadge import BadgeStatus, BadgeCriteriaType, BadgeCriteriaLogic
from app.Models.MCompletion import CompletionItemType


class BadgeBase(BaseModel):
    name: str
    description: str | None = None
    image_emoji: str | None = "🏅"
    status: BadgeStatus = BadgeStatus.draft
    criteria_logic: BadgeCriteriaLogic = BadgeCriteriaLogic.and_
    expire_days: int | None = None


class BadgeCreate(BadgeBase):
    pass


class BadgeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    image_emoji: str | None = None
    status: BadgeStatus | None = None
    criteria_logic: BadgeCriteriaLogic | None = None
    expire_days: int | None = None


class BadgeOut(BadgeBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str | None = None


class BadgeCriterionIn(BaseModel):
    criteria_type: BadgeCriteriaType
    required_item_type: CompletionItemType | None = None
    required_item_id: str | None = None
    min_percent: Decimal | None = None
    cohort_id: str | None = None


class BadgeCriterionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    criteria_type: BadgeCriteriaType
    required_item_type: CompletionItemType | None = None
    required_item_id: str | None = None
    min_percent: Decimal | None = None
    cohort_id: str | None = None


class BadgeCriteriaUpdate(BaseModel):
    criteria: list[BadgeCriterionIn]


class BadgeDetailOut(BadgeOut):
    criteria: list[BadgeCriterionOut] = []


class BadgeAwardIn(BaseModel):
    user_id: str


class BadgeIssuedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    badge_id: str
    user_id: str
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    awarded_manually: bool


class BadgeProgressCriterionOut(BaseModel):
    criteria_type: BadgeCriteriaType
    met: bool


class BadgeMineOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    image_emoji: str | None = None
    course_id: str | None = None
    is_earned: bool
    issued_at: datetime | None = None
    criteria_progress: list[BadgeProgressCriterionOut] = []
