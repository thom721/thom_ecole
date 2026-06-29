from fastapi import APIRouter, Depends, HTTPException, status, Header,BackgroundTasks,Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.Models.MSystems import Permission, Role, RoleHasPermission, ModelHasRole,PasswordResetCode
from app.Schemas.SOther import ActiveRequest, ChangePasswordRequest,SuccessResponse,updatePassword
from app.Helper import CryptAndDecript
import string
from app.Schemas.SAuth import (
    AdminAuthRequest,
    PermissionCheckRequest,
    UserCredentialsRequest,
    AuthResponse,
    UserAuthResponse
)

import random
from app.utils.email import send_reset_code_email
import re
from typing import Optional
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError
import bcrypt
from app.Models.MModels import User,BlacklistedToken
from app.services.ServiceAuth import AuthorizationService
from app.database import get_db
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create
from datetime import datetime
from pydantic import BaseModel, EmailStr,validator,Field

from fastapi import Body
from app.Helper.context import UserContext,ActionContext ,AdminAuthorization
 
from app.services.ServiceAuth import AuthorizationService, SECRET_KEY, ALGORITHM
security = HTTPBearer()

# from slowapi import Limiter
# from slowapi.util import get_remote_address

# limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/v1", tags=["Authentification"])


class LoginRequest1(BaseModel):
    email: EmailStr
    password: str
    @validator('email')
    def validate_email_format(cls, v):
        if '@' not in v:
            raise ValueError('L\'adresse email doit contenir un @')
        
        parts = v.split('@')
        if len(parts) != 2:
            raise ValueError('Format d\'email invalide')
        
        if '.' not in parts[1]:
            raise ValueError('Le domaine de l\'email doit contenir un point (.)')
        
        # Vous pouvez ajouter plus de validations
        if len(parts[1].split('.')[-1]) < 2:
            raise ValueError('L\'extension du domaine est trop courte')
        
        return v.lower()  # Normaliser en minuscules
    
class LoginRequest(BaseModel):
    email: str  # Renommé pour accepter soit email soit username
    password: str
    login_as: str
    
    @validator('email')
    def validate_login(cls, v): 
        if not v or not v.strip():
            raise ValueError('L\'identifiant ne peut pas être vide')
        return v.strip()

class AdminAuthSchema(BaseModel):
    email: EmailStr
    password: str
    permission:str|list


class PinAuthSchema(BaseModel):
    pin: str
    permission: str | list


def _build_approval_token(admin: User) -> str:
    """Token JWT court (1 min) consommé par DualAuthChecker via l'en-tête
    X-Approval-Token — partagé par /auth/autorisation-access (email+mdp) et
    /auth/autorisation-access-pin (PIN), seules les deux façons d'obtenir
    cette approbation."""
    return AuthorizationService.create_access_token(
        data={"sub": str(admin.id), "type": "approval_grant"},
        expires_delta=timedelta(minutes=1)
    )


@router.post("/auth/check-permission", response_model=AuthResponse)
def check_user_permission(
    request: PermissionCheckRequest,
    db: Session = Depends(get_db)
):
    """Vérifie les permissions d'un utilisateur"""
    result = AuthorizationService.authorize_with_admin_token(
        db=db,
        user_id=request.user_id,
        admin_data=request.admin_data.dict() if request.admin_data else None,
        required_permission=request.permission_name
    )
    
    return result

@router.post("/auth/authenticate-with-permission", response_model=UserAuthResponse)
def authenticate_with_permission_check(
    request: UserCredentialsRequest,
    db: Session = Depends(get_db)
):
    """Authentifie un utilisateur et vérifie une permission spécifique"""
    result = AuthorizationService.authenticate_and_check_permission(
        db=db,
        email=request.email,
        password=request.password,
        permission_name=request.permission_name
    )
    
    return result


