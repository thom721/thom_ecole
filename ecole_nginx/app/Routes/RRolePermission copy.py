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
from app.dependencies.Dependencie import check_permission,first_or_create 
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
    db: Session = Depends(get_db)
):
    """
    Assigner un rôle à un utilisateur.
    """
    # Vérifier si l'utilisateur existe
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    # Supprimer les anciens rôles
    db.execute(
        "DELETE FROM model_has_roles WHERE model_id = :user_id",
        {"user_id": request.user_id}
    )
    
    # Ajouter les nouveaux rôles
    for role_id in request.role:
        db.execute(
            """
            INSERT INTO model_has_roles (role_id, model_type, model_id)
            VALUES (:role_id, :model_type, :model_id)
            """,
            {
                "role_id": role_id,
                "model_type": "App\\Models\\User",
                "model_id": request.user_id
            }
        )
    
    db.commit()
    return {"success": "Le ou les rôles ont été assignés avec succès."}

# # 4. assign_permission_to_role
# @router.post("/assign-permission-to-role")
# def assign_permission_to_role(
#     request: AssignPermissionRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Assigner une permission à un rôle ou utilisateur.
#     """
#     if request.role and request.user_id:
#         raise HTTPException(
#             status_code=400,
#             detail="Vous devez fournir soit un rôle, soit un utilisateur, mais pas les deux."
#         )
    
#     if not request.permission:
#         raise HTTPException(
#             status_code=400,
#             detail="Le champ permission est requis."
#         )
    
 
    
#     if request.role:
#         # Assigner à un rôle
#         role = db.query(Role).filter(Role.id == request.role).first()
#         if not role:
#             raise HTTPException(status_code=404, detail="Rôle introuvable")
        
#         # Supprimer anciennes permissions
#         db.execute(
#             text("DELETE FROM role_has_permissions WHERE role_id = :role_id"),
#             {"role_id": request.role}
#         )
        
#         # Ajouter nouvelles permissions
#         for perm_id in request.permission:
#             db.execute(
#                text( "INSERT INTO role_has_permissions (permission_id, role_id) VALUES (:perm_id, :role_id)"),
#                 {"perm_id": perm_id, "role_id": request.role}
#             )
    
#     elif request.user_id:
#         # Assigner à un utilisateur
#         user = db.query(User).filter(User.id == request.user_id).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="Utilisateur introuvable")
        
#         # Supprimer anciennes permissions
#         db.execute(
#             text("DELETE FROM model_has_permissions WHERE model_id = :user_id"),
#             {"user_id": request.user_id}
#         )
        
#         # Ajouter nouvelles permissions
#         for perm_id in request.permission:
#             db.execute(
#                 """
#                 INSERT INTO model_has_permissions (permission_id, model_type, model_id)
#                 VALUES (:perm_id, :model_type, :model_id)
#                 """,
#                 {
#                     "perm_id": perm_id,
#                     "model_type": "App\\Models\\User",
#                     "model_id": request.user_id
#                 }
#             )
    
#     db.commit()
#     return {"success": "La ou les permissions ont été assignées avec succès."}


def sync_role_permissions(db: Session, role_id: str, new_permissions: list[str]):
    # Permissions actuelles
    current = db.execute(
        text("SELECT permission_id FROM role_has_permissions WHERE role_id = :role_id"),
        {"role_id": role_id}
    ).fetchall()

    current_ids = {p[0] for p in current}
    new_ids = set(new_permissions)

    to_add = new_ids - current_ids
    # ➖ À supprimer
    to_remove = current_ids - new_ids

    if to_remove:
        db.execute(
            text("""
                DELETE FROM role_has_permissions
                WHERE role_id = :role_id
                AND permission_id IN :perm_ids
            """),
            {"role_id": role_id, "perm_ids": tuple(to_remove)}
        )

    for perm_id in to_add:
        db.execute(
            text("""
                INSERT INTO role_has_permissions (role_id, permission_id)
                VALUES (:role_id, :perm_id)
            """),
            {"role_id": role_id, "perm_id": perm_id}
        )


