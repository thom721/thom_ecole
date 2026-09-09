from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LiveSessionBase(BaseModel):
    title: str
    description: str | None = None
    is_visible: bool = True
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    join_window_minutes_before: int = 10


class LiveSessionCreate(LiveSessionBase):
    pass


class LiveSessionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_visible: bool | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    join_window_minutes_before: int | None = None


class LiveSessionOut(LiveSessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    room_name: str


class LiveSessionDetailOut(LiveSessionOut):
    is_joinable: bool
    not_joinable_reason: str | None = None


class LiveSessionJoinOut(BaseModel):
    jitsi_base_url: str
    room_name: str
    jwt: str


class LiveSessionAttendanceRowOut(BaseModel):
    student_id: str
    student_name: str
    first_joined_at: datetime
    last_left_at: datetime | None = None
    is_currently_in_session: bool
    join_count: int
