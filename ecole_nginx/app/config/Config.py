import socket
from fastapi import APIRouter, Depends, HTTPException, Header
from app.templates.email import email_template
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Template
import os
from typing import Optional, List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()
App_name= "Lekol 360"
logo_url='https://aplekol360.local/static/logo/school_logo.png'
BASE_URL='https://aplekol360.local'
url='https://aplekol360.local'
STORAGE_PATH='/static/'

# conf = ConnectionConfig(
#     MAIL_USERNAME="your_email@example.com",
#     MAIL_PASSWORD="your_password",
#     MAIL_FROM="your_email@example.com",
#     MAIL_PORT=587,
#     MAIL_SERVER="smtp.gmail.com",
#     MAIL_STARTTLS=True,
#     MAIL_SSL_TLS=False,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True
# )


conf = ConnectionConfig(
    MAIL_USERNAME="software@infini-software.cloud",
    MAIL_PASSWORD="", # Ne pas laisser vide !
    MAIL_FROM="software@infini-software.cloud",
    MAIL_PORT=587,                          # Port standard pour SSL
    MAIL_SERVER="smtp.titan.email",
    MAIL_STARTTLS=True,                    # Désactivé car on est en SSL direct
    MAIL_SSL_TLS=False,                      # Activé pour le port 465
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM_NAME="Lekol 360"
)

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):

    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False
    
async def send_account_notification(
    email: str,
    prenom: str,
    school_name: str,
    url: str,
    user_email: str,
    password: str,
    type_compte: str
):
    """Envoie un email de notification de création de compte"""
    
    # Vérifier la connexion internet avant d'envoyer
    if not check_internet_connection():
        raise HTTPException(
            status_code=503,
            detail="Pas de connexion internet. Impossible d'envoyer l'email de notification."
        )
    
    try:
        template = Template(email_template)
        html_content = template.render(
            prenom=prenom,
            school_name=school_name,
            url=url,
            email=user_email,
            password=password,
            type_compte=type_compte
        )
        
        message = MessageSchema(
            subject=f"Création de votre compte {type_compte}",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'envoi de l'email"#: {str(e)}
        )
    

# Charge les variables d'environnement
load_dotenv()

class SimpleSettings:
    # Application
    APP_NAME: str = "School Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "9001"))
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "School Management System"
    
    # CORS
    @property
    def BACKEND_CORS_ORIGINS(self):
        origins = os.getenv("BACKEND_CORS_ORIGINS", "")
        if origins:
            return [origin.strip() for origin in origins.split(",")]
        return []
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/school_db")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1520"))  # 8 jours
    
    # Security
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    PASSWORD_SALT_ROUNDS: int = 12
    
    # File upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx"]
      
   
    # Email (optionnel)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST","smtp.hostinger.com")
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER","software@infini-software.cloud")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD","Janvier@21@")
    MAIL_FROM: Optional[str] = os.getenv("MAIL_FROM","software@infini-software.cloud")
    MAIL_FROM_NAME: Optional[str] = os.getenv("MAIL_FROM_NAME",'Lekol 360')
    # Redis (optionnel pour cache)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Logging

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    
    # Paths
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    STATIC_DIR: str = os.getenv("STATIC_DIR", "static")


settings = SimpleSettings()

# Factory pour obtenir les settings selon l'environnement
def get_settings():
    return settings