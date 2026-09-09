from fastapi import Header, HTTPException, status

from app.config.Config import settings


def require_integration_key(x_integration_key: str | None = Header(default=None)) -> None:
    """Auth machine-à-machine pour les endpoints d'export destinés à
    elearning-iusth — pas une réutilisation du JWT utilisateur (voir plan
    d'intégration : c'est un appel serveur-à-serveur, pas une action
    humaine)."""
    if not settings.INTEGRATION_API_KEY or x_integration_key != settings.INTEGRATION_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé d'intégration invalide")
