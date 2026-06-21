from typing import Optional
from pydantic import BaseModel, EmailStr

class AdminAuthRequest(BaseModel):
    email: EmailStr
    password: str

class PermissionCheckRequest(BaseModel):
    user_id: Optional[str] = None
    permission_name: str
    admin_data: Optional[AdminAuthRequest] = None

class AuthResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    authorization: Optional[bool] = None
    required_permission: Optional[str] = None
    require_admin_auth: Optional[bool] = None

class UserCredentialsRequest(BaseModel):
    email: EmailStr
    password: str
    permission_name: str

class UserAuthResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    permission: Optional[bool] = None
    errors: Optional[str] = None