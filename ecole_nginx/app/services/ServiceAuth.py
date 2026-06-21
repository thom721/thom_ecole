from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_,and_
import bcrypt
from typing import Optional, Dict, Any,List
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError

from app.Models.MModels import User
from app.Models.MSystems import Permission, Role, RoleHasPermission, ModelHasRole,ModelHasPermission
from app.database import get_db
from app.config.Config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

class AuthorizationService:    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe correspond au hash"""
        hashed_normalized = hashed_password.replace("$2y$", "$2b$")
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_normalized.encode('utf-8')
        )
        # return bcrypt.checkpw(
        #     plain_password.encode('utf-8'), 
        #     hashed_password.encode('utf-8')
        # )
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash un mot de passe"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def user_has_permission(db: Session, user_id: str, permission_name: str) -> bool:
        """Vérifie si un utilisateur a une permission donnée (directe ou via un rôle), en un seul aller-retour DB"""
        try:
            direct = db.query(Permission.id)\
                .join(ModelHasPermission, ModelHasPermission.permission_id == Permission.id)\
                .filter(
                    Permission.name == permission_name,
                    ModelHasPermission.model_id == user_id,
                    ModelHasPermission.model_type == "App\\Models\\User"
                )

            via_role = db.query(Permission.id)\
                .join(RoleHasPermission, RoleHasPermission.permission_id == Permission.id)\
                .join(ModelHasRole, ModelHasRole.role_id == RoleHasPermission.role_id)\
                .filter(
                    Permission.name == permission_name,
                    ModelHasRole.model_id == user_id,
                    ModelHasRole.model_type == "App\\Models\\User"
                )

            return db.query(direct.union(via_role).exists()).scalar()

        except Exception as e:
            print(f"[Erreur] user_has_permission → {e}")
            return False
    
    # @staticmethod
    # Ajoute ces prints dans find_user_by_credentials
    @staticmethod
    def find_user_by_credentials(db: Session, email: str, password: str, login_as) -> Optional[User]:
        try:
            # 1. Vérifie si l'email existe
            user_by_email = db.query(User).filter(
                or_(User.email == email, User.username == email)
            ).first()
            # print(f"👉 User par email seulement: {user_by_email}")
            # new_password = "m9ZNc42Yn2M"
            new_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8").replace("$2b$", "$2y$")
            # print(new_hash)
            
            if user_by_email:
                # print(f"👉 userable_type en base: '{user_by_email.userable_type}'")
                # print(f"👉 userable_type reçu:    '{login_as}'")
                # print(f"👉 status: {user_by_email.status}")
                # print(f"👉 Hash en base: {user_by_email.password}")
                
                # 2. Vérifie le password
                pwd_ok = AuthorizationService.verify_password(password, user_by_email.password)
                print(f"👉 Password correct: {pwd_ok}")

            user = db.query(User).filter(
                or_(User.email == email, User.username == email),
                User.userable_type == login_as if login_as != 'as_desktop' else True
            ).first()
            
            if not user:
                return None
                
            if AuthorizationService.verify_password(password, user.password):
                return user
            
            return None
            
        except Exception as e:
            print(f"[Erreur] find_user_by_credentials → {e}")
            import traceback
            traceback.print_exc()
            return None
    # def find_user_by_credentials(db: Session, email: str, password: str, login_as) -> Optional[User]:
    #     """Trouve un utilisateur par email et vérifie le mot de passe"""
    #     try:
             
    #         user = db.query(User).filter(
    #             or_(
    #                 User.email == email,
    #                 User.username == email
    #             ),
    #             User.userable_type == login_as if login_as != 'as_desktop' else True
    #         ).first()
    #         if not user:
    #             return None
             
    #         if AuthorizationService.verify_password(password, user.password):
    #             return user
            
    #         return None
            
    #     except Exception as e:
    #         print(f"[Erreur] find_user_by_credentials → {e}")
    #         return None
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crée un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def authorize_with_admin_token(
        db: Session,
        user_id: Optional[str] = None,
        admin_data: Optional[Dict[str, Any]] = None,
        required_permission: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Vérifie les permissions d'un utilisateur ou d'un administrateur.
        """
        # 1. Vérifie l'utilisateur courant
        if user_id and required_permission:
            has_permission = AuthorizationService.user_has_permission(db, user_id, required_permission)
            if has_permission:
                return {
                    "success": True,
                    "id": user_id,
                    "role": "user"
                }
        
        # 2. Si l'utilisateur n'a pas la permission, demande une autorisation admin
        if not admin_data or "email" not in admin_data or "password" not in admin_data:
            return {
                "success": False,
                "authorization": False,
                "message": "Action non autorisée. Veuillez fournir un autre compte pour autorisation.",
                "required_permission": required_permission,
                "require_admin_auth": True
            }
        
        # 3. Vérifie les identifiants de l'admin
        admin_user = AuthorizationService.find_user_by_credentials(
            db, admin_data["email"], admin_data["password"]
        )
        
        if not admin_user:
            return {
                "success": False,
                "authorization": False,
                "message": "Identifiants administrateur invalides."
            }
        
        # 4. Vérifie les permissions de l'admin
        if required_permission:
            has_admin_permission = AuthorizationService.user_has_permission(
                db, admin_user.id, required_permission
            )
            if not has_admin_permission:
                return {
                    "success": False,
                    "authorization": False,
                    "message": "L'administrateur n'a pas la permission requise pour cette action."
                }
        
        # 5. Tout est bon
        return {
            "success": True,
            "id": admin_user.id,
            "role": "admin"
        }
    
    @staticmethod
    def authenticate_and_check_permission(
        db: Session,
        email: str,
        password: str,
        permission_name: str
    ) -> Dict[str, Any]:
        """Authentifie un utilisateur et vérifie ses permissions"""
        try:
            user = AuthorizationService.find_user_by_credentials(db, email, password)
            
            if not user:
                return {
                    "success": False,
                    "errors": "Identifiant ou mot de passe incorrect"
                }
            
            has_permission = AuthorizationService.user_has_permission(db, user.id, permission_name)
            
            if has_permission:
                # Créer un token d'accès
                access_token = AuthorizationService.create_access_token(
                    data={"sub": user.id, "email": user.email}
                )
                
                return {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name
                    },
                    "permission": True,
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            
            return {
                "success": False,
                "errors": "L'utilisateur n'a pas la permission requise pour cette action"
            }
            
        except Exception as e:
            print(f"[Erreur] authenticate_and_check_permission → {e}")
            return {
                "success": False,
                "errors": "Une erreur est survenue lors de l'authentification"
            }
        
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

    

