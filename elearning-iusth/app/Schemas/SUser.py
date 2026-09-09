from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from app.Models.MUser import SystemRole


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str
    system_role: SystemRole = SystemRole.student


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    system_role: SystemRole | None = None
    is_active: bool | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    system_role: SystemRole
    is_active: bool
    avatar_path: str | None = None
    must_change_password: bool
    created_at: datetime
