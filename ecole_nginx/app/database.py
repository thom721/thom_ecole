import os
import platform
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator


import urllib.parse

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Charge le .env explicitement ici : database.py construit l'engine dès l'import,
# avant qu'on soit sûr qu'un autre module ait déjà appelé load_dotenv().
load_dotenv()

# Nombre de tentatives et délai avant abandon. Sur l'installation Windows habituelle,
# MySQL est déjà démarré donc la 1ère tentative réussit (aucun changement de comportement).
# Utile surtout pour Docker Compose, où le conteneur MySQL peut ne pas être encore
# prêt à accepter des connexions au tout premier démarrage de l'API.
DB_CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "5"))
DB_CONNECT_RETRY_DELAY = int(os.getenv("DB_CONNECT_RETRY_DELAY", "3"))


def _windows_ssl_args() -> str:
    """Le MySQL embarqué sur Windows (Controllers/Main_run.py, self.ssl_dir)
    exige l'authentification par certificat client. Les certs sont générés à
    l'installation dans <ProgramFiles>/ecole-serve/mysql-8.0.41-winx64/certs —
    chemin dérivé de %PROGRAMFILES% (pas hardcodé "C:\\Program Files") pour
    rester correct même sur une install 32 bits ou un lecteur différent.
    Si les fichiers n'existent pas (Mac/Linux, ou Windows pas encore installé),
    retourne une chaîne vide : pas de SSL, comme avant."""
    if platform.system() != "Windows":
        return ""
    program_files = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    certs_dir = Path(program_files) / "ecole-serve" / "mysql-8.0.41-winx64" / "certs"
    ca, cert, key = certs_dir / "ca.pem", certs_dir / "client-cert.pem", certs_dir / "client-key.pem"
    if not (ca.exists() and cert.exists() and key.exists()):
        return ""
    return f"?ssl_ca={ca.as_posix()}&ssl_cert={cert.as_posix()}&ssl_key={key.as_posix()}"


def _candidate_configs():
    """Liste des configurations à essayer, dans l'ordre, jusqu'à ce qu'une
    connexion réussisse. Sur Windows, reproduit l'historique (port 3307,
    deux comptes possibles, SSL client) ; sur Mac/Linux/Docker, une seule
    config surchargeable par variables d'env (DB_HOST/DB_PORT/... — voir
    app_gui.py et docker-compose.yml, qui les positionnent déjà)."""
    if platform.system() == "Windows":
        ssl_args = _windows_ssl_args()
        return [
            {"user": "root", "db": "lemignon", "pw": "@#1900", "host": "localhost", "port": "3307", "ssl": ssl_args},
            {"user": "user_pyside", "db": "lekol360", "pw": "@#Janvier21", "host": "localhost", "port": "3307", "ssl": ssl_args},
        ]
    return [{
        "user": os.getenv("DB_USER", "root"),
        "db": os.getenv("DB_NAME", "lekol360"),
        "pw": os.getenv("DB_PASSWORD", "@#1900"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "3306"),
        "ssl": "",
    }]


def get_engine_dynamically():
    import time

    configs = _candidate_configs()
    last_error = None
    for attempt in range(1, DB_CONNECT_RETRIES + 1):
        for config in configs:
            pw_encoded = quote_plus(config["pw"])
            DATABASE_URL = (
                f"mysql+pymysql://{config['user']}:{pw_encoded}@{config['host']}:{config['port']}"
                f"/{config['db']}{config['ssl']}"
            )
            try:
                engine = create_engine(
                    DATABASE_URL,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    connect_args={
                        "connect_timeout": 10
                    }
                )
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return engine
            except Exception as e:
                last_error = e
                continue
        if attempt < DB_CONNECT_RETRIES:
            print(f"Connexion DB échouée (tentative {attempt}/{DB_CONNECT_RETRIES}) : {last_error}")
            time.sleep(DB_CONNECT_RETRY_DELAY)

    print(f"Erreur connexion DB: {last_error}")
    raise Exception("Impossible de se connecter : Aucune configuration valide trouvée.")
# Utilisation
engine = get_engine_dynamically()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_foreign", # Convention Laravel
    "pk": "pk_%(table_name)s"
}
# Base = declarative_base()
metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

# Dépendance pour obtenir la session DB
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# sed 's/utf8mb4_0900_ai_ci/utf8mb4_general_ci/g' 16_05_2026.sql > 16_05_2026_fixed.sql
# mysql -u root -p lekol360 < 16_05_2026_fixed.sql