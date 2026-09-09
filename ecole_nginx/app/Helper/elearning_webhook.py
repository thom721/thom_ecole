"""Synchronisation temps réel VERS elearning-iusth (voir plan Épic 20,
elearning-iusth). Fire-and-forget uniquement : jamais bloquant, jamais
transactionnel — une panne réseau ici ne doit JAMAIS faire échouer
l'opération réelle côté ecole_nginx qui a déclenché l'appel (inscription
d'élève, changement de professeur). Toute exception est interceptée et
journalisée, jamais remontée à l'appelant."""

import httpx
from sqlalchemy.orm import Session

from app.config.Config import settings
from app.Routes.RIntegrationExport import resolve_professeur_login_email, resolve_student_login_email


def _post(path: str, payload: dict) -> None:
    if not settings.ELEARNING_WEBHOOK_URL or not settings.ELEARNING_WEBHOOK_KEY:
        return  # intégration non configurée pour cette école — no-op silencieux
    try:
        with httpx.Client(base_url=settings.ELEARNING_WEBHOOK_URL,
                           headers={"X-Webhook-Key": settings.ELEARNING_WEBHOOK_KEY}, timeout=5.0) as client:
            client.post(path, json=payload)
    except httpx.HTTPError as e:
        print(f"[elearning_webhook] échec d'envoi vers {path} : {e}")


def notify_enrollment_changed(db: Session, annee_academique_id: str, changes: list[dict]) -> None:
    """`changes` : liste de {etudiant_id, classes_id, status} (status=True
    ajouté/actif, False retiré) — résout l'email de connexion de chaque
    étudiant au passage (voir plan Épic 20 : le webhook porte l'info déjà
    résolue, pas juste des ids bruts)."""
    if not changes:
        return
    payload_changes = [
        {
            "etudiant_id": c["etudiant_id"],
            "classes_id": c["classes_id"],
            "status": c["status"],
            "etudiant_login_email": resolve_student_login_email(db, c["etudiant_id"]),
        }
        for c in changes
    ]
    _post("/webhooks/ecole-nginx/enrollment-changed",
          {"annee_academique_id": annee_academique_id, "changes": payload_changes})


def notify_programme_changed(db: Session, annee_academique_id: str, changes: list[dict]) -> None:
    """`changes` : liste de {programme_id, professeur_id} — résout l'email
    de connexion du nouveau professeur au passage."""
    if not changes:
        return
    from app.Models.MModels import Professeur

    payload_changes = []
    for c in changes:
        professeur = db.query(Professeur).filter(Professeur.id == c["professeur_id"]).first()
        payload_changes.append({
            "programme_id": c["programme_id"],
            "professeur_id": c["professeur_id"],
            "professeur_login_email": resolve_professeur_login_email(db, professeur),
        })
    _post("/webhooks/ecole-nginx/programme-changed",
          {"annee_academique_id": annee_academique_id, "changes": payload_changes})
