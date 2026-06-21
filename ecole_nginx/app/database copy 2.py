import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator


import urllib.parse

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

password = "@@@@@@@@@@"  # ton mot de passe
password_encoded = urllib.parse.quote_plus(password)
user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
server_path = os.path.join(
user_profile, "AppData", "Local", ".ecole_360", ".certs"
        )
server_path=r"C:\Program Files\ecole-serve\mysql-8.0.41-winx64\certs"
ssl_ca = os.path.join(server_path, "ca.pem").replace("\\", "/")
ssl_cert = os.path.join(server_path, "client-cert.pem").replace("\\", "/")
ssl_key = os.path.join(server_path, "client-key.pem").replace("\\", "/")

def get_engine_dynamically():
    # Liste des configurations possibles
    configs = [
        {"user": "root","db": "lemignon", "pw": "@@@@@@@@@@", "host": "localhost"},
        {"user": "user_pyside","db": "lekol360", "pw": "@#Janvier21", "host": "localhost"},
        
    ]
    
    ssl_args = f"?ssl_ca={ssl_ca}&ssl_cert={ssl_cert}&ssl_key={ssl_key}"
    
    for config in configs:
        pw_encoded = quote_plus(config['pw'])
        user = config['user']
        host = config['host']

        DATABASE_URL = f"mysql+pymysql://{user}:{pw_encoded}@{host}:3307/{config['db']}{ssl_args}"
        # mysql+pymysql://root:Lekol360@db/lekol360_cloud
        try:
            # On crée un moteur temporaire avec un timeout court
            # engine = create_engine(url, connect_args={"connect_timeout": 2})
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
            
            # On tente une requête simple pour vérifier si le mot de passe/DB match
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return engine # On retourne le bon moteur
                
        except Exception as e:
            # print(f"❌ Échec pour {config['db']}")
            continue
            
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
# alembic revision -m "create_other_transactions_table"


# certbot certonly --manual --preferred-challenges dns -d api.institutionlemignon.com
# ```

# **2. Certbot donne une nouvelle valeur → ajoute UN SEUL enregistrement TXT sur Hostinger**
# ```
# Type  : TXT
# Nom   : _acme-challenge.api
# Valeur: (la nouvelle valeur)
# ```

# **3. Vérifie sur Windows avant d'appuyer Entrée**
# ```
# nslookup -type=TXT _acme-challenge.api.institutionlemignon.com 8.8.8.8


# docker exec -it lekol360_api bash

# docker compose stop nginx
# certbot certonly --standalone -d api.institutionlemignon.com
# docker compose up -d nginx

# cp /etc/letsencrypt/live/api.institutionlemignon.com/fullchain.pem ./nginx/ssl/cert.pem
# cp /etc/letsencrypt/live/api.institutionlemignon.com/privkey.pem ./nginx/ssl/key.pem

# sudo systemctl restart lemignon-api
# sudo journalctl -u lemignon-api -f 


# apt-get install -y python3-pip python3-cffi python3-brotli \
#     libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 \
#     libffi-dev libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 \
#     shared-mime-info
 
# bash# Relancer juste le container de l'API (le plus rapide)
# docker compose restart api

# # OU forcer un rebuild complet si tu as modifié des dépendances
# docker compose up --build -d api

# # Voir les logs en temps réel pour vérifier
# docker compose logs -f api
 

# # Installer les dépendances système (WeasyPrint)
# RUN apt-get update && apt-get install -y \
#     python3-cffi \
#     python3-brotli \
#     libpango-1.0-0 \
#     libharfbuzz0b \
#     libpangoft2-1.0-0 \
#     libffi-dev \
#     libcairo2 \
#     libgdk-pixbuf2.0-0 \
#     shared-mime-info \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Copier et installer les dépendances Python
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# Ensuite rebuild :
# bashdocker compose up --build -d api

# # Vérifier que tout s'est bien installé
# docker compose logs -f api
# Si tu n'as pas de Dockerfile et que tu utilises une image existante, tu peux aussi l'installer directement dans le container qui tourne (mais c'est temporaire, perdu au prochain rebuild) :
# bashdocker compose exec api bash
# apt-get update && apt-get install -y libpango-1.0-0 libcairo2 ...


# -- Créer l'utilisateur dédié SymmetricDS
# CREATE USER 'symds'@'%' IDENTIFIED BY 'mot_de_passe_fort';

# -- Droits sur la base métier
# GRANT ALL PRIVILEGES ON ta_base.* TO 'symds'@'%';

# -- Droits système nécessaires pour SymmetricDS
# GRANT PROCESS ON *.* TO 'symds'@'%';
# GRANT SUPER ON *.* TO 'symds'@'%';
# GRANT REPLICATION SLAVE ON *.* TO 'symds'@'%';
# GRANT REPLICATION CLIENT ON *.* TO 'symds'@'%';
# GRANT RELOAD ON *.* TO 'symds'@'%';
# GRANT CREATE ON *.* TO 'symds'@'%';
# GRANT DROP ON *.* TO 'symds'@'%';
# GRANT REFERENCES ON *.* TO 'symds'@'%';

# -- Appliquer
# FLUSH PRIVILEGES;

# -- Vérifier
# SHOW GRANTS FOR 'symds'@'%';