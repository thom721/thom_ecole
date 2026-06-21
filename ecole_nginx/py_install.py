# ==================== 1. MODÈLE DE LOG ====================
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
from database import Base

class Log(Base):
    __tablename__ = 'logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=False)
    authorization_id = Column(Integer, nullable=True)
    paiement_key = Column(String(255), nullable=True)
    model_type = Column(String(255), nullable=False)
    model_id = Column(Integer, nullable=False)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== 2. CONTEXTE POUR STOCKER LES INFOS ====================
from contextvars import ContextVar
from typing import Optional

# Variables de contexte (équivalent de Laravel Helper)
current_user_id: ContextVar[Optional[int]] = ContextVar('current_user_id', default=None)
current_admin_id: ContextVar[Optional[int]] = ContextVar('current_admin_id', default=None)
custom_action: ContextVar[Optional[str]] = ContextVar('custom_action', default=None)
last_paiement_key: ContextVar[Optional[str]] = ContextVar('last_paiement_key', default=None)


class ActionContext:
    """Helper pour gérer les actions personnalisées"""
    
    @staticmethod
    def set_action(action: str):
        custom_action.set(action)
    
    @staticmethod
    def get_action() -> Optional[str]:
        return custom_action.get()
    
    @staticmethod
    def clear():
        custom_action.set(None)


class AdminAuthorization:
    """Helper pour gérer l'admin ID"""
    
    @staticmethod
    def set_admin_id(admin_id: int):
        current_admin_id.set(admin_id)
    
    @staticmethod
    def get_admin_id() -> Optional[int]:
        return current_admin_id.get()
    
    @staticmethod
    def clear():
        current_admin_id.set(None)


# ==================== 3. OBSERVATEUR GLOBAL ====================
import json
from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

class GlobalModelObserver:
    """
    Observateur global pour logger automatiquement les actions CRUD
    """
    
    EXCLUDED_FIELDS = ['password', 'remember_token', 'updated_at', 'created_at']
    
    def __init__(self, db: Session, request_ip: str = None):
        self.db = db
        self.request_ip = request_ip
    
    def sanitize_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Exclure les champs sensibles"""
        return {k: v for k, v in attributes.items() if k not in self.EXCLUDED_FIELDS}
    
    def model_to_dict(self, model: Any, exclude_none: bool = False) -> Dict[str, Any]:
        """Convertir un modèle SQLAlchemy en dictionnaire"""
        result = {}
        for column in inspect(model.__class__).columns:
            value = getattr(model, column.name)
            if exclude_none and value is None:
                continue
            # Convertir les types spéciaux en JSON sérialisables
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            result[column.name] = value
        return result
    
    def get_changes(self, model: Any) -> Dict[str, Any]:
        """Récupérer uniquement les champs modifiés"""
        state = inspect(model)
        changes = {}
        
        for attr in state.attrs:
            hist = attr.load_history()
            if hist.has_changes():
                changes[attr.key] = attr.value
        
        return changes
    
    def json_diff(self, old: Dict, new: Dict) -> Dict:
        """Calculer la différence entre deux dictionnaires JSON"""
        diff = {}
        
        for key, value in new.items():
            if key not in old:
                diff[key] = value
            elif isinstance(value, dict) and isinstance(old[key], dict):
                sub_diff = self.json_diff(old[key], value)
                if sub_diff:
                    diff[key] = sub_diff
            elif old[key] != value:
                diff[key] = {
                    '_modified_from': old[key],
                    '_to': value
                }
        
        return diff
    
    def created(self, model: Any):
        """Logger la création d'un modèle"""
        new_values = self.model_to_dict(model)
        self.log_activity('create', model, None, new_values)
    
    def updated(self, model: Any, old_values: Dict[str, Any]):
        """Logger la mise à jour d'un modèle"""
        changes = self.get_changes(model)
        if not changes:
            return  # Pas de changement réel
        
        self.log_activity('update', model, old_values, changes)
    
    def deleted(self, model: Any):
        """Logger la suppression d'un modèle"""
        old_values = self.model_to_dict(model)
        self.log_activity('delete', model, old_values, None)
    
    def log_activity(
        self, 
        action: str, 
        model: Any, 
        old: Optional[Dict], 
        new: Optional[Dict]
    ):
        """Enregistrer l'activité dans la base de données"""
        user_id = current_user_id.get()
        
        if not user_id:
            raise Exception("User non authentifié lors du log")
        
        # Sanitize
        old_sanitized = self.sanitize_attributes(old or {})
        new_sanitized = self.sanitize_attributes(new or {})
        
        # Gestion spéciale pour les champs JSON (exemple: paiement_details)
        if hasattr(model, 'paiement_details') and old and new:
            if 'paiement_details' in old_sanitized and 'paiement_details' in new_sanitized:
                old_json = old_sanitized['paiement_details']
                new_json = new_sanitized['paiement_details']
                
                if isinstance(old_json, str):
                    old_json = json.loads(old_json)
                if isinstance(new_json, str):
                    new_json = json.loads(new_json)
                
                diff = self.json_diff(old_json, new_json)
                if not diff:
                    return  # Pas de changement réel
                
                new_sanitized['paiement_details'] = diff
        
        # Récupérer l'action personnalisée ou utiliser l'action par défaut
        final_action = ActionContext.get_action() or action
        
        # Récupérer l'admin ID ou utiliser le user_id
        auth_id = AdminAuthorization.get_admin_id() or user_id
        
        # Récupérer la clé de paiement si disponible
        paiement_key = getattr(model, 'last_paiement_key', None)
        
        # Créer le log
        log_entry = Log(
            id=uuid.uuid4(),
            action=final_action,
            user_id=user_id,
            authorization_id=auth_id,
            paiement_key=paiement_key,
            model_type=f"{model.__class__.__module__}.{model.__class__.__name__}",
            model_id=model.id,
            old_values=old_sanitized if old_sanitized else None,
            new_values=new_sanitized if new_sanitized else None,
            ip_address=self.request_ip
        )
        
        self.db.add(log_entry)
        self.db.commit()
        
        # Clear context
        AdminAuthorization.clear()
        ActionContext.clear()


