# app/Routes/pdf/vente_recu.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from io import BytesIO

from app.database import get_db
from app.Models.MFinancials import Vente
from app.Models.MSystems import Profile  

from app.Helper.pdf_personaliser import PDFGenerator
router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()


@router.get("/print-recu-vente/{id}")
def generate_pdf_vente(
    id: str,
    db: Session = Depends(get_db)
):
    try: 
        vente = (
            db.query(Vente)
            .options(
                joinedload(Vente.user),
                joinedload(Vente.etudiant),
                joinedload(Vente.order_items),
            )
            .filter(Vente.id == id)
            .first()
        )

        if not vente:
            raise HTTPException(status_code=404, detail="Vente introuvable")

        info = db.query(Profile).first()
        print(vente.__dict__)
        context = {
            "vente": vente,
            "info": info,
            "date": vente.created_at.strftime("%d/%m/%Y"),
        }

        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
            "vente_recu.html",  # Votre template Jinja2
            context,
            "vente_recu.pdf"
        )
        # return data
          # Retourner le PDF
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=vente_recu.pdf"
               }
          )
        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=fiche-vente.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
