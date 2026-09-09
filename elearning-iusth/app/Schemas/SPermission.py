from pydantic import BaseModel, ConfigDict


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str | None = None


class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    permission_names: list[str] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permission_names: list[str] | None = None


class RoleOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    permission_names: list[str] = []


class UserRoleCreate(BaseModel):
    role_id: str


class UserRoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    role_id: str
    role_name: str