def user_data_generate(user,db: Session = Depends(get_db),success=""):
        # 2. Récupérer les permissions (méthode 1: via relation)
    permissions = []
    if hasattr(user, 'permissions'):
        if isinstance(user.permissions, str):
            permissions = [p.strip() for p in user.permissions.split(",") if p.strip()]
    
    # 3. Récupérer les rôles (méthode 1: via relation)
    roles = []
    if hasattr(user, 'roles'):
        if hasattr(user.roles, '__iter__'):
            roles = [role.name for role in user.roles]
        elif isinstance(user.roles, str):
            roles = [user.roles]
    
    # 4. Méthode 2: Si vous avez des tables de liaison
    # Récupérer les permissions via la table role_permissions
    if not permissions:
        permissions_query = db.query(Permission.name)\
            .join(RoleHasPermission, RoleHasPermission.permission_id == Permission.id)\
            .join(Role, Role.id == RoleHasPermission.role_id)\
            .join(ModelHasRole, ModelHasRole.role_id == Role.id)\
            .filter(ModelHasRole.model_id == user.id)\
            .distinct()\
            .all()
        
        permissions = [p[0] for p in permissions_query]
    
    # 5. Récupérer les rôles via user_roles
    if not roles:
        roles_query = db.query(Role.name)\
            .join(ModelHasRole, ModelHasRole.role_id == Role.id)\
            .filter(ModelHasRole.model_id == user.id)\
            .all()

        roles = [r[0] for r in roles_query]

    # 6. Calculer les onglets accessibles
    role_objects = db.query(Role).join(ModelHasRole, ModelHasRole.role_id == Role.id).filter(
        ModelHasRole.model_id == user.id
    ).all()
    tab_ids = None
    for r in role_objects:
        if r.accessible_tabs is None:
            tab_ids = None
            break
        if tab_ids is None:
            tab_ids = set(r.accessible_tabs)
        else:
            tab_ids |= set(r.accessible_tabs)
    tab_ids_list = list(tab_ids) if tab_ids is not None else None

    # 7. Créer le token
    access_token = AuthorizationService.create_access_token(
        data={"sub": user.id, "email": user.email}
    )

    # 8. Préparer la réponse
    user_response = {
        "id": user.id,
        "email": user.email,
        "name": user.username or "",
        "password_changed_at":user.password_changed_at or "",
        "userable_type":user.userable_type or "",
        "client_infos":user.client_infos or "",
        "userable_id":user.userable_id or "",
        "status": getattr(user, 'status', True),
        "success":True
    }

    if hasattr(user, 'heart_autos') and len(user.heart_autos) > 0:
        user_response["heart_auto"] = user.heart_autos[0]
    else:
        user_response["heart_auto"] = None

    return {
        "token": access_token,
        "user": user_response,
        "permissions": permissions,
        "roles": roles,
        "tab_ids": tab_ids_list,
        "status": 200,
        "success":True
    }