def sync_user_permissions(db: Session, user_id: str, new_permissions: list[str]):
    current = db.execute(
        text("SELECT permission_id FROM model_has_permissions WHERE model_id = :user_id"),
        {"user_id": user_id}
    ).fetchall()

    current_ids = {p[0] for p in current}
    new_ids = set(new_permissions)

    to_add = new_ids - current_ids
    to_remove = current_ids - new_ids

    if to_remove:
        db.execute(
            text("""
                DELETE FROM model_has_permissions
                WHERE model_id = :user_id
                AND permission_id IN :perm_ids
            """),
            {"user_id": user_id, "perm_ids": tuple(to_remove)}
        )

    for perm_id in to_add:
        db.execute(
            text("""
                INSERT INTO model_has_permissions (permission_id, model_type, model_id)
                VALUES (:perm_id, :model_type, :model_id)
            """),
            {
                "perm_id": perm_id,
                "model_type": "App\\Models\\User",
                "model_id": user_id
            }
        )

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
    db: Session = Depends(get_db)
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










        from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import List
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class AssignRoleRequest(BaseModel):
    """Modèle pour l'assignation de rôles à un utilisateur"""
    user_id: str = Field(..., description="ID de l'utilisateur")
    role: List[str] = Field(..., min_items=1, description="Liste des IDs de rôles")
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Valider que l'ID utilisateur n'est pas vide"""
        if not v or not v.strip():
            raise ValueError("Le champ user_id est requis")
        return v.strip()
    
    @field_validator('role')
    @classmethod
    def validate_role_list(cls, v: List[str]) -> List[str]:
        """Valider que la liste de rôles n'est pas vide"""
        if not v:
            raise ValueError("Le champ role doit être une liste non vide")
        
        # Valider que chaque rôle est un ID valide
        for role in v:
            if not role or not role.strip():
                raise ValueError("Chaque rôle doit avoir un ID valide")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": ["abc12345-e89b-12d3-a456-426614174001", "def67890-e89b-12d3-a456-426614174002"]
            }
        }

class RoleList(BaseModel):
    """Liste de rôles à assigner"""
    role: List[str] = Field(..., min_items=1, description="Liste des IDs de rôles")
    
    @field_validator('role')
    @classmethod
    def validate_role_list(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Le champ role doit être une liste non vide")
        
        for role in v:
            if not role or not role.strip():
                raise ValueError("Chaque rôle doit avoir un ID valide")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": ["abc12345-e89b-12d3-a456-426614174001", "def67890-e89b-12d3-a456-426614174002"]
            }
        }

class AssignRoleResponse(BaseModel):
    """Réponse pour l'assignation de rôles"""
    success: str
    assigned_count: int
    roles: List[str]

class RoleInfo(BaseModel):
    """Information sur un rôle"""
    id: str
    name: str
    guard_name: str
    
    class Config:
        from_attributes = True

class UserRolesResponse(BaseModel):
    """Liste des rôles d'un utilisateur"""
    user_id: str
    roles: List[RoleInfo]

# ============================================================================
# MODÈLES SQLAlchemy
# ============================================================================

from sqlalchemy import Column, String, ForeignKey, Index, TIMESTAMP
from database import Base
from datetime import datetime



