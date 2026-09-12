"""Synchronisation temps réel VERS elearning-iusth (voir plan Épic 20,
elearning-iusth). Fire-and-forget uniquement : jamais bloquant, jamais
transactionnel — une panne réseau ici ne doit JAMAIS faire échouer
l'opération réelle côté ecole_nginx qui a déclenché l'appel (inscription
d'élève, changement de professeur). Toute exception est interceptée et
journalisée, jamais remontée à l'appelant.

Deux niveaux de retry :
1. _post() retente immédiatement quelques fois avec un backoff court (dans
   le BackgroundTask lui-même, voir _MAX_RETRIES) — couvre une panne réseau
   passagère de quelques secondes.
2. Au-delà, l'appel est déposé dans webhook_queue (MSystems.WebhookQueue)
   plutôt que perdu, et repris par le drain périodique
   (app/main.py::_webhook_queue_drain_loop, appelle drain_webhook_queue()
   ci-dessous) — couvre une panne plus longue (elearning-iusth down
   plusieurs minutes/heures). Une ligne abandonne définitivement après
   MAX_QUEUE_ATTEMPTS (voir drain_webhook_queue)."""

import time
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.config.Config import settings
from app.database import SessionLocal
from app.Models.MSystems import WebhookQueue
from app.Routes.RIntegrationExport import resolve_professeur_login_email, resolve_student_login_email, get_programme_export

_MAX_RETRIES = 3
_RETRY_BACKOFF_SECONDS = (1, 3, 9)

# Tentatives totales (immédiates + reprises par le drain) avant d'abandonner
# définitivement une ligne de la file d'attente (status="failed").
MAX_QUEUE_ATTEMPTS = 10


def _send_once(path: str, payload: dict) -> None:
    """Un seul essai, sans retry — lève httpx.HTTPError en cas d'échec
    (réseau injoignable ou réponse non-2xx)."""
    with httpx.Client(base_url=settings.ELEARNING_WEBHOOK_URL,
                       headers={"X-Webhook-Key": settings.ELEARNING_WEBHOOK_KEY}, timeout=5.0) as client:
        response = client.post(path, json=payload)
        response.raise_for_status()


def _enqueue(path: str, payload: dict, error: object) -> None:
    """Dépose l'appel en base pour reprise par drain_webhook_queue() —
    appelé seulement après échec de toutes les tentatives immédiates de
    _post. Ouvre sa propre session (indépendante de celle de l'appelant,
    potentiellement déjà fermée après plusieurs secondes de retry+sleep)."""
    db = SessionLocal()
    try:
        db.add(WebhookQueue(
            path=path, payload=payload, status="pending",
            attempts=_MAX_RETRIES + 1, last_error=str(error)[:1000],
            last_attempt_at=datetime.utcnow(),
        ))
        db.commit()
    except Exception as e:
        print(f"[elearning_webhook] échec d'enregistrement en file d'attente pour {path} : {e}")
    finally:
        db.close()


def _post(path: str, payload: dict) -> None:
    if not settings.ELEARNING_WEBHOOK_URL or not settings.ELEARNING_WEBHOOK_KEY:
        return  # intégration non configurée pour cette école — no-op silencieux

    last_error: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            _send_once(path, payload)
            return  # succès, on s'arrête là
        except httpx.HTTPError as e:
            last_error = e
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS[attempt])

    print(f"[elearning_webhook] échec après {_MAX_RETRIES + 1} tentative(s) vers {path} : {last_error} — mis en file d'attente")
    _enqueue(path, payload, last_error)


def drain_webhook_queue(batch_size: int = 20) -> None:
    """Reprend les webhooks en attente (voir _enqueue) — appelé
    périodiquement par app/main.py::_webhook_queue_drain_loop, jamais par
    la requête HTTP qui a échoué. Une ligne qui échoue encore reste
    'pending' (reprise au prochain passage) jusqu'à MAX_QUEUE_ATTEMPTS, où
    elle passe 'failed' et n'est plus retentée automatiquement."""
    if not settings.ELEARNING_WEBHOOK_URL or not settings.ELEARNING_WEBHOOK_KEY:
        return

    db = SessionLocal()
    try:
        rows = (
            db.query(WebhookQueue)
            .filter(WebhookQueue.status == "pending")
            .order_by(WebhookQueue.created_at.asc())
            .limit(batch_size)
            .all()
        )
        for row in rows:
            try:
                _send_once(row.path, row.payload)
                row.status = "sent"
            except httpx.HTTPError as e:
                row.attempts += 1
                row.last_error = str(e)[:1000]
                if row.attempts >= MAX_QUEUE_ATTEMPTS:
                    row.status = "failed"
                    print(f"[elearning_webhook] abandon définitif après {row.attempts} tentative(s) vers {row.path} (id={row.id})")
            row.last_attempt_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        print(f"[elearning_webhook] erreur pendant le drain de la file d'attente : {e}")
        db.rollback()
    finally:
        db.close()


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


def notify_programme_changed(db: Session, annee_academique_id: str, programme_ids: list[str]) -> None:
    """`programme_ids` : programmes créés OU modifiés dans ce lot (tout
    changement, pas seulement le professeur). Le payload porte la fiche
    complète de chaque programme (mêmes champs que
    GET /integration/programmes/ProgrammeExportOut, voir
    RIntegrationExport.get_programme_export) pour que elearning-iusth
    puisse créer/mettre à jour le cours correspondant sans repasser par un
    import complet."""
    if not programme_ids:
        return

    payload_changes = []
    for programme_id in programme_ids:
        export = get_programme_export(db, programme_id)
        if export is not None:
            payload_changes.append(export.model_dump(mode="json"))

    if not payload_changes:
        return

    _post("/webhooks/ecole-nginx/programme-changed",
          {"annee_academique_id": annee_academique_id, "changes": payload_changes})


def notify_programme_deleted(annee_academique_id: str, programme_id: str) -> None:
    """Un Programme supprimé côté ecole_nginx n'est jamais rejoué par un
    import (l'import n'upserte que ce qu'il reçoit, il ne supprime rien de
    ce qui manque) — sans cet évènement dédié, le cours resterait visible
    indéfiniment côté elearning-iusth après suppression de sa source."""
    _post("/webhooks/ecole-nginx/programme-deleted",
          {"annee_academique_id": annee_academique_id, "programme_id": programme_id})
