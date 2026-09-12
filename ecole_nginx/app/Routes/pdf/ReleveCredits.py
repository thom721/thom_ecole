# app/Routes/pdf/ReleveCredits.py — relevé de notes PDF pour le système à
# crédits (niveau Universitaire, voir app/Models/MCredits.py). Distinct du
# bulletin bloc (BulletinPrint.py, Intra/Final) : un étudiant Universitaire
# est soit sur le système bloc soit sur le système à crédits, jamais les
# deux (voir RNotes.py/RCoursEtudiant.py, garde-fou déjà en place).

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MModels import Etudiant, User, Cours
from app.Models.MSystems import Profile
from app.Helper.credits import resume_progres_etudiant
from app.Helper.pdf_personaliser import PDFGenerator
from app.dependencies.Dependencie import get_current_user, user_has_permission
from app.Routes.RCredits import _est_lui_meme

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()


class ReleveCreditsRequest(BaseModel):
    etudiant_id: str


@router.post("/imprime-releve-credits")
def imprimer_releve_credits(
    request: ReleveCreditsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Relevé de notes PDF (système à crédits) — réutilise tel quel
    resume_progres_etudiant (app/Helper/credits.py), déjà exact et déjà
    utilisé par la page web Progrès de l'étudiant. Accès : le personnel
    via la même permission que le bulletin bloc, ou l'étudiant lui-même
    (même _est_lui_meme que RCredits.py — libre-service)."""
    if not _est_lui_meme(current_user, request.etudiant_id) and not user_has_permission(current_user, "Imprimer bulletin", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorisé à imprimer ce relevé")

    etudiant = db.query(Etudiant).filter(Etudiant.id == request.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    progres = resume_progres_etudiant(db, request.etudiant_id)

    cours_ids = [i["cours_id"] for i in progres["inscriptions"]]
    cours_par_id = {
        c.id: c.cours_nom
        for c in db.query(Cours).filter(Cours.id.in_(cours_ids)).all()
    } if cours_ids else {}
    for inscription in progres["inscriptions"]:
        inscription["cours_nom"] = cours_par_id.get(inscription["cours_id"], inscription["cours_id"])

    profile = db.query(Profile).first()

    result = {
        "etudiant": {
            "identifiant": etudiant.identifiant,
            "nom": etudiant.nom,
            "prenom": etudiant.prenom,
        },
        "info": profile,
        "progres": progres,
    }

    try:
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
            "releve_credits.html", result, "releve_credits.pdf",
        )
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=releve_credits.pdf"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du relevé : {str(e)}")
