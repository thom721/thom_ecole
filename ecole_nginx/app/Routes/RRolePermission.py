# app/Routes/RAuthorization.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text,select, delete
from typing import List, Optional
from app.Models.MModels import User, Professeur
from app.Models.MSystems import Permission, Role, Personnel
from app.Schemas.SRolePermission import (
    PermissionResponse, RoleResponse, UserWithPermissions,RoleResponseShow,
    UserWithRoles, AssignRoleRequest, AssignPermissionRequest,PermissionResponseShow,PermissionResponseAll,UserWithPermissionsAll
)
from app.database import get_db
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
from app.Models.MSystems import ModelHasPermission,ModelHasRole,RoleHasPermission
from pydantic import BaseModel, Field, field_validator, model_validator
import logging

logger = logging.getLogger(__name__)



router = APIRouter(prefix="/api/v1", tags=["Role et Permission"])

# 1. get_all_permissions
@router.get("/permission", response_model=PermissionResponseShow)
def get_all_permissions(db: Session = Depends(get_db)):
    """
    Récupère toutes les permissions.
    """
    permissions = db.query(Permission).all()
    # return permissions 
    return PermissionResponseShow(data=permissions) 

# 2. get_all_roles
@router.get("/role", response_model=RoleResponseShow)
def get_all_roles(db: Session = Depends(get_db)):
    """
    Récupère tous les rôles.
    """
    roles = db.query(Role).all()
    return RoleResponseShow(data=roles)

# 3. assign_role_to_user

@router.post("/assign-role-to-user")
def assign_role_to_user(
    request: AssignRoleRequest,
    db: Session = Depends(get_db),current_user: User = Depends(check_permission("Modifier role"))
):
    """
    Assigner un rôle à un utilisateur.
    """
    
    try:
        user_exists = db.query(
                select(User.id).where(User.id == request.user_id).exists()
            ).scalar()
            
        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail={"errors": {"user_id": ["Utilisateur introuvable."]}}
            )
        
        valid_roles = []
        for role_id in request.role:
            role_exists = db.query(
                select(Role.id).where(Role.id == role_id).exists()
            ).scalar()
            
            if not role_exists:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": {"role": [f"Le rôle {role_id} n'existe pas."]}}
                )
            
            valid_roles.append(role_id)
        
        # Supprimer les anciens rôles

        delete_stmt = delete(ModelHasRole).where(
            ModelHasRole.model_id == request.user_id,
            ModelHasRole.model_type == "App\\Models\\User"
        )
        db.execute(delete_stmt)


        for role_id in valid_roles:
            new_role = ModelHasRole(
                role_id=role_id,
                model_type="App\\Models\\User",
                model_id=request.user_id
            )
            db.add(new_role)
        
        db.commit()
    
        return {"success": "Le ou les rôles ont été assignés avec succès."}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur dans assign_role_to_user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"errors": str(e)}
        )

# 
# 5. get_permission_by_role
@router.get("/get-permission-by-role/{role}", response_model=PermissionResponseAll)
def get_permission_by_role(role: str, db: Session = Depends(get_db)):
    """
    Récupérer les permissions d'un rôle spécifique.
    """
    role = db.query(Role).filter(Role.id == role).first()
    if not role:
        raise HTTPException(status_code=404, detail="Rôle introuvable")
    
    return {"permis": [{"id": p.id, "name": p.name} for p in role.permissions]}


