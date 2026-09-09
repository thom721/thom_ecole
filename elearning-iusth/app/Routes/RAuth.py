import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.Config import settings
from app.database import get_db
from app.Helper.email import send_password_reset_email
from app.Models.MPasswordReset import PasswordResetToken
from app.Models.MUser import User, SystemRole
from app.Schemas.SAuth import (
    RegisterRequest, LoginRequest, TokenResponse, ChangePasswordRequest,
    ForgotPasswordRequest, ResetPasswordRequest, MessageResponse,
)
from app.Schemas.SUser import UserOut
from app.dependencies.auth import hash_password, verify_password, create_access_token, get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Réponse générique, identique que l'email corresponde à un compte ou non
# (n'expose jamais quels emails existent en base).
_FORGOT_PASSWORD_GENERIC_MESSAGE = (
    "Si un compte existe avec cet email, un lien de réinitialisation vient de lui être envoyé."
)
_RESET_TOKEN_LIFETIME = timedelta(hours=1)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Auto-inscription : toujours system_role=student. Les comptes
    professeur/admin sont créés par un admin via /users (voir RUsers.py)."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cet email est déjà utilisé")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        system_role=SystemRole.student,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte désactivé")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(user)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/change-password", response_model=UserOut)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mot de passe actuel incorrect")

    current_user.password_hash = hash_password(data.new_password)
    current_user.must_change_password = False
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user is not None:
        token = secrets.token_urlsafe(32)
        db.add(PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(timezone.utc) + _RESET_TOKEN_LIFETIME,
        ))
        db.commit()
        reset_link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"
        send_password_reset_email(user.email, user.first_name, reset_link)
    return MessageResponse(message=_FORGOT_PASSWORD_GENERIC_MESSAGE)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == data.token).first()
    now = datetime.now(timezone.utc)
    if (
        reset_token is None
        or reset_token.used_at is not None
        or reset_token.expires_at.replace(tzinfo=timezone.utc) < now
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien de réinitialisation invalide ou expiré")

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    reset_token.used_at = now
    db.commit()
    return MessageResponse(message="Mot de passe réinitialisé avec succès")
