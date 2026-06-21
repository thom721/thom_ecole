from fastapi import APIRouter, Depends, HTTPException, Query,status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.database import get_db
from app.Models.MFinancials import FraisInscription
from app.Models.MModels import Niveau,AnneeAcademique,User
from app.Schemas.SInscription import PaginatedFraisInscriptionResponse, FraisInscriptionCreate,FraisInscriptionResponse,FraisInscriptionUpdate,FraisInscriptionResponseOne
from pydantic import BaseModel,validator,computed_field,field_validator
from app.Models.MFinancials import FraisDivers
import math
# from app.dependencies.Dependencie import check_permission,first_or_create,validate_exists,first_or_update_safe
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
import uuid
router = APIRouter(prefix="/api/v1", tags=["Frais d'Inscription"])

# GET paginé (16 par page comme ton Laravel)
@router.get("/fraisDinscription", response_model=PaginatedFraisInscriptionResponse)
def get_frais_inscriptions(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(16, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    # Query avec relations chargées
    query = (
        db.query(FraisInscription)
        .options(
            joinedload(FraisInscription.niveau),
            joinedload(FraisInscription.annee_academique)
        )
        .order_by(desc(FraisInscription.updated_at))
    )
    
    # Pagination
    total = query.count()
    skip = (page - 1) * per_page
    
    frais_inscriptions = query.offset(skip).limit(per_page).all()
    
    # Transformer en réponse
    data = []
    for frais in frais_inscriptions:
        data.append(FraisInscriptionResponse(
            id=frais.id,
            prix=frais.prix,
            niveau=frais.niveau.name if frais.niveau else None,
            annee_academique=frais.annee_academique.annee_academique if frais.annee_academique else None,
            niveau_id=frais.niveau_id,
            anneeAc=frais.anneeAc,
            created_at=frais.created_at,
            updated_at=frais.updated_at
        ))
    
    # Calculer la dernière page
    last_page = math.ceil(total / per_page) if total else 1
    
    return PaginatedFraisInscriptionResponse(
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
@router.get("/fraisDinscription/{frais_id}", response_model=FraisInscriptionResponseOne)
def get_frais_inscription(frais_id: str, db: Session = Depends(get_db)):
    frais = (
        db.query(FraisInscription)
        .options(
            joinedload(FraisInscription.niveau),
            joinedload(FraisInscription.annee_academique)
        )
        .filter(FraisInscription.id == frais_id)
        .first()
    )
    
    if not frais:
        raise HTTPException(status_code=404, detail="Frais d'inscription non trouvé")
    
    return FraisInscriptionResponseOne(data={
        "id":frais.id,
        "prix":frais.prix,
        "niveau":frais.niveau.name if frais.niveau else None,
        "annee_academique":frais.annee_academique.annee_academique if frais.annee_academique else None,
        "niveau_id":frais.niveau_id,
        "anneeAc":frais.anneeAc,
        "created_at":frais.created_at,
        "updated_at":frais.updated_at
    }
    )

# POST créer
# @router.post("/", response_model=FraisInscriptionResponse, status_code=201)
# def create_frais_inscription(
#     frais: FraisInscriptionCreate,
#     db: Session = Depends(get_db)
# ):
#     # Vérifier que le niveau existe
#     niveau = db.query(Niveau).filter(Niveau.id == frais.niveau_id).first()
#     if not niveau:
#         raise HTTPException(status_code=404, detail="Niveau non trouvé")
    
#     # Vérifier que l'année académique existe
#     annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == frais.anneeAc).first()
#     if not annee:
#         raise HTTPException(status_code=404, detail="Année académique non trouvée")
    
#     # Vérifier s'il existe déjà un frais pour ce niveau et cette année
#     existing = db.query(FraisInscription).filter(
#         FraisInscription.niveau_id == frais.niveau_id,
#         FraisInscription.anneeAc == frais.anneeAc
#     ).first()
    
#     if existing:
#         raise HTTPException(
#             status_code=400,
#             detail="Des frais d'inscription existent déjà pour ce niveau et cette année académique"
#         )
    
#     # Créer
#     db_frais = FraisInscription(**frais.model_dump())
    
#     db.add(db_frais)
#     db.commit()
#     db.refresh(db_frais)
    
#     return get_frais_inscription(db_frais.id, db)


class FraisInscriptionIn(BaseModel):
    id: str | None = None
    prix: float
    anneeAc: str
    niveau_id: str

    @validator('niveau_id')
    def validate_niveau_id(cls, v):
        # Vérifier le format UUID
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("niveau_id doit être un UUID valide")

    @field_validator("prix")
    @classmethod
    def prix_superieur_a_zero(cls, v):
        if v <= 0:
            raise ValueError("Le prix doit être supérieur à 0")
        return v
            

    @validator('anneeAc')
    def validate_anneeAc(cls, v):
        # Vérifier le format UUID
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Annee academique doit être un UUID valide")

@router.post("/fraisDinscription")
def store_frais_inscription(data: FraisInscriptionIn, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):

    validate_exists(Niveau, Niveau.id, db, data.niveau_id)
    validate_exists(AnneeAcademique, AnneeAcademique.id, db, data.anneeAc)

    try:
        if data.id:
            frais = db.query(FraisInscription).filter_by(id=data.id).first()
            if not frais:
                raise HTTPException(404, "Frais introuvable")

            existing = db.query(FraisInscription).filter(
                FraisInscription.niveau_id == data.niveau_id,
                FraisInscription.anneeAc == data.anneeAc,
                FraisInscription.id != data.id,
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Un frais d'inscription existe déjà pour ce niveau et cette année académique"
                ) 

            frais = first_or_update_safe(
                db,
                FraisInscription,
                search={
                    "niveau_id": data.niveau_id,
                    "anneeAc": data.anneeAc
                },
                data={
                    "prix": data.prix,
                    "niveau_id": data.niveau_id,
                    "anneeAc": data.anneeAc
                }
            )
            db.refresh(frais)
            return {"success": True, "id": frais.id}
        else:
            existing = db.query(FraisInscription).filter(
                FraisInscription.niveau_id == data.niveau_id,
                FraisInscription.anneeAc == data.anneeAc
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Un frais d'inscription existe déjà pour ce niveau et cette année académique"
                ) 
            frais = first_or_update_safe(
                db,
                FraisInscription,
                search={
                    "niveau_id": data.niveau_id,
                    "anneeAc": data.anneeAc
                },
                data={
                    "prix": data.prix
                }
            )

            db.refresh(frais)
            return {"success": True, "id": frais.id}
    except InterruptedError as e:
        db.rollback()
        # Analyser l'erreur pour donner un message plus précis
        error_msg = str(e.orig)
        if "niveau_id" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le niveau avec l'ID {frais.niveau_id} n'existe pas dans la base de données"
            )
        elif "anneeAc" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"L'année académique avec l'ID {frais.anneeAc} n'existe pas"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erreur de contrainte d'intégrité dans la base de données"
            )
            
    except HTTPException:
        raise
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {str(e)}"
        )


