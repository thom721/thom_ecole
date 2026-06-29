from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.Models.MSystems import Profile
from app.Schemas.SProfile import ProfileCreate, ProfileUpdate, ProfileOut,ShowProfile
import base64
import os 
from app.Models.MModels import User
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
from sqlalchemy.orm import Session
from app.Helper.persistent_storage import LOGO_DIR
UPLOAD_DIR = str(LOGO_DIR)
# from app.utils import generate_uuid  # si tu as une fonction utils pour UUID

router = APIRouter(prefix="/api/v1", tags=["Profiles"])

# 🔹 Lister tous les profils
@router.get("/get-profile", response_model=ShowProfile)
def get_profiles(db: Session = Depends(get_db)):
    profiles = db.query(Profile).first()
    return ShowProfile(data=profiles)

# 🔹 Récupérer un profil par ID
@router.get("/profile/{profile_id}", response_model=ProfileOut)
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# 🔹 Mettre à jour un profil
@router.put("update/{profile_id}", response_model=ProfileOut)
def update_profile(profile_id: str, profile_in: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    for key, value in profile_in.dict(exclude_unset=True).items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile

# 🔹 Supprimer un profil
@router.delete("/profile/{profile_id}")
def delete_profile(profile_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"success": True, "message": "Profile deleted"}

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class ProfileCreate(BaseModel):
    id: Optional[str] = None
    nom: str
    email: EmailStr
    ligne1: str = Field(..., pattern=r'^[\d\s()+-]+$')
    ligne2: Optional[str] = Field(None, pattern=r'^[\d\s()+-]+$')
    adresse: str
    logo_image_path: Optional[str] = None # Sera utilisé pour le Base64 ou le chemin
    logo_image_base64: Optional[str] = None # Sera utilisé pour le Base64 ou le chemin

@router.post("/profile")
async def store_profile(data: ProfileCreate, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    # 1. Logique d'autorisation (Équivalent AuthorizationHelper)
    if data.id:
        # Simulation: check_permission(request, 'Modifier profile')
        action = "update"
    else:
        # Simulation: check_permission(request, 'Ajouter profile')
        action = "create"
    if not user_has_permission(current_user, "Modifier profile", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé à ajouter un programme"
        )
    try:
        # 2. Récupérer le premier profil (Laravel Profile::first())
        db_profile = db.query(Profile).first()
        
        logo_path = None
        # 3. Gestion de l'image (Base64)
        if data.logo_image_path and "base64," in data.logo_image_path:
            # Décoder l'image
            header, encoded = data.logo_image_path.split(",", 1)
            image_data = base64.b64decode(encoded)
            
            # Supprimer l'ancien logo si nécessaire
            if db_profile and db_profile.logo_image_path:
                old_path = os.path.join(UPLOAD_DIR, os.path.basename(db_profile.logo_image_path))
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Sauvegarder le nouveau
            file_name = "school_logo.png"
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            with open(f"{UPLOAD_DIR}/{file_name}", "wb") as f:
                f.write(image_data)
            logo_path = f"logo/{file_name}"

        # 4. Update ou Create
        if db_profile:
            # Mise à jour des champs
            db_profile.nom = data.nom
            db_profile.email = data.email
            db_profile.ligne1 = data.ligne1
            db_profile.ligne2 = data.ligne2
            db_profile.adresse = data.adresse
            db_profile.is_receive_arriere = bool(getattr(data, 'is_receive_arriere', False))
            if logo_path:
                # data.logo_image_path EST déjà le data-URI base64 complet
                # ("data:image/png;base64,...") envoyé par le web ET le
                # bureau — aucun des deux clients ne renseigne jamais le
                # champ séparé data.logo_image_base64 (toujours None), donc
                # s'appuyer sur lui ici écrasait le logo affiché dans tous
                # les PDF (qui lisent info.logo_image_base64) à chaque
                # changement de logo, sur web comme sur bureau.
                db_profile.logo_image_path = logo_path
                db_profile.logo_image_base64 = data.logo_image_path

            db.commit()
            db.refresh(db_profile)
            final_data = db_profile
        else:
            # Création (firstOrCreate)
            new_profile = Profile(
                nom=data.nom,
                email=data.email,
                ligne1=data.ligne1,
                ligne2=data.ligne2,
                adresse=data.adresse,
                logo_image_path=logo_path,
                logo_image_base64=data.logo_image_path if logo_path else data.logo_image_base64,
                is_receive_arriere=bool(getattr(data, 'is_receive_arriere', False)),
            )
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            final_data = new_profile

        return {
            "success": True,
            "message": "Opération réussie !",
            "data": final_data
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
