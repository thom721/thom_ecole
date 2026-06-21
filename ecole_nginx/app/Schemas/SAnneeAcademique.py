from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime, date 

# Base schema
class AnneeAcademiqueBase(BaseModel):
    date_debut: date
    date_fin: date
    niveau_detude: str = Field(..., max_length=255)
    annee_academique: str = Field(..., max_length=255)
    status: bool = True

# Schema pour la création
class AnneeAcademiqueCreate(AnneeAcademiqueBase):
    pass

# Schema pour la mise à jour
class AnneeAcademiqueUpdate(BaseModel):
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    niveau_detude: Optional[str] = Field(None, max_length=255)
    annee_academique: Optional[str] = Field(None, max_length=255)
    status: Optional[bool] = None

# Schema pour la réponse AVEC décorateur
class AnneeAcademiqueResponse(BaseModel):
    id: str
    date_debut: date
    date_fin: date
    niveau_detude: str
    annee_academique: str
    status: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Champ calculé avec @computed_field (Pydantic v2)
    @computed_field
    def status_text(self) -> str:
        """Retourne 'Actif' ou 'Inactif' basé sur status boolean"""
        return 'Actif' if self.status else 'Inactif'
    
    # Version avec le décorateur personnalisé
#     @with_status_text
#     def to_dict(self) -> dict:
#         """Retourne le dict avec status_text ajouté par le décorateur"""
#         return self.model_dump()
    
    class Config:
        from_attributes = True

# Schema pour réponse paginée
class PaginatedAnneeAcademiqueResponse(BaseModel):
    data: list[AnneeAcademiqueResponse]
    meta: dict

class AnneeAcademiqueResponseOne(BaseModel):
    data:AnneeAcademiqueResponse