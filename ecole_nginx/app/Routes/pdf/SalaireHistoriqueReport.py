from datetime import datetime, date
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, model_validator
from app.database import get_db
from app.Models.MModels import Professeur, User
from app.Models.MSystems import Personnel, Profile
from app.Models.MFinancials import SalaireHistorique
from app.Helper.pdf_personaliser import PDFGenerator
from app.dependencies.Dependencie import check_permission

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()


class PrintSalaireHistoriqueRequest(BaseModel):
    date_debut: date = Field(..., description="Date de début")
    date_fin: date = Field(..., description="Date de fin")

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.date_debut > self.date_fin:
            raise ValueError("La date de début doit être avant ou égale à la date de fin")
        return self


@router.post("/print-salaire-historique-report")
def print_salaire_historique_report(
    request: PrintSalaireHistoriqueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Imprimer rapport")),
):
    """État de tous les changements de salaire_fixe (augmentations et
    baisses) pour une intervalle de dates — voir SalaireHistorique
    (journalisé automatiquement depuis RAcademic.py:store_professeur/
    store_personnel quand salaire_fixe change réellement)."""
    date_debut = datetime.combine(request.date_debut, datetime.min.time())
    date_fin = datetime.combine(request.date_fin, datetime.max.time())

    historiques = db.query(SalaireHistorique).filter(
        SalaireHistorique.created_at.between(date_debut, date_fin)
    ).order_by(SalaireHistorique.created_at.asc()).all()

    rows = []
    for h in historiques:
        if h.employe_type == "professeur":
            employe = db.query(Professeur).filter(Professeur.id == h.employe_id).first()
            type_label = "Professeur"
        else:
            employe = db.query(Personnel).filter(Personnel.id == h.employe_id).first()
            type_label = "Personnel"

        if not employe:
            continue

        ancien = float(h.ancien_montant) if h.ancien_montant is not None else None
        nouveau = float(h.nouveau_montant)
        ecart = nouveau - ancien if ancien is not None else nouveau

        rows.append({
            "nom": f"{employe.prenom} {employe.nom}",
            "type": type_label,
            "ancien_montant": ancien,
            "nouveau_montant": nouveau,
            "ecart": ecart,
            "date": h.created_at.strftime("%d/%m/%Y") if h.created_at else "",
        })

    profile = db.query(Profile).first()
    data = {
        "info": profile,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "date_debut": request.date_debut.strftime("%d/%m/%Y"),
        "date_fin": request.date_fin.strftime("%d/%m/%Y"),
        "rows": rows,
    }

    pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "salaire_historique.html", data, "historique_salaires.pdf"
    )
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=historique_salaires.pdf"},
    )
