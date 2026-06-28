from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.Models.MModels import User
from app.Models.MFinancials import Payroll
from app.Schemas.SPayroll import PayrollSchema, PayrollCreateSchema, PaginatedPayrollResponse
from app.dependencies.Dependencie import get_current_user, user_has_permission
from app.Helper.context import UserContext, ActionContext

router = APIRouter(prefix="/api/v1", tags=["Payroll"])


@router.get("/payroll", response_model=PaginatedPayrollResponse)
def index_payroll(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Payroll).options(joinedload(Payroll.user)).order_by(Payroll.created_at.desc())

    total = query.count()
    skip = (page - 1) * per_page
    rows = query.offset(skip).limit(per_page).all()

    return {
        "data": [PayrollSchema.from_model(p) for p in rows],
        "meta": {
            "current_page": page,
            "last_page": (total + per_page - 1) // per_page if total else 1,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if rows else 0,
            "to": skip + len(rows) if rows else 0,
        },
    }


@router.post("/payroll", response_model=PayrollSchema, status_code=201)
def store_payroll(
    data: PayrollCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Ajouter paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to create payroll entry")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("create")

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employé introuvable")

    payroll = Payroll(
        user_id=data.user_id,
        montant=data.montant,
        mois=data.mois,
        annee=data.annee,
        methode_paiement=data.methode_paiement,
    )
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return PayrollSchema.from_model(payroll)


@router.post("/payroll/{payroll_id}/pay", response_model=PayrollSchema)
def pay_payroll(
    payroll_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Modifier paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to update payroll entry")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("update")

    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Versement introuvable")

    payroll.statut = "Payé"
    payroll.date_versement = datetime.utcnow()
    db.commit()
    db.refresh(payroll)
    return PayrollSchema.from_model(payroll)


@router.delete("/payroll/{payroll_id}")
def delete_payroll(
    payroll_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Supprimer paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to delete payroll entry")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("delete")

    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Versement introuvable")

    db.delete(payroll)
    db.commit()
    return {"success": "Opération réussie"}