# ==================== 4. MIXIN POUR LES MODÈLES ====================
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event

class ObservableMixin:
    """
    Mixin à ajouter aux modèles qui doivent être observés
    
    Usage:
        class User(Base, ObservableMixin):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            ...
    """
    
    @declared_attr
    def __mapper_args__(cls):
        """Configuration automatique des événements SQLAlchemy"""
        return {
            'eager_defaults': True
        }
    
    @classmethod
    def register_observers(cls, db: Session, request_ip: str = None):
        """Enregistrer les observateurs pour ce modèle"""
        observer = GlobalModelObserver(db, request_ip)
        
        @event.listens_for(cls, 'after_insert')
        def after_insert(mapper, connection, target):
            observer.created(target)
        
        @event.listens_for(cls, 'after_update')
        def after_update(mapper, connection, target):
            # Récupérer les anciennes valeurs avant l'update
            old_values = {}
            state = inspect(target)
            for attr in state.attrs:
                hist = attr.load_history()
                if hist.has_changes() and hist.deleted:
                    old_values[attr.key] = hist.deleted[0]
            
            observer.updated(target, old_values)
        
        @event.listens_for(cls, 'after_delete')
        def after_delete(mapper, connection, target):
            observer.deleted(target)


# ==================== 5. MIDDLEWARE FASTAPI ====================
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour capturer l'IP et l'utilisateur courant
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Récupérer l'IP du client
        client_ip = request.client.host
        
        # Stocker dans le request state pour utilisation ultérieure
        request.state.client_ip = client_ip
        
        # Traiter la requête
        response = await call_next(request)
        
        return response


# ==================== 6. DÉPENDANCE POUR RÉCUPÉRER L'UTILISATEUR ====================
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Récupérer l'utilisateur courant depuis le token JWT
    À adapter selon votre système d'authentification
    """
    # TODO: Décoder le JWT et extraire l'user_id
    # Exemple simplifié:
    token = credentials.credentials
    # user_id = decode_jwt(token)
    user_id = 1  # Placeholder
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié"
        )
    
    # Stocker dans le contexte
    current_user_id.set(user_id)
    
    return user_id


# ==================== 7. EXEMPLE D'UTILISATION ====================
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

# Ajouter le middleware
app.add_middleware(LoggingMiddleware)

# Modèle exemple
class User(Base, ObservableMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100))
    email = Column(String(100))
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Enregistrer les observers au démarrage
@app.on_event("startup")
def startup_event():
    # Créer une session temporaire pour l'enregistrement
    db = SessionLocal()
    try:
        User.register_observers(db)
    finally:
        db.close()

# Route exemple
@app.post("/users")
async def create_user(
    nom: str,
    email: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
    request: Request = None
):
    """
    Créer un utilisateur - sera automatiquement loggé
    """
    # Optionnel: définir une action personnalisée
    ActionContext.set_action("user_registration")
    
    # Créer l'utilisateur
    user = User(nom=nom, email=email, password="hashed_password")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Le log est automatiquement créé grâce à l'observer !
    
    return {"id": user.id, "nom": user.nom}


@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    nom: str = None,
    email: str = None,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
    request: Request = None
):
    """
    Mettre à jour un utilisateur - sera automatiquement loggé
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Optionnel: définir un admin ID différent
    AdminAuthorization.set_admin_id(99)  # Admin qui autorise l'action
    
    # Mettre à jour
    if nom:
        user.nom = nom
    if email:
        user.email = email
    
    db.commit()
    db.refresh(user)
    
    # Le log est automatiquement créé avec les changements !
    
    return {"id": user.id, "nom": user.nom}


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Supprimer un utilisateur - sera automatiquement loggé
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    # Le log de suppression est automatiquement créé !
    
    return {"message": "User deleted successfully"}


# ==================== 8. FONCTION GET_DB ====================
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()