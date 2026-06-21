from pydantic import BaseModel, Field,computed_field
from typing import Optional
from datetime import datetime

# Schema pour la création
class ParamExamCreate(BaseModel):
    niveau_id: str
    annee_academique_id: str
    evaluation_par: str = Field(..., max_length=255)

# Schema pour la mise à jour
class ParamExamUpdate(BaseModel):
    niveau_id: Optional[str] = None
    annee_academique_id: Optional[str] = None
    evaluation_par: Optional[str] = Field(None, max_length=255)

# Schema pour la réponse (avec joins)
class ParamExamResponse(BaseModel):
    id: Optional[str] = None
    name: str = Field(alias="name")
    evaluation_par: str
    annee_academique: str
    niveau_id: str
    annee_academique_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @computed_field
    @property
    def niveau_name(self) -> str:
        return self.name 
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Pour accepter alias

# Schema pour la réponse paginée
class PaginatedResponse(BaseModel):
    data: list[ParamExamResponse]
    meta: dict

class ParamExamResponseOne(BaseModel):
    data: ParamExamResponse