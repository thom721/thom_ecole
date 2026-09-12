from pydantic import BaseModel, Field,computed_field
from typing import Optional, Union, List
from datetime import datetime
 

# Schema pour la création
class CoursCreate(BaseModel):
    cours_nom: str = Field(..., max_length=255)
    note_de_passage: Optional[str] = Field(None, max_length=255)
    coefficients: Optional[str] = Field(None, max_length=255)
    niveau_id: Optional[str] = None
    type_matiere: str = Field("base", max_length=255)

class CourseItem(BaseModel):
    id: Optional[str] = None
    cours_nom: str
    niveau_id: Optional[str] = None
    note_de_passage: Optional[str] = None
    coefficients: Optional[str] = None
    type_matiere: Optional[str] = None
    # Système à crédits (niveau "Universitaire" uniquement, voir
    # app/Models/MCredits.py) — nullable pour les autres niveaux.
    credits: Optional[float] = None
    # Nombre de reprises autorisées avant blocage automatique d'une nouvelle
    # inscription à ce cours (voir RCredits.py::creer_inscription). NULL =
    # aucune limite.
    reprises_max: Optional[int] = None
    # Prérequis de ce cours (liste d'id Cours) — None = ne pas toucher aux
    # prérequis existants (ex: mise à jour d'autre chose sans y penser),
    # [] = retirer tous les prérequis, sinon reconcilié tel quel (voir
    # RCours.py::store_cours).
    prerequis_ids: Optional[List[str]] = None
    # Poids de la phase Intra dans la note globale (système à crédits,
    # Universitaire uniquement) — voir RCredits.py::saisir_note_credits.
    poids_intra_percent: Optional[float] = None

class CoursesRequest(BaseModel):
    CoursesObject: list[CourseItem]

class CourseUpdateRequest(BaseModel):
    id: Optional[str]=None
    cours_nom: str
    coefficients: Optional[str] = None
    niveau_id: Optional[str] = None
    type_matiere: Optional[str] = None

# Schema pour la mise à jour
class CoursUpdate(BaseModel):
    cours_nom: Optional[str] = Field(None, max_length=255)
    note_de_passage: Optional[str] = Field(None, max_length=255)
    coefficients: Optional[str] = Field(None, max_length=255)
    niveau_id: Optional[str] = None
    type_matiere: Optional[str] = Field(None, max_length=255)

# Schema pour la réponse
class CoursResponse(BaseModel):
    id: str
    cours_nom: str
    type_matiere: str
    # date: Optional[datetime] = Field(None, alias="created_at")
    note_de_passage: Optional[str] = None
    coefficients: Optional[str] = None
    credits: Optional[float] = None
    reprises_max: Optional[int] = None
    prerequis_ids: Optional[List[str]] = None
    poids_intra_percent: Optional[float] = None
    niveau_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
 
    @computed_field
    @property
    def date(self) -> str:
        if self.created_at:
            return self.created_at.strftime("%d %b %Y")  # ex: 14 Jan 2026
        return ""
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Pour gérer les alias

# Schema pour réponse paginée
class PaginatedCoursResponse(BaseModel):
    data: List[CoursResponse]
    meta: dict

class CoursResponseSchema(BaseModel):
    id: str
    cours_nom: str

class simpleCoursResponse(BaseModel):
    cours: List[CoursResponseSchema]

class CoursResponseSchemaOne(BaseModel):
    data: CoursResponse
