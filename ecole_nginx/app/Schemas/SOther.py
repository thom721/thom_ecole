from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
# from pydantic import BaseModel, Field, validator, field_validator
from pydantic import BaseModel, computed_field,Field,EmailStr,validator,model_validator, field_validator
from typing import Optional, List
from datetime import datetime 
import re
import uuid 


# ============================================================================
# MODÈLES Pydantic - SCHEMAS
# ============================================================================

# ModelHasPermission Schemas
class ModelHasPermissionBase(BaseModel):
    permission_id: str = Field(..., max_length=36)
    model_type: str = Field(..., max_length=255)
    model_id: str = Field(..., max_length=36)
    
    @validator('permission_id', 'model_id')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('Doit être un UUID valide')
        return v

class ModelHasPermissionCreate(ModelHasPermissionBase):
    pass

class ModelHasPermissionResponse(ModelHasPermissionBase):
    class Config:
        from_attributes = True


# ModelHasRole Schemas
class ModelHasRoleBase(BaseModel):
    role_id: str = Field(..., max_length=36)
    model_type: str = Field(..., max_length=255)
    model_id: str = Field(..., max_length=36)
    
    @validator('role_id', 'model_id')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('Doit être un UUID valide')
        return v

class ModelHasRoleCreate(ModelHasRoleBase):
    pass

class ModelHasRoleResponse(ModelHasRoleBase):
    class Config:
        from_attributes = True


# PasswordResetToken Schemas
class PasswordResetTokenBase(BaseModel):
    email: str = Field(..., max_length=255)
    token: str = Field(..., max_length=255)

class PasswordResetTokenCreate(PasswordResetTokenBase):
    pass

class PasswordResetTokenResponse(PasswordResetTokenBase):
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# PersonalAccessToken Schemas
class PersonalAccessTokenBase(BaseModel):
    tokenable_type: str = Field(..., max_length=255)
    tokenable_id: str = Field(..., max_length=36)
    name: str = Field(..., max_length=255)
    abilities: Optional[str] = None
    
    @validator('tokenable_id')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('Doit être un UUID valide')
        return v

class PersonalAccessTokenCreate(PersonalAccessTokenBase):
    token: str = Field(..., max_length=64)

class PersonalAccessTokenUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    abilities: Optional[str] = None
    last_used_at: Optional[datetime] = None

class PersonalAccessTokenResponse(PersonalAccessTokenBase):
    id: str
    token: str
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# RoleHasPermission Schemas
class RoleHasPermissionBase(BaseModel):
    permission_id: str = Field(..., max_length=36)
    role_id: str = Field(..., max_length=36)
    
    @validator('permission_id', 'role_id')
    def validate_uuid(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError('Doit être un UUID valide')
        return v

class RoleHasPermissionCreate(RoleHasPermissionBase):
    pass

class RoleHasPermissionResponse(RoleHasPermissionBase):
    class Config:
        from_attributes = True


# Session Schemas
class SessionBase(BaseModel):
    user_id: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    payload: str
    last_activity: int
    
    @validator('ip_address')
    def validate_ip(cls, v):
        if v is None:
            return v
        # Validation basique d'IP (IPv4 ou IPv6)
        import re
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$'
        if not (re.match(ipv4_pattern, v) or re.match(ipv6_pattern, v)):
            raise ValueError('Adresse IP invalide')
        return v

class SessionCreate(SessionBase):
    id: str = Field(..., max_length=255)

class SessionUpdate(BaseModel):
    user_id: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    payload: Optional[str] = None
    last_activity: Optional[int] = None

class SessionResponse(SessionBase):
    id: str
    
    class Config:
        from_attributes = True





# Schemas Pydantic pour Permission et Role
class PermissionBase(BaseModel):
    name: str = Field(..., max_length=255)
    guard_name: str = Field(..., max_length=255)

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str = Field(..., max_length=255)
    guard_name: str = Field(..., max_length=255)

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schemas Pydantic pour Permission et Role
class PermissionBase(BaseModel):
    name: str = Field(..., max_length=255)
    guard_name: str = Field(..., max_length=255)

class PermissionCreate(PermissionBase):
    pass

class PermissionResponse(PermissionBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str = Field(..., max_length=255)
    guard_name: str = Field(..., max_length=255)

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============================================================================
# MODÈLES COMPLEXES AVEC RELATIONS
# ============================================================================

class RoleWithPermissions(RoleResponse):
    """Role avec ses permissions"""
    permissions: List[PermissionResponse] = []

class PermissionWithRoles(PermissionResponse):
    """Permission avec ses roles"""
    roles: List[RoleResponse] = []

class UserSessionInfo(BaseModel):
    """Information de session enrichie"""
    session_id: str
    user_id: Optional[str]
    ip_address: Optional[str]
    last_activity: datetime
    is_active: bool
    
    @validator('last_activity', pre=True)
    def convert_timestamp(cls, v):
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v



class ActiveRequest(BaseModel):
    id: str = Field(..., description="ID du professeur ou personnel")

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("ID doit être une chaîne")

        v = v.strip()

        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Format d'ID invalide (UUID attendu)")
        return v

 
    
# Pour changer le mot de passe
class ChangePasswordRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur")
    professeur_id: Optional[str] = Field(None, description="ID du professeur")
    personnel_id: Optional[str] = Field(None, description="ID du personnel")
    password: str = Field(..., min_length=8, description="Nouveau mot de passe")
    password_confirm: str = Field(..., min_length=8, description="Confirmation du mot de passe")
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'[0-9]', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return v
    
    @field_validator('password_confirm')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v

# Réponses
class SuccessResponse(BaseModel):
    success: str
    status: Optional[bool] = None

class updatePassword(BaseModel):
    current_password: str 
    password: str = Field(..., min_length=8, description="Nouveau mot de passe") 
    password_confirmation: str = Field(..., min_length=8, description="Confirmation du mot de passe")
 

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'[0-9]', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return v
    
    @field_validator('password_confirmation')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v