from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session


def authorize_with_admin_token(token: str, permission: str, db: Session):
    """Vérifie les permissions de l'utilisateur"""
    # Implémentez votre logique d'autorisation ici
    # Exemple simplifié:
    if not token:
        raise HTTPException(status_code=401, detail="Token manquant")
    
    # Vérifier le token et les permissions
    # ... votre logique ...
    
    return True


