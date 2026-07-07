from datetime import datetime, date
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field, model_validator
from app.database import get_db
from app.Models.MModels import User, Professeur
from app.Models.MSystems import Personnel, Profile
from app.Models.MFinancials import Payroll
from app.Helper.pdf_personaliser import PDFGenerator
from app.dependencies.Dependencie import check_permission

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()


class PayrollReportType(str, Enum):
    GLOBAL = "Global"
    PROFESSEUR = "Professeur"
    PERSONNEL = "Personnel"


class PrintPayrollReportRequest(BaseModel):
    date_debut: date = Field(..., description="Date de début")
    date_fin: date = Field(..., description="Date de fin")
    type: PayrollReportType = Field(..., description="Global, Professeur ou Personnel")

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.date_debut > self.date_fin:
            raise ValueError("La date de début doit être avant ou égale à la date de fin")
        return self


@router.post("/print-payroll-report")
def print_payroll_report(
    request: PrintPayrollReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Imprimer rapport")),
):
    """Rapport Payroll pour une intervalle de dates arbitraire (filtre sur
    Payroll.created_at, même convention que les autres rapports —
    GlobalRepport.py : Depense/Loan/OtherTransaction.created_at.between()).
    'type' restreint aux professeurs, au personnel (tous les employés qui
    ne sont pas professeurs), ou aux deux (Global)."""
    date_debut = datetime.combine(request.date_debut, datetime.min.time())
    date_fin = datetime.combine(request.date_fin, datetime.max.time())

    payrolls = db.query(Payroll).options(joinedload(Payroll.user)).filter(
        Payroll.created_at.between(date_debut, date_fin)
    ).order_by(Payroll.created_at.asc()).all()

    rows = []
    total_du = 0.0
    total_verse = 0.0
    total_solde = 0.0

    for p in payrolls:
        if not p.user:
            continue
        is_professeur = p.user.userable_type == "App\\Models\\Professeur"
        is_personnel = p.user.userable_type == "App\\Models\\Personnel"

        if request.type == PayrollReportType.PROFESSEUR and not is_professeur:
            continue
        if request.type == PayrollReportType.PERSONNEL and not is_personnel:
            continue
        if not is_professeur and not is_personnel:
            continue

        if is_professeur:
            employe = db.query(Professeur).filter(Professeur.id == p.user.userable_id).first()
            type_label = "Professeur"
        else:
            employe = db.query(Personnel).filter(Personnel.id == p.user.userable_id).first()
            type_label = "Personnel"

        if not employe:
            continue

        montant_du = float(p.montant_du) if p.montant_du is not None else float(p.montant)
        remaining = float(p.remaining_balance) if p.remaining_balance is not None else 0.0
        montant_verse = montant_du - remaining

        total_du += montant_du
        total_verse += montant_verse
        total_solde += remaining

        rows.append({
            "nom": f"{employe.prenom} {employe.nom}",
            "type": type_label,
            "mois": p.mois,
            "annee": p.annee,
            "montant_du": montant_du,
            "montant_verse": montant_verse,
            "solde_restant": remaining,
            "statut": p.statut,
        })

    profile = db.query(Profile).first()
    data = {
        "info": profile,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "type_label": request.type.value,
        "date_debut": request.date_debut.strftime("%d/%m/%Y"),
        "date_fin": request.date_fin.strftime("%d/%m/%Y"),
        "rows": rows,
        "total_du": total_du,
        "total_verse": total_verse,
        "total_solde": total_solde,
    }

    pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "payroll_report.html", data, "rapport_payroll.pdf"
    )
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=rapport_payroll.pdf"},
    )
