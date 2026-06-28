"""
Helpers pour gérer le contexte de l'application (équivalent des Helpers Laravel)
"""
from contextvars import ContextVar
from typing import Optional
from app.dependencies.Dependencie import get_current_user

# Variables de contexte (thread-safe pour async)
current_user_id: ContextVar[Optional[str]] = ContextVar('current_user_id', default=None)
current_admin_id: ContextVar[Optional[str]] = ContextVar('current_admin_id', default=None)
custom_action: ContextVar[Optional[str]] = ContextVar('custom_action', default=None)
last_paiement_key: ContextVar[Optional[str]] = ContextVar('last_paiement_key', default=None)
action_reason: ContextVar[Optional[str]] = ContextVar('action_reason', default=None)


class ActionContext:
    """
    Helper pour gérer les actions personnalisées
    Équivalent de App\Helper\ActionPersonalisation dans Laravel
    """
    
    @staticmethod
    def set_action(action: str):
        """Définir une action personnalisée pour le prochain log"""
        custom_action.set(action)
    
    @staticmethod
    def get_action() -> Optional[str]:
        """Récupérer l'action personnalisée"""
        return custom_action.get()
    
    @staticmethod
    def clear():
        """Nettoyer l'action personnalisée"""
        custom_action.set(None)


class AdminAuthorization:
    """
    Helper pour gérer l'admin ID
    Équivalent de App\Helper\AdminAuthorization dans Laravel
    """
    
    @staticmethod
    def set_admin_id(admin_id: str):
        """Définir l'ID de l'admin qui autorise l'action"""
        current_admin_id.set(admin_id)
    
    @staticmethod
    def get_admin_id() -> Optional[str]:
        """Récupérer l'ID de l'admin"""
        return current_admin_id.get()
    
    @staticmethod
    def clear():
        """Nettoyer l'admin ID"""
        current_admin_id.set(None)


class UserContext:
    """
    Helper pour gérer l'utilisateur courant
    """
    
    @staticmethod
    def set_user_id(user_id: str):
        """Définir l'ID de l'utilisateur courant"""
        current_user_id.set(user_id)
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """Récupérer l'ID de l'utilisateur courant"""
        return current_user_id.get()
    
    @staticmethod
    def clear():
        """Nettoyer l'utilisateur courant"""
        current_user_id.set(None)


class ReasonContext:
    """
    Helper pour la raison saisie par l'utilisateur lors d'un retour de
    paiement ou d'une suppression de vente/dépense/transaction — reprise
    par global_observer.py dans le Log (colonne `reason`).
    """

    @staticmethod
    def set_reason(reason: str):
        """Définir la raison pour le prochain log"""
        action_reason.set(reason)

    @staticmethod
    def get_reason() -> Optional[str]:
        """Récupérer la raison"""
        return action_reason.get()

    @staticmethod
    def clear():
        """Nettoyer la raison"""
        action_reason.set(None)


class PaiementContext:
    """
    Helper pour gérer la clé de paiement
    """
    
    @staticmethod
    def set_paiement_key(key: str):
        """Définir la dernière clé de paiement"""
        last_paiement_key.set(key)
    
    @staticmethod
    def get_paiement_key() -> Optional[str]:
        """Récupérer la dernière clé de paiement"""
        return last_paiement_key.get()
    
    @staticmethod
    def clear():
        """Nettoyer la clé de paiement"""
        last_paiement_key.set(None)

