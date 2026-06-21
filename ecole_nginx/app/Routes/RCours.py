from fastapi import APIRouter, Depends, HTTPException, Query,status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc, desc, or_
from typing import Optional, List,Union
from app.Models.MModels import Niveau,User,Cours
from app.Models.MRelations import Programme
import math
from sqlalchemy import func
from datetime import datetime
from app.database import get_db  
from app.Schemas.cours_schema import (
    CoursCreate, 
    CoursUpdate, 
    CoursResponse, 
    PaginatedCoursResponse,CoursResponseSchemaOne,CoursesRequest,CourseUpdateRequest
)
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role
router = APIRouter(prefix="/api/v1", tags=["cours"])
 
# GET avec pagination optionnelle et recherche
@router.get("/cours", response_model=Union[List[CoursResponse], PaginatedCoursResponse])
def get_cours(
    page: Optional[int] = Query(None, ge=1, description="Page number (optionnel)"),
    per_page: int = Query(16, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Recherche sur cours_nom"),
    db: Session = Depends(get_db)
):
    # Query de base
    query = db.query(
        Cours.id,
        Cours.cours_nom,
        Cours.note_de_passage,
        Cours.coefficients,
        Cours.created_at,
        Cours.updated_at,
        Cours.niveau_id,
        Cours.type_matiere
    )
    
    # Recherche textuelle (comme ton Laravel)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Cours.cours_nom.ilike(search_pattern))
    
    # Order by (comme ton Laravel)
    query = query.order_by(asc(Cours.cours_nom)).order_by(asc(Cours.updated_at))
    
    # Si pas de pagination
    if page is None:
        results = query.all()
        
        data = []
        for row in results:
            data.append(CoursResponse(
                id=row.id,
                cours_nom=row.cours_nom,
                type_matiere=row.type_matiere,
                date=row.created_at,  # alias pour created_at
                note_de_passage=row.note_de_passage,
                coefficients=row.coefficients,
                niveau_id=row.niveau_id,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
        
        return data  # Retourne directement la liste
    
    # Avec pagination
    total = query.count()
    skip = (page - 1) * per_page
    
    results = query.offset(skip).limit(per_page).all()
    
    # Transformer les résultats
    data = []
    for row in results:
        data.append(CoursResponse(
            id=row.id,
            cours_nom=row.cours_nom,
            type_matiere=row.type_matiere,
            date=row.created_at,
            note_de_passage=row.note_de_passage,
            coefficients=row.coefficients,
            niveau_id=row.niveau_id,
            created_at=row.created_at,
            updated_at=row.updated_at
        ))
    
    # Calculer la dernière page
    last_page = math.ceil(total / per_page) if total else 1
    
    # Construire les query params
    query_params = {}
    if search:
        query_params["search"] = search
    
    return PaginatedCoursResponse(
        data=data,
        meta={
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if data else 0,
            "to": skip + len(data) if data else 0,
            "query_params": query_params
        }
    )

# GET par ID
@router.get("/cours/{cours_id}", response_model=CoursResponseSchemaOne)
def get_cours_by_id(cours_id: str, db: Session = Depends(get_db)):
    cours = (
        db.query(Cours)
        .options(joinedload(Cours.niveau))
        .filter(Cours.id == cours_id)
        .first()
    )
    
    if not cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    
    return CoursResponseSchemaOne(data={
        "id":cours.id,
        "cours_nom":cours.cours_nom,
        "type_matiere":cours.type_matiere,
        "date":cours.created_at,
        "note_de_passage":cours.note_de_passage,
        "coefficients":cours.coefficients,
        "niveau_id":cours.niveau_id,
        "created_at":cours.created_at,
        "updated_at":cours.updated_at
    }
    )

# POST créer
@router.post("/cours")
def store_cours(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
): 
    try:
        payload = CoursesRequest(**request)
        if "id" in request and request.get("id"):
            # payload = CourseUpdateRequest(**request)

            niveau = db.query(Niveau).filter(Niveau.id == payload.niveau_id).first()
            if not niveau:
                raise HTTPException(status_code=422, detail="Niveau invalide")

            if niveau.name == "Universitaire" and request.get("note_de_passage") is None:
                raise HTTPException(
                    status_code=422,
                    detail="Note de passage ne peut pas être vide"
                )

            if niveau.name != "Universitaire" and request.get("coefficients") is None:
                raise HTTPException(
                    status_code=422,
                    detail="Coefficient ne peut pas être vide"
                )

            user_has_permission(current_user, "Modifier cours",db)

            # existing_cours = db.query(Cours).filter(
            #         Cours.cours_nom == payload.cours_nom,
            #         Cours.id != payload.id
            #     ).first()
            
 
            existing_cours = db.query(Cours).filter(
                func.lower(Cours.cours_nom) == func.lower(payload.cours_nom),
                Cours.id != payload.id
            ).first()

            print(existing_cours.cours_nom,payload.cours_nom,existing_cours.id, payload.id)
            if existing_cours:
                print('existing_cours')
                raise HTTPException(
                    status_code=400,
                    detail=f"Le nom de cours '{payload.cours_nom}' est déjà utilisé par un autre cours."
                )

            # Update Programme lié
            db.query(Programme).filter(
                Programme.cours_id == payload.id
            ).update({
                "niveau_id": payload.niveau_id
            })


            # Update Cours
            db.query(Cours).filter(
                Cours.id == payload.id
            ).update({
                "cours_nom": payload.cours_nom,
                "niveau_id": payload.niveau_id,
                "type_matiere": payload.type_matiere,
            })

            db.commit()
            return {"success": "Cours mis à jour avec succès."}
        
        for item in payload.CoursesObject:
            niveau = db.query(Niveau).filter(Niveau.id == item.niveau_id).first()

            if not niveau:
                raise HTTPException(
                    status_code=422,
                    detail="Niveau invalide"
                )

            if niveau.name == "Universitaire" and not item.note_de_passage:
                raise HTTPException(
                    status_code=422,
                    detail="La note de passage est obligatoire pour le niveau universitaire."
                )
            
        for item in payload.CoursesObject:
            if item.id:
                if not user_has_permission(current_user, "Modifier cours", db):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Access denied"
                    )

                existing_cours = db.query(Cours).filter(
                func.lower(Cours.cours_nom) == func.lower(item.cours_nom),
                Cours.id != item.id
            ).first()
                # 
                if existing_cours:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Le nom de cours '{item.cours_nom}' est déjà utilisé par un autre cours."
                    )

                if not item.cours_nom:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Le nom de cours '{item.cours_nom}' est déjà utilisé par un autre cours."
                    )

                db.query(Cours).filter(
                    Cours.id == item.id
                ).update({
                    "cours_nom": item.cours_nom,
                    "niveau_id": item.niveau_id,
                    "note_de_passage": item.note_de_passage,
                    "coefficients": item.coefficients,
                    "type_matiere": item.type_matiere or "",
                })

            else: 
                if not user_has_permission(current_user, "Ajouter cours", db):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Access denied"
                    )


                existing_cours = db.query(Cours).filter(
                func.lower(Cours.cours_nom) == func.lower(item.cours_nom)
            ).first()

                if existing_cours:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Le nom de cours '{item.cours_nom}' est déjà utilisé par un autre cours."
                    )
                if not item.cours_nom:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Le nom de cours '{item.cours_nom}' est déjà utilisé par un autre cours."
                    )

                exists = db.query(Cours).filter(
                    Cours.cours_nom == item.cours_nom,
                    Cours.niveau_id == item.niveau_id
                ).first()

                if not exists:
                    cours = Cours(
                        cours_nom=item.cours_nom,
                        niveau_id=item.niveau_id,
                        note_de_passage=item.note_de_passage,
                        coefficients=item.coefficients,
                        type_matiere=item.type_matiere or "",
                    )
                    db.add(cours)
            db.commit()
        return {"success": "Cours ajoutés avec succès."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))



