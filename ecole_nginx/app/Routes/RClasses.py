from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from app.Models.MModels import Classe,Niveau,User
from typing import Optional,List,Union
from app.database import get_db
from app.Schemas.SClasse import ClasseCreate,ClasseResponse,ClasseUpdate,PaginatedClasseResponse,ClasseResponseOne
import math
from pydantic import Field
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["Classes"])

# GET avec pagination optionnelle
@router.get("/classes", response_model=Union[List[ClasseResponse], PaginatedClasseResponse])
def get_classes(
    request: Request,
    page: Optional[int] = Query(1, ge=1, description="Page number (optionnel)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    query = db.query(Classe).options(joinedload(Classe.niveau))
    
    # Si pas de pagination (comme ton Laravel)
    if page is None:
        classes = query.order_by(desc(Classe.updated_at)).all()
        
        # Transformer en réponse
        data = []
        for classe in classes:
            data.append({
                "id": classe.id,
                "niveau": classe.niveau.name if classe.niveau else None,
                "nom_classe": classe.nom_classe,
                "niveau_id": classe.niveau_id,
                "created_at": classe.created_at,
                "updated_at": classe.updated_at
            })
        
        return data  # Retourne directement la liste
    
    # Avec pagination
    total = query.count()
    skip = (page - 1) * per_page
    
    classes = (
        query.order_by(desc(Classe.updated_at))
        .offset(skip)
        .limit(per_page)
        .all()
    )
    
    # Transformer en réponse
    data = []
    for classe in classes:
        data.append({
            "id": classe.id,
            "niveau": classe.niveau.name if classe.niveau else None,
            "nom_classe": classe.nom_classe,
            "niveau_id": classe.niveau_id,
            "created_at": classe.created_at,
            "updated_at": classe.updated_at
        })
    
    last_page = math.ceil(total / per_page) if total else 1
    
    return PaginatedClasseResponse(
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
@router.get("/classes/{classe_id}", response_model=ClasseResponseOne)
def get_classe(classe_id: str, db: Session = Depends(get_db)):
    classe = (
        db.query(Classe)
        .options(joinedload(Classe.niveau))
        .filter(Classe.id == classe_id)
        .first()
    )
    
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    
    item = {
        "id": classe.id,
        "niveau": classe.niveau.name if classe.niveau else None,
        "nom_classe": classe.nom_classe,
        "niveau_id": classe.niveau_id,
        "created_at": classe.created_at,
        "updated_at": classe.updated_at
    }
    return ClasseResponseOne(data=item)

# POST créer

class ClasseSchema(BaseModel):
    id: str | None = None
    niveau_id: str
    faculte_id: str | None = None
    nom_classe: str = Field(min_length=3)


@router.post("/classes")
def store_classe(data: ClasseSchema, db: Session = Depends(get_db),current_user: User = Depends(check_permission("Ajouter parametre"))):

    # 🔹 Vérification existence niveau
    niveau = db.query(Niveau).filter(Niveau.id == data.niveau_id).first()
    if not niveau:
        raise HTTPException(status_code=404, detail="Niveau introuvable")
    
    if data.nom_classe in (None, ''):
        raise HTTPException(status_code=422, detail="Cette classe n'est pas valide")
    try:
        # 🔹 Début transaction
        # with db.begin():

        # Préparer les données pour l'update ou create
        update_data = {"nom_classe": data.nom_classe}

        # Cas UPDATE
        if data.id:
            classe = db.query(Classe).filter(Classe.id == data.id).first()
            if not classe:
                raise HTTPException(status_code=404, detail="Classe introuvable")

            exists = db.query(Classe).filter(
            Classe.nom_classe == data.nom_classe,
            Classe.id != data.id
                ).first()
            if exists:
                raise HTTPException(status_code=422, detail="Cette classe existe déjà pour ce niveau")

            # Si niveau universitaire, gérer faculté (logique spécifique)
            # if niveau.name == "Universitaire" and data.faculte_id:
            #     # ici on peut lier à la faculté si besoin
            #     update_data["faculte_id"] = data.faculte_id

            for key, value in update_data.items():
                setattr(classe, key, value)
            db.add(classe)

        # Cas CREATE
        else:
            # Vérifier unicité nom_classe + niveau_id
            existing = db.query(Classe).filter(
                Classe.nom_classe == data.nom_classe,
                Classe.niveau_id == data.niveau_id
            ).first()

            if existing:
                raise HTTPException(status_code=422, detail="Cette classe existe déjà pour ce niveau")

            classe = Classe(
                niveau_id=data.niveau_id,
                nom_classe=data.nom_classe
                # faculte_id=data.faculte_id if niveau.name == "Universitaire" else None
            )
            db.add(classe)

        db.commit()
        db.refresh(classe)
        return {"success": True, "id": classe.id}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Conflit de données")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

 
# DELETE
@router.delete("/delete-classe/{classe}", status_code=204)
def delete_classe(classe: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    classe = db.query(Classe).filter(Classe.id == classe).first()
    
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    
    # Vérifier s'il y a des dépendances
    # (optionnel, selon tes besoins)
        raise HTTPException(status_code=404, detail="Vous ne pouvez pas effectué cette action")
    db.delete(classe)
    db.commit()
    
    return None