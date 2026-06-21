import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Configuration de la base de données
# DATABASE_URL = "mysql+pymysql://root:password@127.0.0.1:3307/lemignon"
import urllib.parse

password = "@@@@@@@@@@"  # ton mot de passe
password_encoded = urllib.parse.quote_plus(password)
user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
server_path = os.path.join(
user_profile, "AppData", "Local", ".ecole_360", ".certs"
        )
server_path=r"C:\Program Files\ecole-serve\mysql-8.0.41-winx64\certs"
ssl_ca = os.path.join(server_path, "ca-cert.pem").replace("\\", "/")
ssl_cert = os.path.join(server_path, "client-cert.pem").replace("\\", "/")
ssl_key = os.path.join(server_path, "client-key.pem").replace("\\", "/")
 
DATABASE_URL = (
    f"mysql+pymysql://root:{password_encoded}@localhost:3307/lemignon"
    f"?ssl_ca={ssl_ca}&ssl_cert={ssl_cert}&ssl_key={ssl_key}"
) 

# engine = create_engine(
#     "mysql+pymysql://root:password@localhost/dbname",
#     connect_args={
#         "ssl": {
#             "ca": "C:/Program Files/mysql/certs/ca.pem",
#             "cert": "C:/Program Files/mysql/certs/client-cert.pem",
#             "key": "C:/Program Files/mysql/certs/client-key.pem"
#         }
#     }
# )

# engine = create_engine(
#     f"mysql+pymysql://root:{password_encoded}@localhost:3307/lemignon",
#     connect_args={
#         "ssl": {
#             "check_hostname": False,
#             "verify_mode": False
#         }
#     }
# )

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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dépendance pour obtenir la session DB
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# self.heartbeat_timer = QTimer()
# self.heartbeat_timer.timeout.connect(self.ping_server)
# self.heartbeat_timer.start(60000) # Toutes les 60 secondes

# def ping_server(self):
#     # Une requête très légère juste pour garder la route et la DB actives
#     # Par exemple, appeler ton endpoint /verify-token vu plus haut
#     try:
#         httpx.get("https://aplekol360.local/api/v1/ping", timeout=2)
#     except:
#         pass