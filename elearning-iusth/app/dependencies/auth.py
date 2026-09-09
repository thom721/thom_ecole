from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config.Config import settings
from app.database import get_db
from app.Models.MUser import User, SystemRole
from app.Models.MEnrollment import Enrollment, CourseRole

security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.id, "system_role": user.system_role.value, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Compte désactivé")
    return current_user


def require_role(roles: list[SystemRole]):
    def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.system_role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle insuffisant")
        return current_user
    return _checker


def require_course_role(roles: list[CourseRole]):
    """Vérifie le rôle de l'utilisateur COURANT sur le cours identifié par le
    paramètre de route `course_id` (ou `id`, selon la route). system_role
    == admin passe toujours. Remplacement direct du RBAC polymorphique
    Laravel écarté (voir Models/MEnrollment.py)."""

    def _checker(
        course_id: str = Path(...),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.system_role == SystemRole.admin:
            return current_user

        enrollment = (
            db.query(Enrollment)
            .filter(Enrollment.course_id == course_id, Enrollment.user_id == current_user.id)
            .first()
        )
        if enrollment is None or enrollment.role_in_course not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle insuffisant sur ce cours")
        return current_user

    return _checker


def get_enrollment_or_none(db: Session, course_id: str, user_id: str) -> Enrollment | None:
    return (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id, Enrollment.user_id == user_id)
        .first()
    )


def assert_course_role(db: Session, current_user: User, course_id: str, roles: list[CourseRole]) -> None:
    """Même vérification que require_course_role, mais appelable directement
    depuis le corps d'une route une fois le course_id connu (cas des routes
    imbriquées comme /sections/{id} où le course_id n'est pas dans l'URL et
    doit d'abord être déduit de la ressource chargée)."""
    if current_user.system_role == SystemRole.admin:
        return
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    if enrollment is None or enrollment.role_in_course not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle insuffisant sur ce cours")
