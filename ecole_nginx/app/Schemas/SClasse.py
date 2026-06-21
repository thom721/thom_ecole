from pydantic import BaseModel, Field
from typing import Optional, Union, List
from datetime import datetime 

# Schema pour la création
class ClasseCreate(BaseModel):
    niveau_id: str
    nom_classe: str = Field(..., max_length=255)

# Schema pour la mise à jour
class ClasseUpdate(BaseModel):
    niveau_id: Optional[str] = None
    nom_classe: Optional[str] = Field(None, max_length=255)

# Schema pour la réponse
class ClasseResponse(BaseModel):
    id: str
    niveau: Optional[str] = None  # nom du niveau
    nom_classe: str
    niveau_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema pour réponse paginée
class PaginatedClasseResponse(BaseModel):
    data: List[ClasseResponse]
    meta: dict
class ClasseResponseOne(BaseModel):
    data: ClasseResponse