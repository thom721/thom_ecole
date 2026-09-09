from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "elearning_iusth"

    SECRET_KEY: str = "change-moi-en-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours

    # Comma-separated list, ex: "http://localhost:5173,https://elearning.iusth.edu.ht"
    BACKEND_CORS_ORIGINS_RAW: str = ""

    UPLOAD_DIR: str = "app/static/uploads"

    # Intégration ecole_nginx (import de cours réels, voir plan) — appel
    # machine-à-machine, clé partagée (même valeur que
    # ecole_nginx/.env::INTEGRATION_API_KEY).
    ECOLE_NGINX_BASE_URL: str = "http://host.docker.internal:9001/api/v1"
    ECOLE_NGINX_INTEGRATION_KEY: str = ""
    # Désactivé par défaut : une école qui déploie cette plateforme sans
    # vouloir de provisionnement automatique de comptes professeur ne doit
    # jamais s'en trouver activée par erreur — à activer explicitement dans
    # .env si souhaité (voir RIntegration.py).
    ECOLE_NGINX_AUTO_PROVISION_TEACHERS: bool = False

    # Envoi d'email (réinitialisation de mot de passe) — compte dédié
    # noreply@iusth.edu.ht (voir ecole_nginx/.env.web.example, même
    # hébergeur), distinct du compte software@infini-software.cloud utilisé
    # par ecole_nginx (systèmes séparés, choix explicite du client).
    SMTP_HOST: str = "smtp.hostinger.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "noreply@iusth.edu.ht"
    SMTP_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@iusth.edu.ht"
    MAIL_FROM_NAME: str = "IUSTH e-learning"
    # Sert à construire le lien cliquable dans l'email de réinitialisation.
    FRONTEND_BASE_URL: str = "http://localhost:5173"

    # Cours en direct (Épic 17) — serveur Jitsi Meet auto-hébergé
    # (docker-jitsi-meet, voir docker-compose.jitsi.yml). Le backend ne
    # traite jamais l'audio/vidéo lui-même : il ne fait que signer un JWT
    # accepté par le serveur Jitsi (même principe que le proxy
    # `mod_bigbluebuttonbn` du vrai Moodle envers un serveur BigBlueButton
    # externe, voir plan). JITSI_BASE_URL doit être l'URL réellement
    # joignable par le navigateur de l'utilisateur (le frontend y charge
    # `external_api.js` directement, sans passer par ce backend).
    JITSI_BASE_URL: str = "https://localhost:8443"
    JITSI_JWT_APP_ID: str = "elearning_iusth"
    JITSI_JWT_APP_SECRET: str = "change-moi-en-production"

    # Webhook de synchronisation temps réel depuis ecole_nginx (Épic 20)
    # — appel machine-à-machine entrant, clé partagée (même valeur que
    # ecole_nginx/.env::ELEARNING_WEBHOOK_KEY). Authentifie l'appelant
    # (ecole_nginx), pas un utilisateur JWT.
    ECOLE_NGINX_WEBHOOK_KEY: str = ""

    # Premier compte admin (voir Helper/bootstrap_admin.py) — vide par
    # défaut, n'agit que si les deux sont explicitement renseignés en
    # .env, et seulement s'il n'existe encore aucun compte admin.
    BOOTSTRAP_ADMIN_EMAIL: str = ""
    BOOTSTRAP_ADMIN_PASSWORD: str = ""

    @property
    def BACKEND_CORS_ORIGINS(self) -> list[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS_RAW.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
