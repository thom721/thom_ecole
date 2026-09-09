from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MNotification import NotificationKind


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    kind: NotificationKind
    title: str
    body: str | None = None
    link_url: str | None = None
    is_read: bool
    created_at: datetime


class UnreadCountOut(BaseModel):
    count: int
