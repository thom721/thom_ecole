import base64
import hashlib
import hmac as _hmac
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin
from app.models import AdminUser, Client, LicenceKey, Payment
from app.pricing import calculer_montant, get_or_create_pricing_config
from app.receipt import construire_recu, generer_recu_pdf
from app.routes.licence import _valider_paiement
from app.schemas import (
    ActiverPlanIn,
    AdminLoginIn,
    AdminLoginOut,
    ClientCreateIn,
    ClientHistoriqueOut,
    ClientListOut,
    ClientOut,
    PaymentPendingOut,
    PricingConfigIn,
    PricingConfigOut,
    RecuOut,
)
from app.security import create_access_token, verify_password
from app.utils import normaliser_mac

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/login", response_model=AdminLoginOut)
def login(data: AdminLoginIn, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.email == data.email).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    return AdminLoginOut(access_token=create_access_token(admin.email))


@router.get("/clients", response_model=list[ClientListOut])
def liste_clients(db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    clients = db.query(Client).order_by(Client.created_at.desc()).all()
    aujourdhui = datetime.utcnow().date()
    resultats = []
    for client in clients:
        derniere_cle = (
            db.query(LicenceKey)
            .filter(LicenceKey.client_id == client.id)
            .order_by(LicenceKey.created_at.desc())
            .first()
        )
        licence_active = None
        if derniere_cle:
            try:
                licence_active = datetime.strptime(derniere_cle.expiration_date, "%Y-%m-%d").date() >= aujourdhui
            except (ValueError, TypeError):
                pass
        resultats.append(ClientListOut(
            **ClientOut.model_validate(client).model_dump(),
            licence_expiration=derniere_cle.expiration_date if derniere_cle else None,
            licence_active=licence_active,
        ))
    return resultats


@router.post("/clients", response_model=ClientOut, status_code=201)
def creer_client(data: ClientCreateIn, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Enregistrement manuel d'un client par l'admin (mêmes champs que
    l'installation automatique via /api/save-data), pour un client dont
    l'installation n'a pas pu s'enregistrer elle-même (pas de réseau, etc.)."""
    mac = normaliser_mac(data.mac)
    existant = db.query(Client).filter(Client.mac == mac).first()
    if existant:
        raise HTTPException(status_code=409, detail="Un client avec cette adresse MAC existe déjà.")
    client = Client(nom=data.nom, prenom=data.prenom, email=data.email, mac=mac)
    db.add(client)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Un client avec cette adresse MAC existe déjà.")
    db.refresh(client)
    return client


@router.get("/clients/{client_id}", response_model=ClientHistoriqueOut)
def historique_client(client_id: int, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return client


@router.post("/clients/{client_id}/activer", response_model=ClientOut)
def activer_client(client_id: int, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    client.suspended = False
    db.commit()
    db.refresh(client)
    return client


@router.post("/clients/{client_id}/suspendre", response_model=ClientOut)
def suspendre_client(client_id: int, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    client.suspended = True
    db.commit()
    db.refresh(client)
    return client


@router.post("/clients/activer-plan")
def activer_plan(data: ActiverPlanIn, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Active manuellement un plan pour un client (paiement reçu hors-ligne :
    cash, chèque, virement...). mac + email doivent correspondre au même
    client déjà enregistré. Génère la clé en cumulant les jours restants du
    plan actuel comme un paiement en ligne normal (voir _valider_paiement) ;
    le serveur local du client (school_client) récupérera cette clé via
    GET /api/licence/derniere-cle dès qu'il aura une connexion."""
    if data.months < 1:
        raise HTTPException(status_code=422, detail="Le nombre de mois doit être d'au moins 1.")

    client = db.query(Client).filter(Client.mac == normaliser_mac(data.mac)).first()
    if not client or client.email.strip().lower() != data.email.strip().lower():
        raise HTTPException(
            status_code=404,
            detail="Aucun client ne correspond à cette adresse MAC et cet email.",
        )
    if client.suspended:
        raise HTTPException(status_code=403, detail="Ce client a été suspendu.")

    config = get_or_create_pricing_config(db)
    amount, currency = calculer_montant(config, data.months, "manuel")
    days_valid = data.months * 30

    payment = Payment(
        client_id=client.id,
        provider="manuel",
        amount=amount,
        currency=currency,
        status="pending",
        days_valid=days_valid,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return _valider_paiement(payment, db)


@router.get("/config", response_model=PricingConfigOut)
def get_config(db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    return get_or_create_pricing_config(db)


@router.put("/config", response_model=PricingConfigOut)
def update_config(data: PricingConfigIn, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    config = get_or_create_pricing_config(db)
    config.monthly_price = data.monthly_price
    config.currency = data.currency
    config.exchange_rate_usd_htg = data.exchange_rate_usd_htg
    config.auto_release = data.auto_release
    db.commit()
    db.refresh(config)
    return config


@router.get("/paiements/en-attente", response_model=list[PaymentPendingOut])
def paiements_en_attente(db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Paiements confirmés par le fournisseur mais non encore activés (auto_release=False).
    Chaque entrée attend qu'un admin clique 'Activer' pour générer la clé."""
    payments = (
        db.query(Payment)
        .filter(Payment.status == "paid")
        .order_by(Payment.created_at.desc())
        .all()
    )
    result = []
    for p in payments:
        client = db.query(Client).filter(Client.id == p.client_id).first()
        result.append(PaymentPendingOut(
            id=p.id,
            provider=p.provider,
            amount=p.amount,
            currency=p.currency,
            days_valid=p.days_valid,
            created_at=p.created_at,
            client_id=client.id,
            client_nom=client.nom,
            client_prenom=client.prenom,
            client_email=client.email,
            client_mac=client.mac,
        ))
    return result


@router.post("/paiements/{payment_id}/activer")
def activer_paiement(payment_id: int, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Active manuellement un paiement 'paid' : génère la clé et passe le statut à 'success'.
    Utilisé quand auto_release=False — l'admin valide la livraison de la clé."""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.status == "paid").first()
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement introuvable ou déjà activé.")
    return _valider_paiement(payment, db)


@router.delete("/paiements/{payment_id}", status_code=204)
def supprimer_paiement(payment_id: int, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Supprime un paiement non encore traité (statut 'pending', 'paid' ou
    'failed' — pas 'success', qui a une clé associée et se supprime via
    /historique/{key_id} pour rester cohérent avec l'historique du client)."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement introuvable.")
    if payment.status == "success":
        raise HTTPException(status_code=409, detail="Ce paiement est déjà activé — supprimez-le depuis l'historique du client.")
    db.delete(payment)
    db.commit()


@router.get("/paiements/{payment_id}/recu", response_model=RecuOut)
def recu_paiement(payment_id: int, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Détail (JSON) d'un reçu — utilisé pour l'aperçu avant téléchargement du
    PDF (voir /recu.pdf ci-dessous)."""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.status == "success").first()
    if not payment:
        raise HTTPException(status_code=404, detail="Reçu introuvable pour ce paiement.")
    return construire_recu(payment, db)


@router.get("/paiements/{payment_id}/recu.pdf")
def recu_paiement_pdf(payment_id: int, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Reçu imprimable (PDF) d'un paiement déjà activé (statut 'success'),
    qu'il ait été payé en ligne (MonCash/NatCash/Stripe) ou activé
    manuellement par un admin — utilisé juste après activation et pour
    retélécharger un reçu depuis l'historique du client."""
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.status == "success").first()
    if not payment:
        raise HTTPException(status_code=404, detail="Reçu introuvable pour ce paiement.")
    pdf = generer_recu_pdf(construire_recu(payment, db))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="recu-{payment_id}.pdf"'},
    )


class EditExpirationIn(BaseModel):
    expiration_date: str  # format YYYY-MM-DD


def _regenerer_cle(mac: str, expiration_date: str, days_valid_key: int) -> str:
    """Régénère le HMAC de la clé pour un mac/date/days_valid donnés."""
    secret = os.environ.get("KEY_SECRET", "CLE_SECRETE_PERSO")
    raw_data = f"{mac}-{expiration_date}-{days_valid_key}-{secret}".encode()
    hashed = _hmac.new(secret.encode(), raw_data, hashlib.sha256).digest()
    encoded = base64.b32encode(hashed).decode().upper()
    clean = ''.join(filter(str.isalnum, encoded))[:16]
    return '-'.join(clean[i:i+4] for i in range(0, len(clean), 4))


@router.patch("/historique/{key_id}")
def modifier_expiration(key_id: int, data: EditExpirationIn, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Modifie la date d'expiration d'une clé et régénère son HMAC en conséquence."""
    key = db.query(LicenceKey).filter(LicenceKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Clé introuvable.")
    try:
        new_date = datetime.strptime(data.expiration_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Format de date invalide (YYYY-MM-DD attendu).")
    client = db.query(Client).filter(Client.id == key.client_id).first()
    days_valid_key = (new_date - datetime.utcnow().date()).days
    key.expiration_date = data.expiration_date
    key.days_valid_key = days_valid_key
    key.key = _regenerer_cle(client.mac, data.expiration_date, days_valid_key)
    db.commit()
    db.refresh(key)
    return {"id": key.id, "expiration_date": key.expiration_date, "key": key.key}


@router.delete("/historique/{key_id}", status_code=204)
def supprimer_historique(key_id: int, db: Session = Depends(get_db), _admin: AdminUser = Depends(get_current_admin)):
    """Supprime une entrée de l'historique des clés et le paiement associé."""
    key = db.query(LicenceKey).filter(LicenceKey.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Clé introuvable.")
    payment_id = key.payment_id
    db.delete(key)
    db.flush()
    if payment_id:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment:
            db.delete(payment)
    db.commit()
