from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MPermission import Permission, Role, RolePermission, UserRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SPermission import (
    PermissionOut, RoleCreate, RoleUpdate, RoleOut, UserRoleCreate, UserRoleOut,
)
from app.dependencies.auth import require_role

router = APIRouter(tags=["permissions"], dependencies=[Depends(require_role([SystemRole.admin]))])


def _role_out(db: Session, role: Role) -> RoleOut:
    names = [
        p.name for p in
        db.query(Permission).join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id == role.id).all()
    ]
    return RoleOut(id=role.id, name=role.name, description=role.description, permission_names=names)


def _validate_permission_names(db: Session, names: list[str]) -> list[Permission]:
    permissions = db.query(Permission).filter(Permission.name.in_(names)).all()
    found_names = {p.name for p in permissions}
    unknown = set(names) - found_names
    if unknown:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Permissions inconnues : {', '.join(unknown)}")
    return permissions


@router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(db: Session = Depends(get_db)):
    return db.query(Permission).order_by(Permission.name).all()


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return [_role_out(db, r) for r in db.query(Role).order_by(Role.name).all()]


@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(data: RoleCreate, db: Session = Depends(get_db)):
    if db.query(Role).filter(Role.name == data.name).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Un rôle avec ce nom existe déjà")
    permissions = _validate_permission_names(db, data.permission_names)

    role = Role(name=data.name, description=data.description)
    db.add(role)
    db.flush()
    for permission in permissions:
        db.add(RolePermission(role_id=role.id, permission_id=permission.id))
    db.commit()
    db.refresh(role)
    return _role_out(db, role)


def _get_role_or_404(db: Session, role_id: str) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rôle introuvable")
    return role


@router.patch("/roles/{role_id}", response_model=RoleOut)
def update_role(role_id: str, data: RoleUpdate, db: Session = Depends(get_db)):
    role = _get_role_or_404(db, role_id)
    if data.name is not None:
        role.name = data.name
    if data.description is not None:
        role.description = data.description
    if data.permission_names is not None:
        permissions = _validate_permission_names(db, data.permission_names)
        db.query(RolePermission).filter(RolePermission.role_id == role.id).delete()
        for permission in permissions:
            db.add(RolePermission(role_id=role.id, permission_id=permission.id))
    db.commit()
    db.refresh(role)
    return _role_out(db, role)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: str, db: Session = Depends(get_db)):
    role = _get_role_or_404(db, role_id)
    if db.query(UserRole).filter(UserRole.role_id == role_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce rôle est attribué à au moins un compte — retirez d'abord ces attributions")
    db.delete(role)
    db.commit()


@router.get("/users/{user_id}/roles", response_model=list[UserRoleOut])
def list_user_roles(user_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(UserRole, Role)
        .join(Role, Role.id == UserRole.role_id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return [UserRoleOut(id=ur.id, user_id=ur.user_id, role_id=ur.role_id, role_name=role.name) for ur, role in rows]


@router.post("/users/{user_id}/roles", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
def assign_role(user_id: str, data: UserRoleCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    if user.system_role != SystemRole.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seul un compte admin peut recevoir un rôle de permission")
    role = _get_role_or_404(db, data.role_id)
    if db.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == data.role_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce rôle est déjà attribué à ce compte")

    user_role = UserRole(user_id=user_id, role_id=data.role_id)
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return UserRoleOut(id=user_role.id, user_id=user_role.user_id, role_id=user_role.role_id, role_name=role.name)


@router.delete("/user-roles/{user_role_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_role(user_role_id: str, db: Session = Depends(get_db)):
    user_role = db.query(UserRole).filter(UserRole.id == user_role_id).first()
    if user_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribution introuvable")
    db.delete(user_role)
    db.commit()
