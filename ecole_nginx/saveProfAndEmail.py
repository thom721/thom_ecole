from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from passlib.context import CryptContext
from datetime import datetime
import socket
from fastapi_mail import FastMail, MessageSchema
from jinja2 import Template


# Configuration du hachage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modèle Pydantic pour la requête


# Router
router = APIRouter()

# Fonction pour vérifier la connexion internet
def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Vérifie si une connexion internet est disponible"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

# Configuration de l'email (à adapter selon votre service)
conf = ConnectionConfig(
    MAIL_USERNAME="your_email@example.com",
    MAIL_PASSWORD="your_password",
    MAIL_FROM="your_email@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Template email
email_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Notification de compte</title>
</head>
<body>
    <h2>Bonjour {{ prenom }},</h2>
    <p>Votre compte a été créé avec succès pour {{ school_name }}.</p>
    <p><strong>{{ type_compte }}</strong></p>
    <p><strong>Vos identifiants de connexion :</strong></p>
    <ul>
        <li>Email: {{ email }}</li>
        <li>Mot de passe: {{ password }}</li>
    </ul>
    <p>Vous pouvez vous connecter à l'adresse suivante: <a href="{{ url }}">{{ url }}</a></p>
    <p>Cordialement,<br>L'équipe de {{ school_name }}</p>
</body>
</html>
"""

# Fonction d'envoi d'email
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
        logger.warning("Pas de connexion internet. Email non envoyé.")
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
            subject="Création de votre compte",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        fm = FastMail(conf)
        await fm.send_message(message)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'envoi de l'email: {str(e)}"
        )

# Fonction d'autorisation
def authorize_with_admin_token(token: str, permission: str, db: Session):
    """Vérifie les permissions de l'utilisateur"""
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant")
    # Implémentez votre logique d'autorisation ici
    return True

# Fonction pour enregistrer l'action
def set_perso_action(action: str):
    """Enregistre l'action personnalisée"""
    # Implémentez votre logique d'enregistrement d'action
    pass






































from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import select, func, distinct, and_, or_
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json
import logging
import locale

# Configuration du logger
logger = logging.getLogger(__name__)






























# from sqlalchemy import select, or_
# from typing import Optional
# from pydantic import BaseModel, EmailStr, Field, validator
# from passlib.context import CryptContext
# from datetime import datetime



# # Configuration du hachage de mot de passe
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Modèle Pydantic pour la requête


 

# # Fonction pour vérifier la connexion internet


# # Configuration de l'email (à adapter selon votre service)


# # Template email


# # Fonction d'envoi d'email



# # Fonction pour enregistrer l'action
# def set_perso_action(action: str):
#     """Enregistre l'action personnalisée"""
#     # Implémentez votre logique d'enregistrement d'action
#     pass


# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# router = APIRouter()

# # Créer un token d'accès personnel
# @router.post("/tokens", response_model=PersonalAccessTokenResponse)
# async def create_token(
#     token_data: PersonalAccessTokenCreate,
#     db: Session = Depends(get_db)
# ):
#     token = PersonalAccessToken(
#         tokenable_type=token_data.tokenable_type,
#         tokenable_id=token_data.tokenable_id,
#         name=token_data.name,
#         token=token_data.token,
#         abilities=token_data.abilities,
#         created_at=datetime.utcnow()
#     )
#     db.add(token)
#     db.commit()
#     db.refresh(token)
#     return token

# # Assigner un rôle à un modèle


# # Créer une session
# @router.post("/sessions", response_model=SessionResponse)
# async def create_session(
#     session_data: SessionCreate,
#     db: Session = Depends(get_db)
# ):
#     session = Session(
#         id=session_data.id,
#         user_id=session_data.user_id,
#         ip_address=session_data.ip_address,
#         user_agent=session_data.user_agent,
#         payload=session_data.payload,
#         last_activity=session_data.last_activity
#     )
#     db.add(session)
#     db.commit()
#     return session

# # Créer un token de réinitialisation de mot de passe
# @router.post("/password-reset", response_model=PasswordResetTokenResponse)
# async def create_password_reset(
#     reset_data: PasswordResetTokenCreate,
#     db: Session = Depends(get_db)
# ):
#     reset_token = PasswordResetToken(
#         email=reset_data.email,
#         token=reset_data.token,
#         created_at=datetime.utcnow()
#     )
#     db.add(reset_token)
#     db.commit()
#     return reset_token

# # Assigner une permission à un rôle
# @router.post("/role-permissions", response_model=RoleHasPermissionResponse)
# async def assign_permission_to_role(
#     assignment: RoleHasPermissionCreate,
#     db: Session = Depends(get_db)
# ):
#     role_permission = RoleHasPermission(
#         permission_id=assignment.permission_id,
#         role_id=assignment.role_id
#     )
#     db.add(role_permission)
#     db.commit()
#     return role_permission