@router.post("/assign", response_model=AssignRoleResponse, status_code=200)
async def assign_role_to_user(
    request_data: AssignRoleRequest,
    db: Session = Depends(get_db)
):
    """
    Assigner des rôles à un utilisateur
    
    **Remplace** tous les rôles existants de l'utilisateur par les nouveaux
    
    **Exemple:**
```json
    {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "role": ["role1-uuid", "role2-uuid"]
    }
```
    
    Cette opération est équivalente à `syncRoles()` dans Laravel
    """
    
    try:
        user_id = request_data.user_id
        roles = request_data.role
        
        # ============================================================
        # VÉRIFICATION DE L'UTILISATEUR
        # ============================================================
        

        
        # ============================================================
        # VÉRIFICATION DES RÔLES
        # ============================================================
        

        
        # ============================================================
        # SUPPRESSION DES ANCIENS RÔLES (syncRoles)
        # ============================================================
        

        
        # ============================================================
        # AJOUT DES NOUVEAUX RÔLES
        # ============================================================
        

        
        logger.info(f"Rôles assignés à l'utilisateur {user_id}: {valid_roles}")
        
        return AssignRoleResponse(
            success="Le ou les rôles ont été assignés avec succès.",
            assigned_count=len(valid_roles),
            roles=valid_roles
        )
    



# ============================================================================
# ROUTER - VERSION REST (endpoints séparés - meilleure pratique)
# ============================================================================

@router.post("/users/{user_id}/assign", response_model=AssignRoleResponse)
async def assign_roles_to_user_rest(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    request_data: RoleList = ...,
    db: Session = Depends(get_db)
):
    """
    Assigner des rôles à un utilisateur (version RESTful)
    
    **Remplace** tous les rôles existants de l'utilisateur par les nouveaux
    
    **Exemple:**
```json
    {
        "role": ["role1-uuid", "role2-uuid", "role3-uuid"]
    }
```
    
    Cette opération est équivalente à `syncRoles()` dans Laravel
    """
    
    try:
        roles = request_data.role
        
        # Vérifier que l'utilisateur existe
        user_exists = db.query(
            select(User.id).where(User.id == user_id).exists()
        ).scalar()
        
        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail={"errors": {"user_id": ["Utilisateur introuvable."]}}
            )
        
        # Vérifier que tous les rôles existent
        valid_roles = []
        for role_id in roles:
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
            ModelHasRole.model_id == user_id,
            ModelHasRole.model_type == "App\\Models\\User"
        )
        db.execute(delete_stmt)
        
        # Ajouter les nouveaux rôles
        for role_id in valid_roles:
            new_role = ModelHasRole(
                role_id=role_id,
                model_type="App\\Models\\User",
                model_id=user_id
            )
            db.add(new_role)
        
        db.commit()
        
        logger.info(f"Rôles assignés à l'utilisateur {user_id}: {valid_roles}")
        
        return AssignRoleResponse(
            success="Le ou les rôles ont été assignés avec succès.",
            assigned_count=len(valid_roles),
            roles=valid_roles
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur dans assign_roles_to_user_rest: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


@router.get("/users/{user_id}", response_model=UserRolesResponse)
async def get_user_roles(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    db: Session = Depends(get_db)
):
    """
    Récupérer tous les rôles d'un utilisateur
    """
    
    try:
        # Vérifier que l'utilisateur existe
        user_exists = db.query(
            select(User.id).where(User.id == user_id).exists()
        ).scalar()
        
        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail={"errors": f"L'utilisateur {user_id} n'existe pas."}
            )
        
        # Récupérer les rôles
        query = (
            select(Role)
            .join(ModelHasRole, ModelHasRole.role_id == Role.id)
            .where(ModelHasRole.model_id == user_id)
            .where(ModelHasRole.model_type == "App\\Models\\User")
        )
        
        roles = db.execute(query).scalars().all()
        
        return UserRolesResponse(
            user_id=user_id,
            roles=[RoleInfo.model_validate(r) for r in roles]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur dans get_user_roles: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


@router.post("/users/{user_id}/add-role/{role_id}")
async def add_single_role_to_user(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    role_id: str = Path(..., description="ID du rôle à ajouter"),
    db: Session = Depends(get_db)
):
    """
    Ajouter un rôle supplémentaire à un utilisateur sans supprimer les existants
    
    Équivalent à `assignRole()` dans Laravel
    """
    
    try:
        # Vérifier que l'utilisateur existe
        user_exists = db.query(
            select(User.id).where(User.id == user_id).exists()
        ).scalar()
        
        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail={"errors": "Utilisateur introuvable."}
            )
        
        # Vérifier que le rôle existe
        role_exists = db.query(
            select(Role.id).where(Role.id == role_id).exists()
        ).scalar()
        
        if not role_exists:
            raise HTTPException(
                status_code=404,
                detail={"errors": f"Le rôle {role_id} n'existe pas."}
            )
        
        # Vérifier si le rôle est déjà assigné
        already_assigned = db.query(
            select(ModelHasRole.role_id).where(
                ModelHasRole.model_id == user_id,
                ModelHasRole.model_type == "App\\Models\\User",
                ModelHasRole.role_id == role_id
            ).exists()
        ).scalar()
        
        if already_assigned:
            return {"success": "Le rôle est déjà assigné à cet utilisateur."}
        
        # Ajouter le rôle
        new_role = ModelHasRole(
            role_id=role_id,
            model_type="App\\Models\\User",
            model_id=user_id
        )
        db.add(new_role)
        db.commit()
        
        logger.info(f"Rôle {role_id} ajouté à l'utilisateur {user_id}")
        
        return {"success": "Le rôle a été ajouté avec succès."}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur dans add_single_role_to_user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    role_id: str = Path(..., description="ID du rôle à retirer"),
    db: Session = Depends(get_db)
):
    """
    Retirer un rôle spécifique d'un utilisateur
    
    Équivalent à `removeRole()` dans Laravel
    """
    
    try:
        # Supprimer le rôle
        delete_stmt = delete(ModelHasRole).where(
            ModelHasRole.model_id == user_id,
            ModelHasRole.model_type == "App\\Models\\User",
            ModelHasRole.role_id == role_id
        )
        
        result = db.execute(delete_stmt)
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail={"errors": "Rôle non trouvé pour cet utilisateur"}
            )
        
        logger.info(f"Rôle {role_id} retiré de l'utilisateur {user_id}")
        
        return {"success": "Le rôle a été retiré avec succès."}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur dans remove_role_from_user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


