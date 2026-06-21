from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.Models.MModels import AnneeAcademique,Niveau,User
from app.Schemas.SAnneeAcademique import PaginatedAnneeAcademiqueResponse,AnneeAcademiqueCreate,AnneeAcademiqueResponse,AnneeAcademiqueUpdate,AnneeAcademiqueResponseOne
from app.database import get_db
import math
from sqlalchemy.exc import IntegrityError
from pydantic import validator,root_validator
from pydantic import BaseModel
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List,Optional
from datetime import datetime 
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create
router = APIRouter(prefix="/api/v1", tags=["Année Académique"])

# GET paginé (5 par page comme ton Laravel)
@router.get("/anneeAcademique", response_model=PaginatedAnneeAcademiqueResponse)
def get_annee_academiques(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    # Compter le total
    total = db.query(AnneeAcademique).count()
    
    # Calculer skip
    skip = (page - 1) * per_page
    
    # Récupérer avec pagination
    annee_academiques = (
        db.query(AnneeAcademique)
        .order_by(desc(AnneeAcademique.updated_at))
        .offset(skip)
        .limit(per_page)
        .all()
    )
    
    # Transformer en réponse (Pydantic le fait automatiquement)
    data = [
        AnneeAcademiqueResponse.from_orm(aa)
        for aa in annee_academiques
    ]
    
    # Calculer la dernière page
    last_page = math.ceil(total / per_page) if total else 1
    
    return PaginatedAnneeAcademiqueResponse(
        data=data,
        meta={
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if data else 0,
            "to": skip + len(data) if data else 0
        }
    )

# GET par ID
@router.get("/anneeAcademique/{annee_id}", response_model=AnneeAcademiqueResponseOne)
def get_annee_academique(annee_id: str, db: Session = Depends(get_db)):
    annee_academique = (
        db.query(AnneeAcademique)
        .filter(AnneeAcademique.id == annee_id)
        .first()
    )
    
    if not annee_academique:
        raise HTTPException(status_code=404, detail="Année académique non trouvée")
    
    return AnneeAcademiqueResponseOne(data=annee_academique)
    # return AnneeAcademiqueResponse.from_orm(annee_academique)

# POST créer
class AnneeAcademiqueSchema(BaseModel):
    id: Optional[str] = None
    date_debut: datetime
    date_fin: datetime
    niveau_detude: Optional[str] = None
    annee_academique: Optional[str] = None
    status: bool

    @validator("date_fin")
    def check_dates(cls, v, values):
        if "date_debut" in values:
            date_debut = values["date_debut"]
            if relativedelta(v, date_debut).months + 12*relativedelta(v, date_debut).years < 9:
                raise ValueError("La période doit être d'au moins 9 mois")
        return v

@router.post("/anneeAcademique")
def store_annee_academique(data: AnneeAcademiqueSchema, db: Session = Depends(get_db),current_user: User = Depends(check_permission("Ajouter parametre"))):
    # 🔹 Construire le champ 'annee_academique'
    d1 = data.date_debut.year
    d2 = data.date_fin.year
    data.annee_academique = f"{d1}/{d2}"
    data.niveau_detude = "Cycle"

    try:
        # with db.begin():  # transaction
        # 🔹 Si status = 1, désactiver les autres
        if data.status:
            db.query(AnneeAcademique).filter(AnneeAcademique.status == True).update({"status": False})

        # 🔹 Update existant
        if data.id:
            annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == data.id).first()
            if not annee:
                raise HTTPException(status_code=404, detail="Année académique introuvable")

            exists = db.query(AnneeAcademique).filter(
            AnneeAcademique.annee_academique == data.annee_academique,
            AnneeAcademique.id != data.id
                ).first()
            if exists:
                raise HTTPException(status_code=422, detail="Cette année académique existe déjà")

            annee.date_debut = data.date_debut
            annee.date_fin = data.date_fin
            annee.niveau_detude = data.niveau_detude
            annee.annee_academique = data.annee_academique
            annee.status = data.status
            db.add(annee)

        # 🔹 Création si n'existe pas
        else:
            # Vérifier unicité sur annee_academique
            existing = db.query(AnneeAcademique).filter(
                AnneeAcademique.annee_academique == data.annee_academique
            ).first()
            if existing:
                raise HTTPException(status_code=422, detail="Cette année académique existe déjà")

            annee = AnneeAcademique(
                date_debut=data.date_debut,
                date_fin=data.date_fin,
                niveau_detude=data.niveau_detude,
                annee_academique=data.annee_academique,
                status=data.status
            )
            db.add(annee)

        db.commit()
        db.refresh(annee)
        return {"success": True, "id": annee.id}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Conflit de données")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# PUT mettre à jour
@router.put("anneeAcademique/{annee_id}", response_model=AnneeAcademiqueResponse)
def update_annee_academique(
    annee_id: str,
    annee: AnneeAcademiqueUpdate,
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    # Trouver
    db_annee = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == annee_id
    ).first()
    
    if not db_annee:
        raise HTTPException(status_code=404, detail="Année académique non trouvée")
    
    # Vérifier unicité si annee_academique est modifié
    if annee.annee_academique and annee.annee_academique != db_annee.annee_academique:
        existing = db.query(AnneeAcademique).filter(
            AnneeAcademique.annee_academique == annee.annee_academique,
            AnneeAcademique.id != annee_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Cette année académique existe déjà"
            )
    
    # Mettre à jour
    update_data = annee.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_annee, field, value)
    
    db.commit()
    db.refresh(db_annee)
    
    return AnneeAcademiqueResponse.from_orm(db_annee)

# DELETE
@router.delete("delete-anneeAcademique/{annee_id}", status_code=204)
def delete_annee_academique(annee_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    annee = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == annee_id
    ).first()
    
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique non trouvée")
    
    db.delete(annee)
    db.commit()
    
    return None