from fastapi import Depends, HTTPException, status,Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from typing import List
from app.Models.MSystems import Permission, Role, RoleHasPermission, ModelHasRole,ModelHasPermission
from jwt import PyJWTError
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Optional
from app.database import get_db
from app.Models.MModels import User,BlacklistedToken
from app.services.ServiceAuth import AuthorizationService, SECRET_KEY, ALGORITHM 
# from jose import JWTError  # ou PyJWTError selon ta lib

security = HTTPBearer()

def get_current_user11(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dépendance pour obtenir l'utilisateur courant via token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dépendance pour obtenir l'utilisateur courant avec vérification Blacklist"""
    
    token = credentials.credentials # On récupère le string du token
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. VÉRIFICATION DE LA BLACKLIST
    # On regarde si ce token précis n'a pas été révoqué
    is_blacklisted = db.query(BlacklistedToken).filter(
        BlacklistedToken.token == token
    ).first()
    
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expirée suite à une déconnexion.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. DÉCODAGE DU JWT (Ton code original)
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (JWTError, Exception): # Gère les erreurs de signature ou d'expiration
        raise credentials_exception
    
    # 3. RÉCUPÉRATION DE L'UTILISATEUR
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Vérifie que l'utilisateur est actif"""
    if not current_user.status:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def check_permission(permission_name: str):
    """Décorateur pour vérifier les permissions"""
    def permission_dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        has_permission = AuthorizationService.user_has_permission(
            db, current_user.id, permission_name
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' requise"
            )

        return current_user

    return permission_dependency


def require_role(roles: List[str]):
    """Factory: crée une dépendance qui exige au moins un des rôles donnés."""
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if not user_has_role(current_user, roles, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôle(s) requis : {', '.join(roles)}"
            )
        return current_user
    return checker


def user_has_role(user, role_names: List[str], db: Session) -> bool:
    """Vérifie si l'utilisateur a un des rôles spécifiés"""
    roles = db.query(Role.name).join(
        ModelHasRole, ModelHasRole.role_id == Role.id
    ).filter(
        ModelHasRole.model_id == user.id,
        ModelHasRole.model_type == "App\\Models\\User"
    ).all()
    
    user_role_names = [r.name for r in roles]
    return any(role in user_role_names for role in role_names)

def user_has_permission111(user, permission_name: str, db: Session) -> bool:
    """Vérifie si l'utilisateur a une permission spécifique"""
    # Récupérer toutes les permissions de l'utilisateur via ses rôles
    permissions = db.query(Permission.name).join(
        RoleHasPermission, RoleHasPermission.permission_id == Permission.id
    ).join(
        ModelHasRole, ModelHasRole.role_id == RoleHasPermission.role_id
    ).filter(
        ModelHasRole.model_id == user.id,
        ModelHasRole.model_type == "App\\Models\\User"
    ).all()
    
    permission_names = [p.name for p in permissions]
    
    return permission_name in permission_names

# def user_has_permission(user, permission_name: str|[], db: Session) -> bool:
#     """Vérifie si un utilisateur a une permission donnée"""
#     try:
            
#         direct_permissions = db.query(Permission.name)\
#             .join(ModelHasPermission, ModelHasPermission.permission_id == Permission.id)\
#             .filter(
#                 ModelHasPermission.model_id == user.id,
#                 ModelHasPermission.model_type == "App\\Models\\User"
#             )\
#             .all()

#         role_permissions = db.query(Permission.name)\
#             .join(RoleHasPermission, RoleHasPermission.permission_id == Permission.id)\
#             .join(ModelHasRole, ModelHasRole.role_id == RoleHasPermission.role_id)\
#             .filter(
#                 ModelHasRole.model_id == user.id,
#                 ModelHasRole.model_type == "App\\Models\\User"
#             )\
#             .all()
        
#         # Combiner les permissions
#         all_permissions = {p.name for p in direct_permissions + role_permissions}# 
        
#         return permission_name in all_permissions
        
#     except Exception as e:
#         print(f"[Erreur] user_has_permission → {e}")
#         return False

def user_has_permission(user, permission_name: str | list, db: Session) -> bool:
    try:
        # On s'assure que c'est une liste pour simplifier la comparaison
        required_perms = [permission_name] if isinstance(permission_name, str) else permission_name
            
        # 1. Permissions directes
        direct_permissions = db.query(Permission.name)\
            .join(ModelHasPermission, ModelHasPermission.permission_id == Permission.id)\
            .filter(
                ModelHasPermission.model_id == user.id,
                ModelHasPermission.model_type == "App\\Models\\User"
            ).all()

        # 2. Permissions via les Rôles
        role_permissions = db.query(Permission.name)\
            .join(RoleHasPermission, RoleHasPermission.permission_id == Permission.id)\
            .join(ModelHasRole, ModelHasRole.role_id == RoleHasPermission.role_id)\
            .filter(
                ModelHasRole.model_id == user.id,
                ModelHasRole.model_type == "App\\Models\\User"
            ).all()
        
        # Set pour une recherche ultra rapide (O(1))
        all_permissions = {p[0] for p in (direct_permissions + role_permissions)}
        print(f"\n\n{all_permissions}\n\n\n")
        # Vérifie si au moins une des permissions requises est possédée
        return any(perm in all_permissions for perm in required_perms)
        
    except Exception as e:
        print(f"❌ Erreur user_has_permission: {e}")
        return False

def verify_dual_auth(
    permission: str | list, # La permission requise pour l'action
    x_approval_token: Optional[str] = Header(None),
    service: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    headers = {
        "X-Action-Success": "false",
        "X-Authorization-Required": "true",
        "X-Message": "Action non autorisee. Veuillez fournir un autre compte pour autorisation.",
        "X-Require-Admin-Auth": "true"
    }
    # 1. Si l'utilisateur a déjà la permission, c'est direct
    if user_has_permission(current_user, permission, service):
        return {"user_id": current_user.id, "admin_id": None}

    # 2. Sinon, on exige le token d'approbation
    if not x_approval_token:
        raise HTTPException(status_code=202, detail="Autorisation admin requise",headers=headers)

    try:
        # 3. Décodage du token
        payload = jwt.decode(x_approval_token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("sub")
        
        if payload.get("type") != "approval_grant":
            raise HTTPException(status_code=401, detail="Type de token invalide")

        # 4. RÉCUPÉRATION DE L'ADMIN ET VÉRIFICATION DES DROITS
        admin = service.query(User).filter(User.id == admin_id).first()
        
        if not admin:
            raise HTTPException(status_code=404, detail="Admin approbateur introuvable")

        # On vérifie si l'ADMIN a la permission requise
        if not user_has_permission(admin, permission, service):
            raise HTTPException(
                status_code=403, 
                detail="L'approbateur n'a pas les privilèges suffisants pour cette action"
            )
            
        return {"user_id": current_user.id, "admin_id": admin.id}
        
    except JWTError:
        raise HTTPException(
            status_code=202, 
            detail="Session d'approbation expirée",
            headers=headers
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=202, 
            detail="Session d'approbation expirée",
            headers=headers
        )
    
def first_or_create(db, model, search: dict, create: dict):
    instance = db.query(model).filter_by(**search).first()

    if instance:
        return instance

    instance = model(**search, **create)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance

def first_or_update(db, model, search: dict, data: dict):
    instance = db.query(model).filter_by(**search).first()

    if instance:
        for key, value in data.items():
            setattr(instance, key, value)
    else:
        instance = model(**search, **data)
        db.add(instance)

    db.commit()
    db.refresh(instance)
    return instance

from sqlalchemy.exc import SQLAlchemyError

def first_or_update_safe(db, model, search: dict, data: dict):
    try:
        instance = db.query(model).filter_by(**search).first()

        if instance:
            for k, v in data.items():
                setattr(instance, k, v)
        else:
            instance = model(**search, **data)
            db.add(instance)

        db.commit()
        db.refresh(instance)
        return instance

    except SQLAlchemyError:
        db.rollback()
        raise



def validate_exists(model, field, db: Session, value, message=None):
    exists = db.query(model).filter(field == value).first()

    if not exists:
        raise HTTPException(
            status_code=422,
            detail=message or f"{model.__name__} introuvable"
        )

    

def authorize_with_admin(
    required_permission: str,
    admin_data: dict = None
):
    """Décorateur pour l'autorisation avec admin"""
    def authorization_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        result = AuthorizationService.authorize_with_admin_token(
            db=db,
            user_id=current_user.id if current_user else None,
            admin_data=admin_data,
            required_permission=required_permission
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.get("message", "Non autorisé")
            )
        
        return result
    
    return authorization_dependency


class DualAuthChecker:
    def __init__(self, permission: str | list):
        self.permission = permission

    def __call__(
        self, 
        x_approval_token: Optional[str] = Header(None), 
        service: Session = Depends(get_db), 
        current_user: User = Depends(get_current_user)
    ):
        return verify_dual_auth(self.permission, x_approval_token, service, current_user)