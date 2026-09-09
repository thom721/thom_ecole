from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MPermission import Permission, Role, RolePermission, UserRole
from app.Models.MUser import User, SystemRole
from app.dependencies.auth import get_current_active_user

# Catalogue défini dans le code, jamais en libre saisie admin (voir plan
# Épic 21) — une permission mal orthographiée dans un formulaire libre ne
# correspondrait plus jamais à aucune vérification réelle, silencieusement.
PERMISSION_CATALOG = ["start_staff_meetings"]


def ensure_permissions_seeded(db: Session) -> None:
    """Upsert idempotent du catalogue — appelé une fois au démarrage de
    l'app (voir main.py, évènement startup)."""
    existing = {p.name for p in db.query(Permission).all()}
    for name in PERMISSION_CATALOG:
        if name not in existing:
            db.add(Permission(name=name))
    db.commit()


def user_has_permission(db: Session, user: User, permission_name: str) -> bool:
    if user.system_role != SystemRole.admin:
        return False
    match = (
        db.query(UserRole)
        .join(Role, Role.id == UserRole.role_id)
        .join(RolePermission, RolePermission.role_id == Role.id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .filter(UserRole.user_id == user.id, Permission.name == permission_name)
        .first()
    )
    return match is not None


def require_permission(permission_name: str):
    def _checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not user_has_permission(db, current_user, permission_name):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission insuffisante")
        return current_user
    return _checker
