from datetime import datetime

from pydantic import BaseModel


class StaffMeetingCreate(BaseModel):
    title: str
    description: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    invitee_user_ids: list[str] = []


class StaffMeetingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None


class StaffMeetingOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    created_by: str
    is_creator: bool = False
    is_joinable: bool = True
    join_error: str | None = None


class EligibleUserOut(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    system_role: str


class StaffMeetingJoinOut(BaseModel):
    jitsi_base_url: str
    room_name: str
    jwt: str
