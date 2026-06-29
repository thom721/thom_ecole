# app/models/system.py
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, JSON, ForeignKey, TIMESTAMP,Index
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
from app.database import Base
import uuid
from app.Models.observable import ObservableMixin

def generate_uuid():
    return str(uuid.uuid4())

# ============= MODELS SYSTÈME =============
   

class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False)
    guard_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    # models = relationship("ModelHasPermission", back_populates="permission")
    # roles = relationship("RoleHasPermission", back_populates="permission")

    user = relationship(
        "User",
        secondary="model_has_permissions",
        primaryjoin="Permission.id == model_has_permissions.c.permission_id",
        secondaryjoin="User.id == model_has_permissions.c.model_id",
        back_populates="permissions",
        lazy="selectin"
    )
    
    roles = relationship(
        "Role",
        secondary="role_has_permissions",
        primaryjoin="Permission.id == role_has_permissions.c.permission_id",
        secondaryjoin="Role.id == role_has_permissions.c.role_id",
        back_populates="permissions",
        lazy="selectin"
    )


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, nullable=False)
    guard_name = Column(String(255), nullable=False)
    accessible_tabs = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    # models = relationship("ModelHasRole", back_populates="role")
    # permissions = relationship("RoleHasPermission", back_populates="role")

        # Relations
    user = relationship(
        "User",
        secondary="model_has_roles",
        primaryjoin="Role.id == model_has_roles.c.role_id",
        secondaryjoin="User.id == model_has_roles.c.model_id",
        back_populates="roles",
        lazy="selectin"
    )
    
    permissions = relationship(
        "Permission",
        secondary="role_has_permissions",
        primaryjoin="Role.id == role_has_permissions.c.role_id",
        secondaryjoin="Permission.id == role_has_permissions.c.permission_id",
        back_populates="roles",
        lazy="selectin"
    )

class Log(Base):
    __tablename__ = "logs"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    action = Column(String(255), nullable=False)
    user_id = Column(CHAR(36), nullable=False)
    authorization_id = Column(String(255))
    model_type = Column(String(255), nullable=False)
    model_id = Column(CHAR(36), nullable=False)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    paiement_key = Column(String(255))
    reason = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    admin = relationship(
        "User",
        primaryjoin="User.id == foreign(Log.authorization_id)",
        viewonly=True
    )
    user = relationship(
        "User",
        primaryjoin="User.id == foreign(Log.user_id)",
        viewonly=True
    )

    # ==================== 2. CONTEXTE POUR STOCKER LES INFOS ====================
    from contextvars import ContextVar
    from typing import Optional

    def __repr__(self):
            return f"<Log(action={self.action}, user_id={self.user_id}, model={self.model_type})>"


    #relationship("User", back_populates="log_actives")
    # admin = relationship("User", back_populates="log_actives")

class LogActive(Base):
    __tablename__ = "log_actives"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    last_key = Column(String(255))
    new_key = Column(String(255))
    exprired_at = Column(String(255), nullable=False)
    f_key = Column(String(255), nullable=True)
    f_day = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="log_actives")

class ClientInfo(Base):
    __tablename__ = "client_infos"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }   
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    client_mac = Column(String(255), nullable=False)
    client_name = Column(String(255), nullable=False)
    authorisation = Column(Boolean, nullable=False, default=False)
    certi_key = Column(Text)
    ss_certi = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HeartAuto(Base):
    __tablename__ = "heart_autos"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    caution = Column(String(255), default="Dont manipulate this row")
    descript = Column(String(255), nullable=False)
    certi_key = Column(Text)
    public_key = Column(Text)
    private_key = Column(Text)
    config_wireguard = Column(Text)
    vpn_ip = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="heart_autos")

class DirectConfig(Base):
    __tablename__ = "direct_configs"
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    value = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    ligne1 = Column(String(255), nullable=False)
    ligne2 = Column(String(255))
    adresse = Column(String(255), nullable=False)
    logo_image_path = Column(String(2040), nullable=False)

    slogan = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    info_de_fondation = Column(String(255), nullable=True)

    logo_image_base64 = Column(LONGTEXT)
    school_url = Column(String(255))
    # Si True : un paiement pour l'année N est refusé tant que tous les
    # versements de l'année N-1 ne sont pas soldés.
    is_receive_arriere = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Personnel(Base):
    __tablename__ = "personnels"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    sexe = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telephone = Column(String(255), nullable=False)
    adresse = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship(
        "User",
        primaryjoin="and_(Personnel.id==foreign(User.userable_id), User.userable_type=='App\\\\Models\\\\Personnel')",
        uselist=False,
        viewonly=True  # <-- important, pour éviter conflit de direction
    )

# Base = declarative_base()

# ============================================================================
# MODÈLES SQLAlchemy
# ============================================================================

class ModelHasPermission(Base):
    __tablename__ = "model_has_permissions"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    permission_id = Column(String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    model_type = Column(String(255), primary_key=True, nullable=False)
    model_id = Column(String(36),ForeignKey('users.id'), primary_key=True, nullable=False)
    
    # __table_args__ = (
    #     Index('model_has_permissions_model_id_model_type_index', 'model_id', 'model_type'),
    # )


class ModelHasRole(Base):
    __tablename__ = "model_has_roles"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    model_type = Column(String(255), primary_key=True, nullable=False)
    model_id = Column(String(36),ForeignKey('users.id'), primary_key=True, nullable=False)
    
    # __table_args__ = (
    #     Index('model_has_roles_model_id_model_type_index', 'model_id', 'model_type'),
    # )

#     Action	Table
# assignRole()	model_has_roles
# givePermissionTo()	model_has_permissions
# syncPermissions()	model_has_permissions
# syncRoles()	model_has_roles


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
        'mysql_engine':'InnoDB'
    }    
    email = Column(String(255), primary_key=True, nullable=False)
    token = Column(String(255), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)

class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email     = Column(String(255), nullable=False, index=True)
    code      = Column(String(6), nullable=False)
    used      = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PersonalAccessToken(Base):
    __tablename__ = "personal_access_tokens"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tokenable_type = Column(String(255), nullable=False)
    tokenable_id = Column(String(36), nullable=False)
    name = Column(String(255), nullable=False)
    token = Column(String(64), unique=True, nullable=False)
    abilities = Column(Text, nullable=True)
    last_used_at = Column(TIMESTAMP, nullable=True)
    expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    
    # __table_args__ = (
    #     Index('personal_access_tokens_tokenable_type_tokenable_id_index', 'tokenable_type', 'tokenable_id'),
    # )


class RoleHasPermission(Base):
    __tablename__ = "role_has_permissions"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    permission_id = Column(String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    

class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    payload = Column(Text, nullable=False)
    last_activity = Column(Integer, nullable=False)
    
    # __table_args__ = (
    #     Index('sessions_user_id_index', 'user_id'),
    #     Index('sessions_last_activity_index', 'last_activity'),
    # )