# PUT mettre à jour
@router.put("/cours/{cours_id}", response_model=CoursResponse)
def update_cours(
    cours_id: str,
    cours: CoursUpdate,
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    # Trouver
    db_cours = db.query(Cours).filter(Cours.id == cours_id).first()
    
    if not db_cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    
    # Vérifier unicité si cours_nom modifié
    if cours.cours_nom and cours.cours_nom != db_cours.cours_nom:
        existing = db.query(Cours).filter(
            Cours.cours_nom == cours.cours_nom,
            Cours.niveau_id == cours.niveau_id or db_cours.niveau_id,
            Cours.id != cours_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Un cours avec ce nom existe déjà pour ce niveau"
            )
    
    # Vérifier niveau si modifié
    if cours.niveau_id:
        niveau = db.query(Niveau).filter(Niveau.id == cours.niveau_id).first()
        if not niveau:
            raise HTTPException(status_code=404, detail="Niveau non trouvé")
    
    # Mettre à jour
    update_data = cours.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cours, field, value)
    
    db.commit()
    db.refresh(db_cours)
    
    return get_cours_by_id(db_cours.id, db)

# DELETE
@router.get("/delete-cours/{cours}", status_code=200)
def delete_cours(cours: str, db: Session = Depends(get_db),current_user: User =Depends(check_permission("Supprimer cours"))):
    # user_has_permission(current_user, "Supprimer cours",db)
    object_cours = db.query(Cours).filter(Cours.id == cours).first()
    if not object_cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    
    # Vérifier s'il y a des dépendances (programmes, notes)
    programmes_count = db.query(Programme).filter(Programme.Cours_id == cours).count()
#     notes_count = db.query(Note).filter(Note.cours_id == cours_id).count()
    
    if programmes_count > 0 :#or notes_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer ce cours car il est utilisé dans des programmes ou notes"
        )
    
    db.delete(object_cours)
    db.commit()
    return {"status": "success", "message": "Le cours a été supprimé avec succès"}
    return {"success": "Cours supprimer avec succès."}
    return None