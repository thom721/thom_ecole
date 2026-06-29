# app/Schemas/SAuthorization.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PermissionResponseAll(BaseModel): #good
    permis: List[PermissionResponse]
    class Config:
        from_attributes = True
    class Config:
        from_attributes = True
    

class PermissionResponseShow(BaseModel):
    data: List[PermissionResponse]

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: str
    accessible_tabs: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True

class RoleResponseShow(BaseModel):
    data:List[RoleResponse]

class UserWithPermissions(BaseModel):
    id: str
    nom: str
    prenom: str
    permissions: List[str] = []
    
    class Config:
        from_attributes = True

class UserWithPermissionsAll(UserWithPermissions):
    data:UserWithPermissions

class UserWithRoles(BaseModel):
    id: str
    nom: str
    prenom: str
    roles: List[str] = []
    
    class Config:
        from_attributes = True

class AssignRoleRequest(BaseModel):
    user_id: str
    role: List[str]

class AssignPermissionRequest(BaseModel):
    role: Optional[str] = None
    user_id: Optional[str] = None
    permission: List[str]