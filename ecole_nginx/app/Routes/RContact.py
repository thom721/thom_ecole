from fastapi import APIRouter, HTTPException
from app.Schemas.SCommunaute import ContactMessage
from app.utils.students_email import send_contact_message
from app.config import Config

router = APIRouter(prefix="/api/v1/contact", tags=["Contact"])

CONTACT_EMAIL = "contact@iusth.edu.ht"

@router.post("/")
def send_contact(data: ContactMessage):
    if not Config.check_internet_connection():
        raise HTTPException(
            status_code=503,
            detail="Pas de connexion internet — impossible d'envoyer le message pour le moment. Réessayez plus tard.",
        )
    try:
        send_contact_message(
            CONTACT_EMAIL, data.prenom, data.nom, data.email, data.objet, data.tel, data.msg,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Échec de l'envoi du message : {e}")
    return {"message": "Message envoyé"}