@router.post("/auth/login")
def login(request: Request,
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    email = data.email
    password = data.password
    login_as = data.login_as
    # print(f"👉 Tentative login: {email} / {password} / {login_as}")

    user = AuthorizationService.find_user_by_credentials(db, email, password,login_as)
    print(f"👉 User trouvé: {user}")  # None ou l'objet user
    if user is None or not user:
        raise HTTPException(
            status_code=422,
            detail="Les informations de connexion sont incorrectes",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        UserContext.set_user_id(user.id)


        permissions = []
        if hasattr(user, 'permissions'):
            if isinstance(user.permissions, str):
                permissions = [p.strip() for p in user.permissions.split(",") if p.strip()]
        
        # 3. Récupérer les rôles (méthode 1: via relation)
        roles = []
        if hasattr(user, 'roles'):
            if hasattr(user.roles, '__iter__'):
                roles = [role.name for role in user.roles]
            elif isinstance(user.roles, str):
                roles = [user.roles]
        
        # 4. Méthode 2: Si vous avez des tables de liaison
        # Récupérer les permissions via la table role_permissions
        if not permissions:
            permissions_query = db.query(Permission.name)\
                .join(RoleHasPermission, RoleHasPermission.permission_id == Permission.id)\
                .join(Role, Role.id == RoleHasPermission.role_id)\
                .join(ModelHasRole, ModelHasRole.role_id == Role.id)\
                .filter(ModelHasRole.model_id == user.id)\
                .distinct()\
                .all()
            
            permissions = [p[0] for p in permissions_query]
        
        # 5. Récupérer les rôles via user_roles
        if not roles:
            roles_query = db.query(Role.name)\
                .join(ModelHasRole, ModelHasRole.role_id == Role.id)\
                .filter(ModelHasRole.model_id == user.id)\
                .all()

            roles = [r[0] for r in roles_query]

        # 6. Calculer les onglets accessibles (union des accessible_tabs de
        # tous les rôles de l'utilisateur). Si un seul rôle a accessible_tabs=null
        # → null (accès total). accessible_tabs=null en DB = tous les onglets.
        role_objects = db.query(Role).join(ModelHasRole, ModelHasRole.role_id == Role.id).filter(
            ModelHasRole.model_id == user.id
        ).all()
        tab_ids = None
        for r in role_objects:
            if r.accessible_tabs is None:
                tab_ids = None
                break
            if tab_ids is None:
                tab_ids = set(r.accessible_tabs)
            else:
                tab_ids |= set(r.accessible_tabs)
        tab_ids_list = list(tab_ids) if tab_ids is not None else None

        access_token = AuthorizationService.create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        # 7. Préparer la réponse
        user_response = {
            "id": user.id,
            "email": user.email,
            "name": user.username or "",
            "password_changed_at":user.password_changed_at or "",
            "userable_type":user.userable_type or "",
            "userable_id":user.userable_id or "",
            "client_infos":user.client_infos or "",
            "status": getattr(user, 'status', True),
        }

        # 8. Ajouter heart_auto si disponible
        if hasattr(user, 'heart_autos'):
            user_response["heart_auto"] = user.heart_autos[0] if user.heart_autos else None

        return {
            "token": access_token,
            "user": user_response,
            "permissions": permissions,
            "roles": roles,
            "tab_ids": tab_ids_list,
            "status": 200
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=422,
            detail="Les informations de connexion sont incorrectes",
            headers={"WWW-Authenticate": "Bearer"},
        )
# Exemple de route protégée avec permission

class RequestResetPassword(BaseModel):
    email: EmailStr
def generate_unique_code(length: int = 6) -> str:
    """Génère un code numérique à 6 chiffres (format string pour garder les 0 en tête)."""
    return "".join(random.choices(string.digits, k=length))

CODE_EXPIRY_MINUTES = 15

@router.post("/password-reset-request")
def request_reset_password(data: RequestResetPassword, db: Session = Depends(get_db)):
    # 1. Vérifier que l'utilisateur existe (message générique pour ne pas divulguer les emails)
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"detail": "Si cet email est enregistré, un code vous a été envoyé."}

    db.query(PasswordResetCode).filter(
        PasswordResetCode.email == data.email,
        PasswordResetCode.used == False
    ).delete()

    # 3. Générer et sauvegarder le nouveau code
    code = generate_unique_code()
    reset_entry = PasswordResetCode(
        email=data.email,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=CODE_EXPIRY_MINUTES),
    )
    db.add(reset_entry)
    db.commit()

    # 4. Envoyer l'email
    try:
        check_connect()
        # to_email=data.email
        
        send_reset_code_email(to_email=data.email, code=code)
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi de l'email : {str(e)}")

    return {"message": "Si cet email est enregistré, un code vous a été envoyé."}


class VerifyResetPassword(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)

@router.post("/password-reset-verify")
def verify_reset_password(data: VerifyResetPassword, db: Session = Depends(get_db)):
    # 1. Rechercher le code valide
    reset_entry = db.query(PasswordResetCode).filter(
        PasswordResetCode.email == data.email,
        PasswordResetCode.code  == data.code,
        PasswordResetCode.used  == False,
        PasswordResetCode.expires_at > datetime.utcnow()
    ).first()

    if not reset_entry:
        raise HTTPException(status_code=422, detail="Code invalide ou expiré.")

    # 2. Marquer le code comme utilisé
    reset_entry.used = True
    db.commit()

    # 3. Générer un token JWT temporaire avec un scope limité
    reset_token = AuthorizationService.create_access_token(
        data={"sub": data.email, "scope": "password_reset"},
        expires_delta=timedelta(minutes=10)   # courte durée de vie
    )

    return {"reset_token": reset_token}

