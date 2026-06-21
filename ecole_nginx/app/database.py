import os
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

# Connexion configurable par variables d'environnement (utile pour installer
# le serveur sur Mac/Windows/Linux avec des identifiants MySQL différents).
# Les valeurs par défaut reproduisent exactement la configuration historique,
# donc rien ne change si aucune de ces variables n'est définie dans le .env.
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "@#1900")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "lekol360")
password_encoded = urllib.parse.quote_plus(DB_PASSWORD)

# Nombre de tentatives et délai avant abandon. Sur l'installation Windows habituelle,
# MySQL est déjà démarré donc la 1ère tentative réussit (aucun changement de comportement).
# Utile surtout pour Docker Compose, où le conteneur MySQL peut ne pas être encore
# prêt à accepter des connexions au tout premier démarrage de l'API.
DB_CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "5"))
DB_CONNECT_RETRY_DELAY = int(os.getenv("DB_CONNECT_RETRY_DELAY", "3"))

def get_engine_dynamically():
    import time

    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    last_error = None
    for attempt in range(1, DB_CONNECT_RETRIES + 1):
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
            if attempt < DB_CONNECT_RETRIES:
                print(f"Connexion DB échouée (tentative {attempt}/{DB_CONNECT_RETRIES}) : {e}")
                time.sleep(DB_CONNECT_RETRY_DELAY)

    print(f"Erreur connexion DB: {last_error}")
    raise Exception("Impossible de se connecter : Aucune configuration valide trouvée.")
# Utilisation
engine = get_engine_dynamically()



# DATABASE_URL = (
#     f"mysql+pymysql://root:{password_encoded}@localhost:3307/lemignon"
#     f"?ssl_ca={ssl_ca}&ssl_cert={ssl_cert}&ssl_key={ssl_key}"
# )

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