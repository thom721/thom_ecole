from fastapi import Header, HTTPException, status

from app.config.Config import settings


def require_webhook_key(x_webhook_key: str | None = Header(default=None)) -> None:
    """Auth machine-à-machine pour le webhook de synchronisation entrant
    depuis ecole_nginx (Épic 20) — symétrique à
    ecole_nginx/app/dependencies/integration_auth.py::require_integration_key,
    dans l'autre sens. Pas une réutilisation du JWT utilisateur : c'est un
    appel serveur-à-serveur, jamais une action humaine.

    Gardé aussi derrière ECOLE_NGINX_AUTO_PROVISION_TEACHERS (voir
    Config.py) — réutilisé comme interrupteur général "intégration
    ecole_nginx approfondie activée", pas seulement le provisionnement
    de comptes professeur : une autre école qui déploie ce projet sans
    activer ce réglage ne doit jamais voir ses inscriptions modifiées
    par un appel entrant, même avec la bonne clé."""
    if not settings.ECOLE_NGINX_AUTO_PROVISION_TEACHERS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Synchronisation ecole_nginx désactivée (ECOLE_NGINX_AUTO_PROVISION_TEACHERS=false)")
    if not settings.ECOLE_NGINX_WEBHOOK_KEY or x_webhook_key != settings.ECOLE_NGINX_WEBHOOK_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé de webhook invalide")
