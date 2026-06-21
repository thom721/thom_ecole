"""Seed de test : mirroring de la table log_actives de lekol360 (ecole_nginx)
dans la base infini-software, pour le même mac que l'install locale, afin de
tester le flux complet (historique + statut expiré + bouton Renouveler) des
deux côtés avec des données cohérentes entre elles.

Le days_valid de chaque entrée est calculé dynamiquement depuis les dates
réelles (exprired_at - created_at), jamais une constante codée en dur.

Idempotent : relance = on repart d'un client propre (les anciennes données
de ce mac sont supprimées avant réinsertion).

Usage : venv/bin/python3 seed_test_data.py
"""
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from app.database import Base, SessionLocal, engine
from app.models import Client, LicenceKey, Payment

Base.metadata.create_all(bind=engine)

MAC = "AC:DE:48:00:11:22"
NOM = "Mignon"
PRENOM = "Mignon"
EMAIL = "institutionlemignon25@gmail.com"

# Données réelles extraites de lekol360.log_actives (ORDER BY created_at),
# y compris la dernière entrée ajoutée via /api/v1/log-activate pour simuler
# un abonnement désormais expiré (new_key généré par genere_key.py).
HISTORIQUE_REEL = [
    {"new_key": "GM3D-RJYD-73XH-UDNK", "exprired_at": "2025-10-29", "created_at": "2025-09-29 09:40:39"},
    {"new_key": "GM3D-RJYD-73XH-UDNK", "exprired_at": "2025-10-29", "created_at": "2025-09-29 10:16:36"},
    {"new_key": "GM3D-RJYD-73XH-UDNK", "exprired_at": "2025-10-29", "created_at": "2025-09-29 10:16:42"},
    {"new_key": "OT46-OTGC-W7IA-5KWZ", "exprired_at": "2025-12-04", "created_at": "2025-11-04 05:46:51"},
    {"new_key": "W7DD-PJ7A-PRR2-EBHQ", "exprired_at": "2026-01-04", "created_at": "2025-12-05 07:31:34"},
    {"new_key": "WI2A-ZKFL-SSAU-PY5M", "exprired_at": "2026-02-06", "created_at": "2026-01-07 05:40:13"},
    {"new_key": "3FZA-F6DK-KN3J-ZMPE", "exprired_at": "2026-03-08", "created_at": "2026-02-06 09:59:32"},
    {"new_key": "OJ2O-T7TR-TY7J-UNL7", "exprired_at": "2026-04-08", "created_at": "2026-03-09 08:55:14"},
    {"new_key": "73ES-DMLV-K6WC-EDZQ", "exprired_at": "2026-04-11", "created_at": "2026-03-12 09:47:53"},
    {"new_key": "X65T-UYAD-X3OF-NOPN", "exprired_at": "2026-07-03", "created_at": "2026-06-03 10:44:21"},
    {"new_key": "X65T-UYAD-X3OF-NOPN", "exprired_at": "2026-07-03", "created_at": "2026-06-03 10:44:33"},
]

# Dernière entrée (expirée) : générée via genere_key.generate_activation_key
# et déjà enregistrée côté lekol360 via POST /api/v1/log-activate, donc
# rejouée ici à l'identique pour que les deux bases soient cohérentes.
ENTREE_EXPIREE = {"new_key": "MNUK-BQW4-3G4Q-533S", "exprired_at": "2026-06-14", "created_at": "2026-06-19 14:29:40"}


def days_valid_for(created_at: str, exprired_at: str) -> int:
    created = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").date()
    expired = datetime.strptime(exprired_at, "%Y-%m-%d").date()
    return (expired - created).days


def main():
    db = SessionLocal()
    try:
        existing = db.query(Client).filter(Client.mac == MAC).first()
        if existing:
            db.query(LicenceKey).filter(LicenceKey.client_id == existing.id).delete()
            db.query(Payment).filter(Payment.client_id == existing.id).delete()
            db.delete(existing)
            db.commit()

        client = Client(nom=NOM, prenom=PRENOM, email=EMAIL, mac=MAC, suspended=False)
        db.add(client)
        db.commit()
        db.refresh(client)

        for entry in HISTORIQUE_REEL:
            db.add(LicenceKey(
                client_id=client.id,
                key=entry["new_key"],
                expiration_date=entry["exprired_at"],
                days_valid=days_valid_for(entry["created_at"], entry["exprired_at"]),
                created_at=datetime.strptime(entry["created_at"], "%Y-%m-%d %H:%M:%S"),
            ))

        payment = Payment(
            client_id=client.id,
            provider="moncash",
            amount=500,
            currency="HTG",
            status="success",
            days_valid=days_valid_for(ENTREE_EXPIREE["created_at"], ENTREE_EXPIREE["exprired_at"]),
            provider_reference="seed-test-expire",
            created_at=datetime.strptime(ENTREE_EXPIREE["created_at"], "%Y-%m-%d %H:%M:%S"),
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        db.add(LicenceKey(
            client_id=client.id,
            key=ENTREE_EXPIREE["new_key"],
            expiration_date=ENTREE_EXPIREE["exprired_at"],
            days_valid=payment.days_valid,
            payment_id=payment.id,
            created_at=datetime.strptime(ENTREE_EXPIREE["created_at"], "%Y-%m-%d %H:%M:%S"),
        ))
        db.commit()

        print(f"✅ Client {EMAIL} ({MAC}) seedé avec {len(HISTORIQUE_REEL) + 1} entrées d'historique.")
        print(f"   Dernière entrée : clé {ENTREE_EXPIREE['new_key']}, expirée le {ENTREE_EXPIREE['exprired_at']} "
              f"({payment.days_valid} jours).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