@router.delete("/users/{user_id}/roles")
async def remove_all_roles_from_user(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    db: Session = Depends(get_db)
):
    """
    Retirer tous les rôles d'un utilisateur
    """
    
    try:
        # Vérifier que l'utilisateur existe
        user_exists = db.query(
            select(User.id).where(User.id == user_id).exists()
        ).scalar()
        
        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail={"errors": "Utilisateur introuvable."}
            )
        
        # Supprimer tous les rôles
        delete_stmt = delete(ModelHasRole).where(
            ModelHasRole.model_id == user_id,
            ModelHasRole.model_type == "App\\Models\\User"
        )
        
        result = db.execute(delete_stmt)
        db.commit()
        
        logger.info(f"Tous les rôles retirés de l'utilisateur {user_id} ({result.rowcount} rôles)")
        
        return {
            "success": "Tous les rôles ont été retirés avec succès.",
            "removed_count": result.rowcount
        }
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur dans remove_all_roles_from_user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


@router.get("/users/{user_id}/has-role/{role_name}")
async def check_user_has_role(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    role_name: str = Path(..., description="Nom du rôle"),
    db: Session = Depends(get_db)
):
    """
    Vérifier si un utilisateur a un rôle spécifique
    
    Équivalent à `hasRole()` dans Laravel
    """
    
    try:
        # Vérifier si l'utilisateur a le rôle
        has_role = db.query(
            select(ModelHasRole.role_id)
            .join(Role, Role.id == ModelHasRole.role_id)
            .where(ModelHasRole.model_id == user_id)
            .where(ModelHasRole.model_type == "App\\Models\\User")
            .where(Role.name == role_name)
            .exists()
        ).scalar()
        
        return {
            "user_id": user_id,
            "role_name": role_name,
            "has_role": has_role
        }
    
    except Exception as e:
        logger.error(f"Erreur dans check_user_has_role: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})