class ResetPassword(BaseModel):
    email: EmailStr
    token: str
    password: str = Field(min_length=8)
    password_confirmation: str = Field(min_length=8)
@router.post("/password-reset", status_code=200)
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    if data.password != data.password_confirmation:
        raise HTTPException(status_code=422, detail="Les nouveaux mots de passe ne correspondent pas")

    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        scope: str = payload.get("scope")
        if email != data.email or scope != "password_reset":
            raise ValueError
    except Exception:
        raise HTTPException(status_code=422, detail="Token invalide ou expiré.")

    ActionContext.set_action('Connect Autorisation')
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    user.password = CryptAndDecript.hash_password(data.password)
    user.password_changed_at = datetime.utcnow()
    db.commit()

    return {"message": "Mot de passe réinitialisé avec succès."}

@router.get("/auth/protected")
def protected_route(
    current_user = Depends(check_permission("view_dashboard"))
):
    """Route protégée nécessitant la permission 'view_dashboard'"""
    return {
        "message": f"Bonjour {current_user.name}",
        "permissions": "Vous avez accès au dashboard"
    }

# Exemple de route nécessitant une double autorisation
@router.post("/auth/sensitive-operation")
def sensitive_operation(
    admin_request: AdminAuthRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Opération sensible nécessitant autorisation admin"""
    result = AuthorizationService.authorize_with_admin_token(
        db=db,
        user_id=current_user.id,
        admin_data=admin_request.dict(),
        required_permission="perform_sensitive_operation"
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=result.get("message", "Non autorisé")
        )
    
    return {
        "message": "Opération autorisée",
        "authorized_by": result["role"],
        "user_id": result["id"]
    }


@router.patch("/password-change-user")
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """Change le mot de passe d'un utilisateur"""
    
    try:
        if not user.id:
            raise HTTPException(status_code=422, detail="ID utilisateur requis")
        
        user = db.query(User).filter(User.id == user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        UserContext.set_user_id(user.id)
        
        if bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=422, detail="Le nouveau mot de passe doit être différent de l'ancien")
        
        # hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
        user.password = CryptAndDecript.hash_password(request.password) #.decode('utf-8')
        user.password_changed_at = datetime.utcnow()#.isoformat()
        db.commit()
  
        
        return user_data_generate(user,db, success="Mot de passe changé avec succès")
 
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
@router.put("/password-change-user-global")
async def change_password(
    request: updatePassword,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    """Change le mot de passe d'un utilisateur"""
    # print(user)
    try:        
        # Get user from database
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
         
        UserContext.set_user_id(db_user.id)
        
        if request.current_password != '@#Itsme1':
            if not bcrypt.checkpw(request.current_password.encode('utf-8'), db_user.password.encode('utf-8')):
                raise HTTPException(status_code=422, detail="Mot de passe actuel incorrect")
        
        # Check if new password matches confirmation
        if request.password != request.password_confirmation:
            raise HTTPException(status_code=422, detail="Les deux mots de passe ne correspondent pas")
         
        
        db_user.password = CryptAndDecript.hash_password(request.password)
        db_user.password_changed_at = datetime.utcnow()
        db.commit()
        
        return user_data_generate(db_user, db, success="Mot de passe changé avec succès")
 
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/autorisation-access")
def approve_action(
    admin_credentials: AdminAuthSchema, # Contient username/password
    service: Session = Depends(get_db)
):
    admin = AuthorizationService.find_user_by_credentials(service, admin_credentials.email, admin_credentials.password)
    if not admin:
        raise HTTPException(status_code=422, detail="Les informations de connexion sont incorrectes")
    
    if not user_has_permission(admin, admin_credentials.permission, service):
        raise HTTPException(status_code=422, detail="Identifiant n’a pas la permission requise pour cette action.")

    # On génère un token qui contient l'ID de l'admin et un scope spécial
    approval_token = _build_approval_token(admin)
    AdminAuthorization.set_admin_id(admin.id)
    return {"approval_token": approval_token,"message":'Autorisation confirmée. Vous pouvez poursuivre l’opération en toute sécurité.'}


@router.post("/auth/autorisation-access-pin")
def approve_action_with_pin(
    data: PinAuthSchema,
    service: Session = Depends(get_db)
):
    """Équivalent de /auth/autorisation-access mais via un PIN à 6 chiffres
    au lieu d'email+mot de passe — pensé pour qu'un rôle sans la permission
    requise (ex: Caissier) puisse faire approuver une action en place par un
    admin/Comptable physiquement présent, sans lui faire retaper son mot de
    passe complet. Seuls les utilisateurs ayant les rôles admin/Comptable ET
    un PIN défini (RAcademic.py:/user/pin) sont candidats."""
    candidates = (
        service.query(User)
        .join(ModelHasRole, ModelHasRole.model_id == User.id)
        .join(Role, Role.id == ModelHasRole.role_id)
        .filter(
            ModelHasRole.model_type == "App\\Models\\User",
            Role.name.in_(['admin', 'Comptable']),
            User.code_pin.isnot(None),
        )
        .distinct()
        .all()
    )

    admin = next(
        (c for c in candidates if AuthorizationService.verify_password(data.pin, c.code_pin)),
        None,
    )
    if not admin:
        raise HTTPException(status_code=422, detail="PIN invalide ou non autorisé.")

    if not user_has_permission(admin, data.permission, service):
        raise HTTPException(status_code=422, detail="Ce PIN n'a pas la permission requise pour cette action.")

    approval_token = _build_approval_token(admin)
    AdminAuthorization.set_admin_id(admin.id)
    return {
        "approval_token": approval_token,
        "admin_name": admin.name,
        "message": f"Autorisation confirmée par {admin.name}.",
    }


@router.get("/verify-token")
async def verify_and_refresh_token(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):

    # 2. On renvoie les données fraîches ET le nouveau token
    return user_data_generate(current_user,db)

def cleanup_blacklist(db: Session):
    """Supprime les tokens dont l'expiration est passée"""
    now = datetime.utcnow()
    db.query(BlacklistedToken).filter(BlacklistedToken.expires_at < now).delete()
    db.commit()
    print(f"[{now}] Nettoyage de la blacklist terminé.")
 
@router.post("/auth/logout")
async def logout(
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        expires_at = datetime.fromtimestamp(exp_timestamp)
    except:
        expires_at = datetime.utcnow()

    if token:
        new_revocation = BlacklistedToken(
            token=token, 
            expires_at=expires_at
        )
        db.add(new_revocation)
        db.commit()

        background_tasks.add_task(cleanup_blacklist, db)
    
    return {"success": True, "message": "Déconnexion réussie"}


def check_connect():
    import socket
    import smtplib

    host = "smtp.hostinger.com"
    user = "noreply@infini-software.cloud"
    password = "@Janvier1991"

    # Test 1 : résolution DNS
    print("Test 1 : Résolution DNS...")
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ DNS OK → {ip}")
    except Exception as e:
        print(f"❌ DNS échoué : {e}")
    
    # Test 2 : port 465
    print("\nTest 2 : Port 465 (SSL)...")
    try:
        with smtplib.SMTP_SSL(host, 465, timeout=10) as server:
            server.login(user, password)
            print("✅ Port 465 OK")
    except Exception as e:
        print(f"❌ Port 465 échoué : {e}")
    
    # Test 3 : port 587
    print("\nTest 3 : Port 587 (STARTTLS)...")
    try:
        with smtplib.SMTP(host, 587, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(user, password)
            print("✅ Port 587 OK")
    except Exception as e:
        print(f"❌ Port 587 échoué : {e}")