# 6. fetch_data_with_permission
@router.get("/fetch-data-with-permission")
def fetch_data_with_permission(
    data: Optional[str] = Query(None, max_length=255),
    db: Session = Depends(get_db)
):
    """
    Rechercher des utilisateurs avec leurs permissions.
    """
    # Recherche des professeurs
    profs_query = db.query(User.id, Professeur.nom, Professeur.prenom)\
        .join(Professeur, Professeur.id == User.userable_id)\
        .filter(User.userable_type == 'App\\Models\\Professeur')
    
    if data:
        search_term = f"%{data}%"
        profs_query = profs_query.filter(
            (Professeur.nom.ilike(search_term)) | (Professeur.prenom.ilike(search_term))
        )
    
    profs = profs_query.all()
    
    # Recherche des personnels
    pers_query = db.query(User.id, Personnel.nom, Personnel.prenom)\
        .join(Personnel, Personnel.id == User.userable_id)\
        .filter(User.userable_type == 'App\\Models\\Personnel')
    
    if data:
        search_term = f"%{data}%"
        pers_query = pers_query.filter(
            (Personnel.nom.ilike(search_term)) | (Personnel.prenom.ilike(search_term))
        )
    
    personnels = pers_query.all()
    
    users = profs + personnels

    result = []

    for user_id, nom, prenom in users:
        # Permissions directes
        direct_perms = db.execute(
            text("SELECT permission_id FROM model_has_permissions WHERE model_id = :user_id"),
            {"user_id": user_id}
        ).fetchall()
        
        # Rôles
        role_ids = db.execute(
            text("SELECT role_id FROM model_has_roles WHERE model_id = :user_id"),
            {"user_id": user_id}
        ).fetchall()
        
        # Permissions des rôles
        role_perms = []
        if role_ids:
            # SQLAlchemy ne supporte pas %s dans text(), on fait une jointure dynamique
            # On utilise un bind param pour chaque role
            bind_params = {f"role_{i}": r[0] for i, r in enumerate(role_ids)}
            placeholders = ", ".join(f":role_{i}" for i in range(len(role_ids)))
            role_perms = db.execute(
                text(f"SELECT DISTINCT permission_id FROM role_has_permissions WHERE role_id IN ({placeholders})"),
                bind_params
            ).fetchall()
        
        # Fusionner toutes les permissions
        all_perms = list(set([p[0] for p in direct_perms] + [p[0] for p in role_perms]))
        
        result.append({
            "id": user_id,
            "nom": nom,
            "prenom": prenom,
            "permissions": all_perms
        })
    
    # return UserWithPermissionsAll(data=result)
    return {"data":result}

# 7. fetch_data_with_role
@router.get("/fetch-data-with-role")#, response_model=List[UserWithRoles]
def fetch_data_with_role(
    data: Optional[str] = Query(None, max_length=255),
    db: Session = Depends(get_db)
):
    """
    Rechercher des utilisateurs avec leurs rôles.
    """ 
    # Même logique que fetch_data_with_permission mais pour les rôles
    profs_query = db.query(User.id, Professeur.nom, Professeur.prenom)\
        .join(Professeur, Professeur.id == User.userable_id)\
        .filter(User.userable_type == 'App\\Models\\Professeur')
    
    if data:
        search_term = f"{data}%"
        profs_query = profs_query.filter(
            (Professeur.nom.ilike(search_term)) | (Professeur.prenom.ilike(search_term))
        )
    
    profs = profs_query.all()
    
    pers_query = db.query(User.id, Personnel.nom, Personnel.prenom)\
        .join(Personnel, Personnel.id == User.userable_id)\
        .filter(User.userable_type == 'App\\Models\\Personnel')
    
    if data:
        search_term = f"%{data}%"
        pers_query = pers_query.filter(
            (Personnel.nom.ilike(search_term)) | (Personnel.prenom.ilike(search_term))
        )
    
    personnels = pers_query.all()
    
    users = profs + personnels
    result = []
    
    for user_id, nom, prenom in users:
        roles = db.execute(
            text("SELECT role_id FROM model_has_roles WHERE model_id = :user_id"),
            {"user_id": user_id}
        ).fetchall()
        
        result.append({
            "id": user_id,
            "nom": nom,
            "prenom": prenom,
            "roles": [r[0] for r in roles]
        })
    
    return {"data":result}






class AssignPermissionRequest(BaseModel):
    """
    Modèle pour l'assignation de permissions
    
    Soit à un rôle, soit à un utilisateur (pas les deux)
    """
    role: Optional[str] = Field(None, description="ID du rôle")
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur")
    permission: List[str] = Field(..., min_items=1, description="Liste des IDs de permissions")
    
    @field_validator('permission')
    @classmethod
    def validate_permission_list(cls, v: List[str]) -> List[str]:
        """Valider que la liste de permissions n'est pas vide"""
        if not v:
            raise ValueError("Le champ permission est requis et doit contenir au moins un élément")
        
        # Valider que chaque permission est un ID valide
        for perm in v:
            if not perm or not perm.strip():
                raise ValueError("Chaque permission doit avoir un ID valide")
        
        return v
    
    @model_validator(mode='after')
    def validate_role_or_user(self):
        """Valider qu'on a soit un rôle, soit un utilisateur, mais pas les deux"""
        role = self.role
        user_id = self.user_id
        
        # Les deux sont fournis
        if role and user_id:
            raise ValueError("Vous devez fournir soit un rôle, soit un utilisateur, mais pas les deux")
        
        # Aucun des deux n'est fourni
        if not role and not user_id:
            raise ValueError("Vous devez fournir soit un rôle, soit un utilisateur")
        
        return self
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "role": "123e4567-e89b-12d3-a456-426614174000",
                    "permission": ["abc12345-e89b-12d3-a456-426614174001", "def67890-e89b-12d3-a456-426614174002"]
                },
                {
                    "user_id": "987e6543-e89b-12d3-a456-426614174003",
                    "permission": ["abc12345-e89b-12d3-a456-426614174001"]
                }
            ]
        }

