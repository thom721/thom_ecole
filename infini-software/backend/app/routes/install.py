from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client
from app.schemas import SaveDataIn
from app.utils import normaliser_mac

router = APIRouter(prefix="/api", tags=["Installation"])


@router.post("/save-data")
def save_data(data: SaveDataIn, db: Session = Depends(get_db)):
    """Reçoit les infos du premier compte admin créé lors de l'installation
    d'ecole_nginx (voir ecole_nginx/gui/first_account.py et
    ecole_nginx/scripts/create-first-admin.sh — INFINI_SAVE_DATA_URL).
    Un même mac qui se réinstalle met simplement à jour ses infos."""
    mac = normaliser_mac(data.mac)
    client = db.query(Client).filter(Client.mac == mac).first()
    if client:
        client.nom = data.nom
        client.prenom = data.prenom
        client.email = data.email
    else:
        client = Client(nom=data.nom, prenom=data.prenom, email=data.email, mac=mac)
        db.add(client)

    try:
        db.commit()
    except IntegrityError:
        # Course entre deux installations sur le même mac (rare) : la ligne
        # existe déjà désormais, on relit et met à jour au lieu d'échouer.
        db.rollback()
        client = db.query(Client).filter(Client.mac == mac).first()
        client.nom = data.nom
        client.prenom = data.prenom
        client.email = data.email
        db.commit()
    return {"success": True}
