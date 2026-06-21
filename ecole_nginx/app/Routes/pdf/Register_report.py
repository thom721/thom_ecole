# app/Schemas/RegisterReportSchema.py
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import  StreamingResponse
# app/Routes/register_report.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db 
from app.Models.MRelations import ClasseEtudiant
from app.Models.MModels import Etudiant,Niveau,AnneeAcademique,Classe
from app.Helper.pdf_personaliser import PDFGenerator
from app.Models.MSystems import Profile


class RegisterReportRequest(BaseModel):
    identifiant: Optional[bool] = False
    classe: str
    annee_ac: str
    cycle: str

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()
@router.post("/print-repport-register21")
def print_register_report(
    request: RegisterReportRequest,
    db: Session = Depends(get_db)
):
    try:
        # 🔹 Query principale (équivalent join Laravel)
        query = (
            db.query(
                ClasseEtudiant,
                Etudiant.nom,
                Etudiant.prenom
            )
            .join(Etudiant, ClasseEtudiant.etudiant_id == Etudiant.id)
            .join(Niveau, ClasseEtudiant.niveau_id == Niveau.id)
            .join(AnneeAcademique, ClasseEtudiant.annee_academique_id == AnneeAcademique.id)
            .join(Classe, ClasseEtudiant.classes_id == Classe.id)
            .filter(ClasseEtudiant.annee_academique_id == request.annee_ac)
            .filter(ClasseEtudiant.status == 1)
        )

        # 🔹 Filtre classe
        if request.classe and request.classe != "Toutes les classes":
            query = query.filter(ClasseEtudiant.classes_id == request.classe)

        # 🔹 Filtre cycle
        if request.cycle and request.cycle != "All":
            query = query.filter(ClasseEtudiant.niveau_id == request.cycle)

        # 🔹 OrderBy
        data_register = query.order_by(Etudiant.nom).all()

        # 🔹 Info école
        info = db.query(Profile).first()

        data = {
            "data_register": [
                {
                    **row.ClasseEtudiant.__dict__,
                    "nom": row.nom,
                    "prenom": row.prenom
                }
                for row in data_register
            ],
            "info": info.__dict__ if info else None,
            "classe": request.classe,
            "cycle": request.cycle,
            "identifiant": bool(request.identifiant),
        }
    
    #     pdf_buffer = pdf_gen.generate_pdf_for_api(
    #     template_file="register_repport.html",  # Votre template Jinja2
    #     data=data,
    #     output_filename="register_repport.pdf"
    # )
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
                "register_repport.html",
                data,
                "register_repport.pdf"
            )
        # return data
          # Retourner le PDF
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=register_repport.pdf"
               }
          )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Une erreur s'est produite lors de l'affichage du rapport. Vérifiez si la classe est dans le bon cycle."
        )

