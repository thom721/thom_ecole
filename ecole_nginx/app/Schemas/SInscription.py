from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime 
from decimal import Decimal

# Schema pour la création
class FraisInscriptionCreate(BaseModel):
    prix: Decimal = Field(..., ge=0, description="Prix de l'inscription")
    niveau_id: str
    anneeAc: str = Field(..., description="ID de l'année académique")

# Schema pour la mise à jour
class FraisInscriptionUpdate(BaseModel):
    prix: Optional[Decimal] = Field(None, ge=0)
    niveau_id: Optional[str] = None
    anneeAc: Optional[str] = None

# Schema pour la réponse (avec relations)
class FraisInscriptionResponse(BaseModel):
    id: str
    prix: Decimal
    niveau: Optional[str] = None  # nom du niveau
    description: Optional[str] = None  # nom du niveau
    annee_academique: Optional[str] = None  # texte de l'année académique
    niveau_id: Optional[str] = None
    anneeAc: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True  # Pour Decimal

# Schema pour réponse paginée
class PaginatedFraisInscriptionResponse(BaseModel):
    data: list[FraisInscriptionResponse]
    meta: dict

class FraisInscriptionResponseOne(BaseModel):
    data:FraisInscriptionResponse