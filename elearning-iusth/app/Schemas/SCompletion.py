from datetime import datetime

from pydantic import BaseModel

from app.Models.MCompletion import CompletionItemType, CompletionMode


class CompletionConfigOut(BaseModel):
    item_type: CompletionItemType
    item_id: str
    mode: CompletionMode


class CompletionConfigUpdate(BaseModel):
    mode: CompletionMode


class CompletionItemOut(BaseModel):
    item_type: CompletionItemType
    item_id: str
    title: str
    is_complete: bool
    completed_at: datetime | None = None


class CompletionMineOut(BaseModel):
    course_id: str
    percent: float
    items: list[CompletionItemOut]


class CompletionReportRowOut(BaseModel):
    student_id: str
    student_name: str
    percent: float
    completed_count: int
    total_count: int
