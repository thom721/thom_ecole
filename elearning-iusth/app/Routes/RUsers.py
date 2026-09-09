from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MUser import User, SystemRole
from app.Schemas.SUser import UserCreate, UserUpdate, UserOut
from app.dependencies.auth import hash_password, require_role

router = APIRouter(prefix="/users", tags=["users"])

# Recherche par email accessible aux professeurs (pas seulement aux admins) :
# nécessaire pour inscrire un étudiant à un cours (REnrollments.py attend un
# user_id, pas un email) sans donner accès au CRUD utilisateurs complet.
@router.get("/lookup", response_model=UserOut, dependencies=[Depends(require_role([SystemRole.teacher, SystemRole.admin]))])
def lookup_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun utilisateur avec cet email")
    return user


admin_router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_role([SystemRole.admin]))])


@admin_router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.last_name, User.first_name).all()


@admin_router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cet email est déjà utilisé")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        system_role=data.system_role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@admin_router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    return user


@admin_router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: str, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@admin_router.patch("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
