from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client
from app.schemas import SaveDataIn

router = APIRouter(prefix="/api", tags=["Installation"])


@router.post("/save-data")
def save_data(data: SaveDataIn, db: Session = Depends(get_db)):
    """Reçoit les infos du premier compte admin créé lors de l'installation
    d'ecole_nginx (voir ecole_nginx/gui/first_account.py et
    ecole_nginx/scripts/create-first-admin.sh — INFINI_SAVE_DATA_URL).
    Un même mac qui se réinstalle met simplement à jour ses infos."""
    client = db.query(Client).filter(Client.mac == data.mac).first()
    if client:
        client.nom = data.nom
        client.prenom = data.prenom
        client.email = data.email
    else:
        client = Client(nom=data.nom, prenom=data.prenom, email=data.email, mac=data.mac)
        db.add(client)

    db.commit()
    return {"success": True}
