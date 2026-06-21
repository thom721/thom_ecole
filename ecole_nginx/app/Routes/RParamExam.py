from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List,Optional
from app.database import get_db
from app.Models.MFinancials import ParamExam
from app.Models.MModels import Niveau,AnneeAcademique,User
from app.Schemas.ParamExam import PaginatedResponse,ParamExamResponse,ParamExamCreate,ParamExamUpdate,ParamExamResponseOne
import math
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
from pydantic import BaseModel,Field

router = APIRouter(prefix="/api/v1", tags=["Params Exams"])

# GET paginé (comme ton Laravel)
@router.get("/paramsExam", response_model=PaginatedResponse)
def get_params_exams(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    # Compter le total
    total = db.query(ParamExam).join(
        Niveau, ParamExam.niveau_id == Niveau.id
    ).filter(
        Niveau.status == 1
    ).count()
    
    # Calculer skip
    skip = (page - 1) * per_page
    
    # Requête avec joins
    query_result = (
        db.query(
            ParamExam.id.label("examId"),
            AnneeAcademique.annee_academique.label("annee_academique"),
            Niveau.name.label("name"),
            ParamExam.evaluation_par,
            ParamExam.created_at,
            ParamExam.updated_at,
            ParamExam.annee_academique_id,
            ParamExam.niveau_id
        )
        .join(AnneeAcademique, ParamExam.annee_academique_id == AnneeAcademique.id)
        .join(Niveau, ParamExam.niveau_id == Niveau.id)
        .filter(Niveau.status == 1)
        .order_by(desc(ParamExam.updated_at))
        .offset(skip)
        .limit(per_page)
        .all()
    )
    
    # CONVERTIR les Rows en dict
    params_exams = []
    for row in query_result:
        params_exams.append({
            "id": row.examId,  # examId → id
            "name": row.name,
            "niveau_id": row.niveau_id,
            "evaluation_par": row.evaluation_par,
            "annee_academique": row.annee_academique,
            "annee_academique_id": row.annee_academique_id,
            "created_at": row.created_at,
            "updated_at": row.updated_at
        })
    
    # Calculer la dernière page
    last_page = math.ceil(total / per_page) if total else 1
    
    return PaginatedResponse(
        data=params_exams,
        meta={
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if params_exams else 0,
            "to": skip + len(params_exams) if params_exams else 0
        }
    )
# GET par ID
@router.get("/paramsExam/{exam_id}", response_model=ParamExamResponseOne)
def get_param_exam(exam_id: str, db: Session = Depends(get_db)):
    param_exam = (
        db.query(
            ParamExam.id,
            AnneeAcademique.annee_academique.label("annee_academique"),
            Niveau.name.label("name"),
            ParamExam.evaluation_par,
            ParamExam.created_at,
            ParamExam.updated_at,
            ParamExam.annee_academique_id,
            ParamExam.niveau_id
        )
        .join(AnneeAcademique, ParamExam.annee_academique_id == AnneeAcademique.id)
        .join(Niveau, ParamExam.niveau_id == Niveau.id)
        .filter(ParamExam.id == exam_id, Niveau.status == 1)
        .first()
    )
    if not param_exam:
        raise HTTPException(status_code=404, detail="Paramètre d'examen non trouvé")
    
    return ParamExamResponseOne(data=param_exam) 


class ParamsExamSchema(BaseModel):
    id: Optional[str] = None
    niveau_id: str
    annee_academique_id: str
    evaluation_par: str = Field(min_length=4)

@router.post("/paramsExam")
def store_params_exam(data: ParamsExamSchema, db: Session = Depends(get_db),current_user: User = Depends(check_permission("Ajouter parametre"))):
    validate_exists(Niveau, Niveau.id, db, data.niveau_id)
    validate_exists(AnneeAcademique, AnneeAcademique.id, db, data.annee_academique_id)
    try:
        # 🔹 Update si id fourni
        if data.id:
            exam = db.query(ParamExam).filter(ParamExam.id == data.id).first()
            if not exam:
                raise HTTPException(status_code=404, detail="Paramètre d'examen introuvable")

            existing = db.query(ParamExam).filter(
                ParamExam.niveau_id == data.niveau_id,
                ParamExam.annee_academique_id == data.annee_academique_id,
                ParamExam.id != data.id,
            ).first()
            if existing:
                raise HTTPException(status_code=404, detail="ce paramètre d'examen existe déjà pour ce niveau")
            
            # Mise à jour
            exam.niveau_id = data.niveau_id
            exam.annee_academique_id = data.annee_academique_id
            exam.evaluation_par = data.evaluation_par
            db.add(exam)
            db.commit()
            db.refresh(exam)
            return {"success": True, "id": exam.id}

        # 🔹 Create si n'existe pas
        else:
            # Vérifier unicité sur niveau_id + annee_academique_id
            existing = db.query(ParamExam).filter(
                ParamExam.niveau_id == data.niveau_id,
                ParamExam.annee_academique_id == data.annee_academique_id
            ).first()
            if existing:
                raise HTTPException(status_code=404, detail="ce paramètre d'examen existe déjà pour ce niveau")
                # return {"success": True, "id": existing.id}  # first_or_create équivalent

            new_exam = ParamExam(
                niveau_id=data.niveau_id,
                annee_academique_id=data.annee_academique_id,
                evaluation_par=data.evaluation_par
            )
            db.add(new_exam)
            db.commit()
            db.refresh(new_exam)
            return {"success": True, "id": new_exam.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# PUT mettre à jour
@router.put("/paramsExam/{exam_id}", response_model=ParamExamResponse)
def update_param_exam(
    exam_id: str, 
    param_exam: ParamExamUpdate, 
    db: Session = Depends(get_db)
):
    # Trouver le paramètre
    db_param_exam = db.query(ParamExam).filter(ParamExam.id == exam_id).first()
    
    if not db_param_exam:
        raise HTTPException(status_code=404, detail="Paramètre d'examen non trouvé")
    
    # Mettre à jour les champs fournis
    update_data = param_exam.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_param_exam, field, value)
    
    db.commit()
    db.refresh(db_param_exam)
    
    # Retourner avec les joins
    return get_param_exam(db_param_exam.id, db)

# DELETE
@router.delete("/delete-paramsExam/{exam}", status_code=204)
def delete_param_exam(exam: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    param_exam = db.query(ParamExam).filter(ParamExam.id == exam).first()
    
    if not param_exam:
        raise HTTPException(status_code=404, detail="Paramètre d'examen non trouvé")
    
    db.delete(param_exam)
    db.commit()
    
    return None