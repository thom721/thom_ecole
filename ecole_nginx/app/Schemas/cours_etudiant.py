from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
 

# Schema pour la réponse
class CoursEtudiantResponse(BaseModel):
    id: str
    identifiant: Optional[str] = None
    fname: str # = #Field(None, alias="nom")  # nom de l'étudiant
    lname: str # = #Field(None, alias="prenom")  # prénom de l'étudiant
    annee_academique: str
    name: Optional[str] = None  # nom du niveau
    classe: Optional[str] = None  # ID de la classe
    nom_classe: Optional[str] = None  # nom de la classe
    evaluation_par: Optional[str] = None
    fac_name: Optional[str] = None  # nom de la faculté
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # data_etudiant: Optional[Dict[str, Any]] = None  # JSON field
    
    class Config:
        from_attributes = True
        populate_by_name = True

# Schema pour réponse paginée
class PaginatedCoursEtudiantResponse(BaseModel):
    data: List[CoursEtudiantResponse]
    meta: dict

 
# ============================================================================
#  KOUMANSMAN ETAP 1
# ============================================================================

class AddNoteRequest(BaseModel):
    niveau: str = Field(..., description="ID du niveau")
    cours: str = Field(..., description="ID du cours")
    class_: str = Field(..., alias="class", description="ID de la classe")
    annee_academique: str = Field(..., description="ID de l'année académique")
    session: Optional[str] = None
    faculte: Optional[str] = None
    
    @field_validator('niveau', 'cours', 'class_', 'annee_academique')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()

class EtudiantNoteData(BaseModel):
    id: str
    nom: str
    prenom: str
    identifiant: str
    annee_academique: str
    niveauId: str
    nom_classe: str
    name: str
    annee_academique_id: str
    classes_id: str
    niveau_id: str
    facName: Optional[str] = None
    facId: Optional[str] = None
    
    class Config:
        from_attributes = True

class CoursNoteData(BaseModel):
    cours_nom: str
    session: Optional[str] = None
    note_de_passage: Optional[float] = None
    nom_classe: str
    coefficients: Optional[float] = None
    type_matiere: Optional[str] = None
    professeur_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class ExamEcheanceData(BaseModel):
    name: str
    evaluation_par: str
    
    class Config:
        from_attributes = True

class AddNoteResponse(BaseModel):
    datas: Dict[str, Any]

class ErrorResponse(BaseModel):
    errors: Dict[str, str]

# ============================================================================
#  FINISMAN ETAP 1
# ============================================================================

# ============================================================================
#  KOUMANSMAN ETAP 2
# ============================================================================
class NoteItem(BaseModel):
    id: str = Field(..., description="ID de l'étudiant")
    identifiant: str = Field(..., description="Identifiant de l'étudiant")
    
    @field_validator('id', 'identifiant')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "identifiant": "ETU2024001"
            }
        }

class EditNoteRequest(BaseModel):
    cours: str = Field(..., description="ID du cours")
    annee_academique: str = Field(..., description="Année académique")
    examen: Optional[str] = Field(None, description="Type d'examen")
    type_matiere: str = Field(..., description="Type de matière")
    notes: List[NoteItem] = Field(..., min_items=1, description="Liste des notes à éditer")
    
    @field_validator('cours', 'annee_academique', 'type_matiere')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()
    
    @field_validator('type_matiere')
    @classmethod
    def validate_type_matiere(cls, v: str) -> str:
        v = v.lower().strip()
        valid_types = ['base', 'orale','theorique', 'pratique', 'mixte']
        if v not in valid_types:
            raise ValueError(f"Le type de matière doit être l'un de: {', '.join(valid_types)}")
        return v

class EtudiantNoteResult(BaseModel):
    etudiant_id: str
    note: float

class EditNoteResponse(BaseModel):
    success: List[EtudiantNoteResult]

class EditNoteErrorResponse(BaseModel):
    errors: List[str]
    errors_: Optional[str] = None
# ============================================================================
#  FINISMAN ETAP 2
# ============================================================================


# ============================================================================
#  KOUMANSMAN ETAP 3
# ============================================================================

# ============================================================================
#  FINISMAN ETAP 3
# ============================================================================