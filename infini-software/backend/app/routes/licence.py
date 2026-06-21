import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Client, LicenceKey, Payment
from app.payments.base import get_provider
from app.pricing import calculer_montant, get_or_create_pricing_config
from app.schemas import PaiementCreateIn, PricingConfigOut
from genere_key import generate_activation_key

router = APIRouter(prefix="/api/licence", tags=["Licence"])

PAYMENT_TEST_MODE = os.environ.get("PAYMENT_TEST_MODE", "false").lower() == "true"


def _valider_paiement(payment: Payment, db: Session) -> dict:
    """Marque un paiement comme réussi et génère la clé d'activation
    correspondante. Cumule les jours restants du plan actuel s'il n'est pas
    encore expiré, pour qu'un renouvellement anticipé n'efface jamais les
    jours déjà payés (sinon generate_activation_key recalcule toujours depuis
    aujourd'hui)."""
    client = db.query(Client).filter(Client.id == payment.client_id).first()

    aujourdhui = datetime.utcnow().date()
    base_date = aujourdhui
    cle_courante = (
        db.query(LicenceKey)
        .filter(LicenceKey.client_id == client.id)
        .order_by(LicenceKey.created_at.desc())
        .first()
    )
    if cle_courante:
        try:
            expiration_courante = datetime.strptime(cle_courante.expiration_date, "%Y-%m-%d").date()
            if expiration_courante > base_date:
                base_date = expiration_courante
        except (ValueError, TypeError):
            pass

    jours_valid_ajustes = (base_date - aujourdhui).days + payment.days_valid
    key, expiration_date, _ = generate_activation_key(mac_address=client.mac, days_valid=jours_valid_ajustes)

    licence_key = LicenceKey(
        client_id=client.id,
        key=key,
        expiration_date=expiration_date,
        days_valid=payment.days_valid,
        days_valid_key=jours_valid_ajustes,
        payment_id=payment.id,
    )
    payment.status = "success"
    db.add(licence_key)
    db.commit()

    return {"status": "success", "key": key, "expiration_date": expiration_date}


@router.get("/tarif", response_model=PricingConfigOut)
def tarif(db: Session = Depends(get_db)):
    """Prix mensuel + taux de change courants, public (pas d'auth) — utilisé
    par la page de renouvellement pour afficher le prix avant paiement."""
    return get_or_create_pricing_config(db)


@router.get("/verifier-mac")
def verifier_mac(mac: str = Query(...), db: Session = Depends(get_db)):
    """Vérifie qu'un mac est bien enregistré sur ce serveur (installation
    déjà inscrite via /api/save-data) avant d'autoriser un paiement. Ne
    renvoie aucune donnée personnelle (nom/prénom/email) — juste l'existence
    et le statut, pour que la page de renouvellement puisse valider le champ
    mac (lecture seule côté client) avant d'afficher le formulaire de paiement."""
    client = db.query(Client).filter(Client.mac == mac).first()
    return {"exists": client is not None, "suspended": client.suspended if client else False}


@router.get("/derniere-cle")
def derniere_cle(mac: str = Query(...), db: Session = Depends(get_db)):
    """Dernière clé émise pour ce mac (public, mêmes garanties que
    /verifier-mac — pas de données personnelles). Utilisé par le serveur
    ecole_nginx du client (via school_client) pour savoir, après un paiement,
    s'il existe une clé plus récente que celle qu'il a en local et l'appliquer
    lui-même (modèle "pull" : infini-software ne peut pas appeler directement
    un serveur derrière un réseau local/NAT)."""
    client = db.query(Client).filter(Client.mac == mac).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable.")
    derniere = (
        db.query(LicenceKey)
        .filter(LicenceKey.client_id == client.id)
        .order_by(LicenceKey.created_at.desc())
        .first()
    )
    if not derniere:
        raise HTTPException(status_code=404, detail="Aucune clé émise pour ce client.")
    return {
        "key": derniere.key,
        "expiration_date": derniere.expiration_date,
        # days_valid_key est la valeur réellement utilisée dans le HMAC de
        # `key` (cumul des jours restants inclus en cas de renouvellement
        # anticipé) — c'est elle qu'il faut transmettre pour qu'une
        # revérification HMAC locale (ecole_nginx) retombe juste. `days_valid`
        # (la valeur "sémantique", ce que le client a payé cette fois-ci)
        # n'est pas exposée ici : elle ne correspond pas forcément au HMAC.
        "days_valid": derniere.days_valid_key,
        "created_at": derniere.created_at,
    }


@router.post("/payer")
async def initier_paiement(data: PaiementCreateIn, db: Session = Depends(get_db)):
    """Démarre un paiement de renouvellement pour le client identifié par son mac.
    Le montant n'est jamais fourni par l'appelant : il est calculé côté serveur
    à partir du prix mensuel configuré par l'admin et du nombre de mois choisi
    (carte -> USD ; MonCash/NatCash -> converti en HTG au taux du jour)."""
    client = db.query(Client).filter(Client.mac == data.mac).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable. L'installation doit s'enregistrer d'abord.")
    if client.suspended:
        raise HTTPException(status_code=403, detail="Ce client a été suspendu par un administrateur.")
    if data.months < 1:
        raise HTTPException(status_code=422, detail="Le nombre de mois doit être d'au moins 1.")

    config = get_or_create_pricing_config(db)
    amount, currency = calculer_montant(config, data.months, data.provider)
    days_valid = data.months * 30

    payment = Payment(
        client_id=client.id,
        provider=data.provider,
        amount=amount,
        currency=currency,
        status="pending",
        days_valid=days_valid,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    order_id = f"licence-{client.id}-{payment.id}-{uuid.uuid4().hex[:8]}"

    if PAYMENT_TEST_MODE:
        payment.provider_reference = order_id
        db.commit()
        resultat = _valider_paiement(payment, db)
        return {"payment_id": payment.id, "redirect_url": None, "provider_reference": order_id, **resultat}

    try:
        provider = get_provider(data.provider)
        result = await provider.create_payment(amount=amount, currency=currency, order_id=order_id)
    except (NotImplementedError, ValueError) as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail=f"Erreur fournisseur de paiement : {e}")

    payment.provider_reference = result.provider_reference
    db.commit()

    return {"payment_id": payment.id, "redirect_url": result.redirect_url, "provider_reference": result.provider_reference}


@router.get("/payer/confirmer")
async def confirmer_paiement(
    payment_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """À appeler après le retour du fournisseur de paiement (callback/retour
    de redirection) pour vérifier le paiement et, si réussi, générer une
    nouvelle clé d'activation pour le client."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement introuvable")
    if payment.status == "success":
        derniere_cle = (
            db.query(LicenceKey)
            .filter(LicenceKey.payment_id == payment.id)
            .order_by(LicenceKey.created_at.desc())
            .first()
        )
        return {"status": "success", "key": derniere_cle.key if derniere_cle else None}

    try:
        provider = get_provider(payment.provider)
        ok = await provider.verify_payment(payment.provider_reference)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erreur de vérification du paiement : {e}")

    if not ok:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=402, detail="Paiement non confirmé par le fournisseur")

    return _valider_paiement(payment, db)