class AssignPermissionResponse(BaseModel):
    """Réponse pour l'assignation de permissions"""
    success: str

class ErrorResponse(BaseModel):
    """Réponse d'erreur"""
    errors: dict

 


@router.post("/assign-permission-to-role", response_model=AssignPermissionResponse, status_code=200)
async def assign_permission_to_role(
    request_data: AssignPermissionRequest,
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    """
    Assigner des permissions à un rôle ou à un utilisateur
    
    **Règles:**
    - Vous devez fournir **soit** un `role` **soit** un `user_id`, mais pas les deux
    - Le champ `permission` doit contenir au moins un ID de permission valide
    - Les anciennes permissions seront remplacées par les nouvelles
    
    **Pour un rôle:**
```json
    {
        "role": "role-uuid",
        "permission": ["perm1-uuid", "perm2-uuid"]
    }
```
    
    **Pour un utilisateur:**
```json
    {
        "user_id": "user-uuid",
        "permission": ["perm1-uuid", "perm2-uuid"]
    }
```
    """
    
    try:
        role_id = request_data.role
        user_id = request_data.user_id
        permissions = request_data.permission
        
        # ============================================================
        # VALIDATION DES ENTITÉS
        # ============================================================
        
        # Vérifier que toutes les permissions existent
        for perm_id in permissions:
            perm_exists = db.query(
                select(Permission.id).where(Permission.id == perm_id).exists()
            ).scalar()
            
            if not perm_exists:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": {"permission": [f"La permission {perm_id} n'existe pas."]}}
                )
        
        # ============================================================
        # ASSIGNATION À UN RÔLE
        # ============================================================
        
        if role_id and not user_id:
            # Vérifier que le rôle existe
            role_exists = db.query(
                select(Role.id).where(Role.id == role_id).exists()
            ).scalar()
            if not user_has_permission(current_user, "Modifier role", db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Non autorisé !"
                )
            if not role_exists:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": {"role": [f"Le rôle {role_id} n'existe pas."]}}
                )
            
            # Supprimer les anciennes permissions du rôle
            delete_stmt = delete(RoleHasPermission).where(
                RoleHasPermission.role_id == role_id
            )
            db.execute(delete_stmt)
            
            # Ajouter les nouvelles permissions
            for perm_id in permissions:
                new_permission = RoleHasPermission(
                    permission_id=perm_id,
                    role_id=role_id
                )
                db.add(new_permission)
            
            db.commit()
            
            logger.info(f"Permissions assignées au rôle {role_id}: {permissions}")
            
            return AssignPermissionResponse(
                success="La ou les permissions ont été assignées avec succès."
            )
        
        # ============================================================
        # ASSIGNATION À UN UTILISATEUR
        # ============================================================
        
        elif user_id and not role_id:
            # Vérifier que l'utilisateur existe
            if not user_has_permission(current_user, "Modifier permission", db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Non autorisé !"
                )
            user_exists = db.query(
                select(User.id).where(User.id == user_id).exists()
            ).scalar()
            
            if not user_exists:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": {"user_id": [f"L'utilisateur {user_id} n'existe pas."]}}
                )
            
            # Supprimer les anciennes permissions de l'utilisateur
            delete_stmt = delete(ModelHasPermission).where(
                ModelHasPermission.model_id == user_id,
                ModelHasPermission.model_type == "App\\Models\\User"
            )
            db.execute(delete_stmt)
            
            # Ajouter les nouvelles permissions
            for perm_id in permissions:
                new_permission = ModelHasPermission(
                    permission_id=perm_id,
                    model_type="App\\Models\\User",
                    model_id=user_id
                )
                db.add(new_permission)
            
            db.commit()
            
            logger.info(f"Permissions assignées à l'utilisateur {user_id}: {permissions}")
            
            return AssignPermissionResponse(
                success="La ou les permissions ont été assignées avec succès."
            )
        
        else:
            # Ce cas ne devrait jamais arriver grâce à la validation Pydantic
            raise HTTPException(
                status_code=422,
                detail={"errors": {"general": ["Vous devez fournir soit un rôle, soit un utilisateur."]}}
            )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur dans assign_permission_to_role: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"errors": {"general": [str(e)]}}
        )