# PUT mettre à jour
@router.put("frais/{frais_id}", response_model=FraisInscriptionResponse)
def update_frais_inscription(
    frais_id: str,
    frais: FraisInscriptionUpdate,
    db: Session = Depends(get_db)
):
    # Trouver
    db_frais = db.query(FraisInscription).filter(
        FraisInscription.id == frais_id
    ).first()
    
    if not db_frais:
        raise HTTPException(status_code=404, detail="Frais d'inscription non trouvé")
    
    # Vérifier niveau si modifié
    if frais.niveau_id:
        niveau = db.query(Niveau).filter(Niveau.id == frais.niveau_id).first()
        if not niveau:
            raise HTTPException(status_code=404, detail="Niveau non trouvé")
    
    # Vérifier année académique si modifiée
    if frais.anneeAc:
        annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == frais.anneeAc).first()
        if not annee:
            raise HTTPException(status_code=404, detail="Année académique non trouvée")
    
    # Vérifier unicité si niveau ou année modifié
    if (frais.niveau_id or frais.anneeAc):
        niveau_id = frais.niveau_id or db_frais.niveau_id
        annee_id = frais.anneeAc or db_frais.anneeAc
        
        existing = db.query(FraisInscription).filter(
            FraisInscription.niveau_id == niveau_id,
            FraisInscription.anneeAc == annee_id,
            FraisInscription.id != frais_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Des frais d'inscription existent déjà pour cette combinaison niveau/année"
            )
    
    # Mettre à jour
    update_data = frais.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_frais, field, value)
    
    db.commit()
    db.refresh(db_frais)
    
    return get_frais_inscription(db_frais.id, db)

