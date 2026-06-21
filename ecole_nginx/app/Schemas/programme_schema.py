from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Schema pour la création
class ProgrammeCreate(BaseModel):
    professeur_id: str
    Cours_id: str
    Faculte_id: Optional[str] = None
    class_: Optional[str] = Field(None, max_length=255, alias="class")
    niveau_id: str
    session: Optional[str] = Field(None, max_length=255)
    heure: Optional[str] = Field(None, max_length=255)
    annee_academique: str = Field(..., max_length=255)
    jours: Optional[str] = Field(None, max_length=255)
    coefficients: Optional[float] = Field(None, max_length=255)
    note_de_passage: Optional[float] = None

# Schema pour la mise à jour
class ProgrammeUpdate(BaseModel):
    professeur_id: Optional[str] = None
    Cours_id: Optional[str] = None
    Faculte_id: Optional[str] = None
    class_: Optional[str] = Field(None, max_length=255, alias="class")
    niveau_id: Optional[str] = None
    session: Optional[str] = Field(None, max_length=255)
    heure: Optional[str] = Field(None, max_length=255)
    annee_academique: Optional[str] = Field(None, max_length=255)
    jours: Optional[str] = Field(None, max_length=255)
    coefficients: Optional[float] = Field(None, max_length=255)
    note_de_passage: Optional[float] = Field(None, max_length=255)


class ProgrammeResponse(BaseModel):
    id: Optional[str] = None
    cours: Optional[str] = Field(None, alias="cours")
    niveau_name: Optional[str] = None
    professeur: Optional[str] = None  # prof_nom + prenom
    classe: Optional[str] = None # Field(None, alias="nom_classe")
    annee_academique: Optional[str] = None
    
    # Champs additionnels pour les filtres
    niveau_id: Optional[str] = None
    class_: str
    coefficients: float
    note_de_passage: Optional[float] = None
    faculte_id: Optional[str] = None
    annee_academique_id: Optional[str] = None
    classe: Optional[str] = None
    professeur_id: Optional[str] = None
    Cours_id: Optional[str] = None
    session: Optional[str] = None
    heure: Optional[str] = None
    jours: Optional[str] = None
    fac_name: Optional[str] = None
    prof_nom: Optional[str] = None
    prenom: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Pour gérer les alias

# Schema pour réponse paginée
class PaginatedProgrammeResponse(BaseModel):
    data: List[ProgrammeResponse]
    meta: dict

class ProgrammeResponseOne(BaseModel):
    data:ProgrammeResponse


class ProgrammeCoursItem(BaseModel):
    id: Optional[str] = None
    cours_id: str
    professeur_id: str
    class_: str = Field(..., alias="class")
    niveau_id: str
    coefficients: Optional[float] = None
    faculte_id: Optional[str] = None
    annee_academique: str
    jours: Optional[str] = None
    heure: Optional[str] = None
    session: Optional[str] = None
    note_de_passage: Optional[float] = None

class ProgrammeCoursRequest(BaseModel):
    programmeCoursObject: list[ProgrammeCoursItem]
