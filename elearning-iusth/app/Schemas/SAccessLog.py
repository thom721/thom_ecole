from datetime import datetime

from pydantic import BaseModel

from app.Models.MAccessLog import AccessItemType


class AccessLogSummaryOut(BaseModel):
    item_type: AccessItemType
    item_id: str | None = None
    title: str
    view_count: int
    unique_student_count: int
    last_accessed_at: datetime


class AccessLogStudentOut(BaseModel):
    student_id: str
    student_name: str
    total_views: int
    last_accessed_at: datetime
