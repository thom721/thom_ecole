"""Lecture (jamais poussée) de la contribution des devoirs gérés côté
elearning-iusth, affichée sur les écrans de saisie de notes d'ecole_nginx
(voir plan Épic 24). Contrairement à elearning_webhook.py (fire-and-forget,
avec file d'attente de reprise), cet appel est synchrone et fait partie
d'une réponse HTTP consultée immédiatement par un professeur — donc :
- un seul essai, timeout court ;
- toute panne (réseau, elearning-iusth down, intégration non configurée
  pour cette école, cours pas encore synchronisé) échoue silencieusement
  vers un dict vide — la saisie de notes doit fonctionner à l'identique
  d'avant cette fonctionnalité, jamais bloquée par elle."""

import httpx

from app.config.Config import settings


def fetch_devoirs_grades(programme_id: str) -> dict[str, dict[str, float | None]]:
    """Retourne {email: {note_devoirs, note_devoirs_intra, note_devoirs_finale}}
    pour le Programme donné, ou {} si l'intégration n'est pas configurée,
    injoignable, ou si ce Programme n'a pas de Course synchronisé côté
    elearning-iusth.

    - note_devoirs : mélangé toutes catégories confondues (système à
      crédits, une seule note_finale par inscription).
    - note_devoirs_intra / note_devoirs_finale : calculés uniquement sur
      les catégories elearning-iusth tagguées côté professeur pour cette
      phase (système bloc : Intra et Final sont deux notes cumulatives
      distinctes, il ne faut jamais additionner le même total aux deux)."""
    if not settings.ELEARNING_WEBHOOK_URL or not settings.ELEARNING_WEBHOOK_KEY:
        return {}
    if not programme_id:
        return {}

    try:
        with httpx.Client(base_url=settings.ELEARNING_WEBHOOK_URL,
                           headers={"X-Webhook-Key": settings.ELEARNING_WEBHOOK_KEY}, timeout=5.0) as client:
            response = client.get("/webhooks/ecole-nginx/devoirs-grades", params={"programme_id": programme_id})
            response.raise_for_status()
            rows = response.json()
    except (httpx.HTTPError, ValueError) as e:
        print(f"[elearning_grades_client] impossible de récupérer les notes de devoirs pour programme_id={programme_id} : {e}")
        return {}

    return {
        row["email"]: {
            "note_devoirs": row.get("note_devoirs"),
            "note_devoirs_intra": row.get("note_devoirs_intra"),
            "note_devoirs_finale": row.get("note_devoirs_finale"),
        }
        for row in rows
        if row.get("email") and (
            row.get("note_devoirs") is not None
            or row.get("note_devoirs_intra") is not None
            or row.get("note_devoirs_finale") is not None
        )
    }