# DELETE
@router.delete("delete-frais/{frais}")
def delete_frais_inscription(frais: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    frais = db.query(FraisInscription).filter(
        FraisInscription.id == frais
    ).first()
    
    if not frais:
        raise HTTPException(status_code=404, detail="Frais d'inscription non trouvé")
    
    db.delete(frais)
    db.commit()
    
    return None

class FraisDiversIn(BaseModel):
    id: str | None = None
    description: str
    prix: float
    anneeAc: str
    niveau_id: str


@router.post("/frais-divers-store")
def store_frais_divers(data: FraisDiversIn, db: Session = Depends(get_db)):

    if data.id:
        frais = db.query(FraisDivers).filter_by(id=data.id).first()
        if not frais:
            raise HTTPException(404)

        frais.description = data.description
        frais.prix = data.prix
        frais.anneeAc = data.anneeAc
        frais.niveau_id = data.niveau_id

    else:
        frais = first_or_create(
            db,
            FraisDivers,
            search={
                "niveau_id": data.niveau_id,
                "anneeAc": data.anneeAc
            },
            create={
                "description": data.description,
                "prix": data.prix
            }
        )

    db.commit()
    return {"success": True}

@router.get("/frais-divers-index", response_model=PaginatedFraisInscriptionResponse)
def get_frais_divers(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(16, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    # Query avec relations chargées
    query = (
        db.query(FraisDivers)
        .options(
            joinedload(FraisDivers.niveau),
            joinedload(FraisDivers.annee_academique)
        )
        .order_by(desc(FraisDivers.updated_at))
    )
    
    # Pagination
    total = query.count()
    skip = (page - 1) * per_page
    
    frais_divers = query.offset(skip).limit(per_page).all()
    
    # Transformer en réponse
    data = []
    for frais in frais_divers:
        data.append(FraisInscriptionResponse(
            id=frais.id,
            prix=frais.prix,
            niveau=frais.niveau.name if frais.niveau else None,
            annee_academique=frais.annee_academique.annee_academique if frais.annee_academique else None,
            niveau_id=frais.niveau_id,
            anneeAc=frais.anneeAc,
            created_at=frais.created_at,
            updated_at=frais.updated_at
        ))
    
    # Calculer la dernière page
    last_page = math.ceil(total / per_page) if total else 1
    
    return PaginatedFraisInscriptionResponse(
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

@router.get("/show-frais-divers/{fraisDivers}", response_model=FraisInscriptionResponseOne)
def get_frais_inscription(fraisDivers: str, db: Session = Depends(get_db)):
    frais = (
        db.query(FraisDivers)
        .options(
            joinedload(FraisDivers.niveau),
            joinedload(FraisDivers.annee_academique)
        )
        .filter(FraisDivers.id == fraisDivers)
        .first()
    )
    
    if not frais:
        raise HTTPException(status_code=404, detail="Frais d'inscription non trouvé")
    
    return FraisInscriptionResponseOne(data={
        "id":frais.id,
        "prix":frais.prix,
        "niveau":frais.niveau.name if frais.niveau else None,
        "annee_academique":frais.annee_academique.annee_academique if frais.annee_academique else None,
        "niveau_id":frais.niveau_id,
        "anneeAc":frais.anneeAc,
        "created_at":frais.created_at,
        "updated_at":frais.updated_at
    }
    )

@router.delete("delete-frais_divers/{frais_divers}")
def delete_frais_inscription(frais_divers: str, db: Session = Depends(get_db)):
    frais_divers = db.query(FraisDivers).filter(
        FraisDivers.id == frais_divers
    ).first()
    
    if not frais_divers:
        raise HTTPException(status_code=404, detail="Frais divers non trouvé")
    
    db.delete(frais_divers)
    db.commit()
    
    return None