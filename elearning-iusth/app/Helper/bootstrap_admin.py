from sqlalchemy.orm import Session

from app.config.Config import settings
from app.Models.MPermission import Permission, Role, RolePermission, UserRole
from app.Models.MUser import User, SystemRole
from app.Helper.permissions import PERMISSION_CATALOG
from app.dependencies.auth import hash_password


def ensure_bootstrap_admin(db: Session) -> None:
    """Crée le tout premier compte admin, avec un rôle regroupant TOUTES
    les permissions du catalogue — nécessaire pour sortir de l'impasse
    "un admin doit déjà exister pour en créer un autre" (POST /users et
    la gestion des rôles, RPermissions.py, sont tous les deux réservés
    système_role=admin). Désactivé par défaut (BOOTSTRAP_ADMIN_EMAIL
    vide) — n'agit que si explicitement configuré en .env, et seulement
    si aucun admin n'existe déjà (jamais de recréation/écrasement d'un
    compte déjà présent, même principe que partout ailleurs dans ce
    projet)."""
    if not settings.BOOTSTRAP_ADMIN_EMAIL or not settings.BOOTSTRAP_ADMIN_PASSWORD:
        return
    if db.query(User).filter(User.system_role == SystemRole.admin).first() is not None:
        return

    user = User(
        email=settings.BOOTSTRAP_ADMIN_EMAIL,
        password_hash=hash_password(settings.BOOTSTRAP_ADMIN_PASSWORD),
        first_name="Admin",
        last_name="Principal",
        system_role=SystemRole.admin,
        must_change_password=False,
    )
    db.add(user)
    db.flush()

    role = db.query(Role).filter(Role.name == "Super Admin").first()
    if role is None:
        role = Role(name="Super Admin", description="Toutes les permissions — assignée automatiquement au premier compte admin")
        db.add(role)
        db.flush()

    existing_permission_ids = {
        rp.permission_id for rp in db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
    }
    for name in PERMISSION_CATALOG:
        permission = db.query(Permission).filter(Permission.name == name).first()
        if permission is not None and permission.id not in existing_permission_ids:
            db.add(RolePermission(role_id=role.id, permission_id=permission.id))

    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()

    print(f"[bootstrap_admin] Premier compte admin créé : {settings.BOOTSTRAP_ADMIN_EMAIL} (rôle Super Admin, toutes permissions)")
