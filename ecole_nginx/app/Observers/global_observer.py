"""
Observateur global pour logger automatiquement les actions CRUD
"""
import json
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from datetime import datetime
import uuid
from fastapi.encoders import jsonable_encoder
from app.Models.MSystems import Log
from app.Helper.context import (
    ActionContext,
    AdminAuthorization,
    UserContext,
    PaiementContext,
    ReasonContext
)


class GlobalModelObserver:
    """
    Observateur global pour logger automatiquement les actions CRUD sur les modèles
    Équivalent de App\Observers\GlobalModelObserver dans Laravel
    """
    
    EXCLUDED_FIELDS = ['password', 'remember_token', 'updated_at', 'created_at','password_changed_at']
    
    def __init__(self, db: Session, request_ip: str = None):
        self.db = db
        self.request_ip = request_ip
    
    def sanitize_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Exclure les champs sensibles des logs"""
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
        """Récupérer uniquement les champs modifiés d'un modèle"""
        state = inspect(model)
        changes = {}
        
        for attr in state.attrs:
            hist = attr.load_history()
            if hist.has_changes():
                changes[attr.key] = attr.value
        
        return changes
    
    def json_diff(self, old: Dict, new: Dict) -> Dict:
        """
        Calculer la différence entre deux dictionnaires JSON
        Retourne uniquement les modifications
        """
        diff = {}
        
        for key, value in new.items():
            if key not in old:
                # Clé ajoutée
                diff[key] = value
            elif isinstance(value, dict) and isinstance(old[key], dict):
                # Comparaison récursive pour les sous-dictionnaires
                sub_diff = self.json_diff(old[key], value)
                if sub_diff:
                    diff[key] = sub_diff
            elif old[key] != value:
                # Valeur modifiée
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
        user_id = UserContext.get_user_id()
        if ActionContext.get_action() != "Connect Autorisation":
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
                
                # Convertir en dict si nécessaire
                if isinstance(old_json, str):
                    old_json = json.loads(old_json)
                if isinstance(new_json, str):
                    new_json = json.loads(new_json)
                
                # Calculer la différence
                diff = self.json_diff(old_json, new_json)
                if not diff:
                    return  # Pas de changement réel
                
                new_sanitized['paiement_details'] = diff
        
        # Récupérer les valeurs du contexte
        final_action = ActionContext.get_action() or action
        auth_id = AdminAuthorization.get_admin_id() or user_id
        paiement_key = getattr(model, 'last_paiement_key', None) or PaiementContext.get_paiement_key()

        if ActionContext.get_action() != "Connect Autorisation":
        # Créer le log
            log_entry = Log(
                action=final_action,
                user_id=user_id,
                authorization_id=auth_id,
                paiement_key=paiement_key,
                reason=ReasonContext.get_reason(),
                model_type=f"{model.__class__.__module__}.{model.__class__.__name__}",
                model_id=model.id,
                old_values=jsonable_encoder(old_sanitized) if old_sanitized else None,
                new_values=jsonable_encoder(new_sanitized) if new_sanitized else None,
                ip_address=self.request_ip
            )

            self.db.add(log_entry)
            self.db.commit()

            # Nettoyer le contexte
            AdminAuthorization.clear()
            ActionContext.clear()
            PaiementContext.clear()
            ReasonContext.clear()

        # from fastapi.encoders import jsonable_encoder

        # # Cette fonction de FastAPI transforme TOUT (dates, UUIDs, etc.) 
        # # en formats compatibles JSON (str, int, float)
        # clean_log_data = jsonable_encoder(etudiant_data)
