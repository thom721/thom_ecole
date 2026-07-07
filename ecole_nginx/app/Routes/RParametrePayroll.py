from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.database import get_db
from app.Models.MModels import User, Cours, AnneeAcademique
from app.Models.MFinancials import ParametrePayroll
from app.Schemas.SParametrePayroll import (
    ParametrePayrollSchema,
    ParametrePayrollCreateSchema,
    ParametrePayrollUpdateSchema,
    ParametrePayrollListResponse,
)
from app.dependencies.Dependencie import get_current_user, user_has_permission
from app.Helper.context import UserContext, ActionContext

router = APIRouter(prefix="/api/v1", tags=["Paramètres Payroll"])


def _to_schema(p: ParametrePayroll, db: Session) -> ParametrePayrollSchema:
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == p.annee_academique).first()
    return ParametrePayrollSchema(
        id=p.id,
        cours_id=p.cours_id,
        cours_nom=p.cours.cours_nom if p.cours else "",
        taux_horaire=float(p.taux_horaire),
        annee_academique=p.annee_academique,
        annee_academique_label=annee.annee_academique if annee else "",
    )


@router.get("/parametre-payroll", response_model=ParametrePayrollListResponse)
def list_parametre_payroll(
    annee_academique: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(ParametrePayroll).options(joinedload(ParametrePayroll.cours))
    if annee_academique:
        query = query.filter(ParametrePayroll.annee_academique == annee_academique)
    rows = query.order_by(ParametrePayroll.annee_academique.desc()).all()
    return {"data": [_to_schema(p, db) for p in rows]}


@router.post("/parametre-payroll", response_model=ParametrePayrollSchema, status_code=201)
def store_parametre_payroll(
    data: ParametrePayrollCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Ajouter paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("create")

    cours = db.query(Cours).filter(Cours.id == data.cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == data.annee_academique).first()
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")

    existing = db.query(ParametrePayroll).filter(
        ParametrePayroll.cours_id == data.cours_id,
        ParametrePayroll.annee_academique == data.annee_academique,
    ).first()
    if existing:
        existing.taux_horaire = data.taux_horaire
        db.commit()
        db.refresh(existing)
        return _to_schema(existing, db)

    param = ParametrePayroll(
        cours_id=data.cours_id,
        taux_horaire=data.taux_horaire,
        annee_academique=data.annee_academique,
    )
    db.add(param)
    db.commit()
    db.refresh(param)
    return _to_schema(param, db)


@router.put("/parametre-payroll/{parametre_id}", response_model=ParametrePayrollSchema)
def update_parametre_payroll(
    parametre_id: str,
    data: ParametrePayrollUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Modifier paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("update")

    param = db.query(ParametrePayroll).filter(ParametrePayroll.id == parametre_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="Paramètre introuvable")

    param.taux_horaire = data.taux_horaire
    db.commit()
    db.refresh(param)
    return _to_schema(param, db)


@router.delete("/parametre-payroll/{parametre_id}")
def delete_parametre_payroll(
    parametre_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Supprimer paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("delete")

    param = db.query(ParametrePayroll).filter(ParametrePayroll.id == parametre_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="Paramètre introuvable")

    db.delete(param)
    db.commit()
    return {"success": "Opération réussie"}
