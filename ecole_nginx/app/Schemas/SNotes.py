from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
import json 

class TypeMatiere(str, Enum):
    THEORIQUE = "theorique"
    PRATIQUE = "pratique"
    MIXTE = "mixte"
    BASE = "base"
    ORALE = "orale"

class TypeControle(str, Enum):
    MOIS = "mois"
    INTRA = "intra"
    FINALE = "finale"
    CONTR_I = "Contr. I"
    CONTR_II = "Contr. II"
    CONTR_III = "Contr. III"
    CONTR_IV = "Contr. IV"
    TRIMESTRE_I = "Trimestre I"
    TRIMESTRE_II = "Trimestre II"
    TRIMESTRE_III = "Trimestre III"


class NoteItemStore(BaseModel):
    id: str = Field(..., description="ID de l'étudiant")
    identifiant: str = Field(..., description="Identifiant de l'étudiant")
    note: float = Field(..., description="Note de l'étudiant")
    
    @field_validator('id', 'identifiant')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()
    
    @field_validator('note')
    @classmethod
    def validate_note(cls, v: float) -> float:
        if v < 0:
            raise ValueError("La note ne peut pas être négative")
        return v

class StoreNoteRequest(BaseModel):
    controle: Optional[str] = None
    examen: Optional[str] = None
    session: Optional[str] = None
    cours: str = Field(..., description="ID du cours")
    type_matiere: str = Field(..., description="Type de matière")
    coefficients: Optional[float] = None
    annee_academique: str = Field(..., description="Année académique")
    note_de_passage: Optional[float] = None
    professeur_id: str = Field(..., description="ID du professeur")
    notes: List[NoteItemStore] = Field(..., min_items=1, description="Liste des notes")
    
    @field_validator('cours', 'annee_academique', 'professeur_id', 'type_matiere')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()
    
    @field_validator('type_matiere')
    @classmethod
    def validate_type_matiere(cls, v: str) -> str:
        return v.lower().strip()
    
    @model_validator(mode='after')
    def validate_conditional_fields(self):
        """Validation conditionnelle des champs"""
        # examen est requis si session est null
        if self.session is None and self.examen is None:
            raise ValueError("Le champ 'examen' est requis lorsque 'session' est null")
        
        # session est requis si examen est null
        if self.examen is None and self.session is None:
            raise ValueError("Le champ 'session' est requis lorsque 'examen' est null")
        
        return self
    
    @model_validator(mode='after')
    def validate_notes_against_coefficients(self):
        """Valider que les notes ne dépassent pas le coefficient"""
        max_note = self.coefficients if self.coefficients else 200
        
        for idx, note_item in enumerate(self.notes):
            if note_item.note > max_note:
                raise ValueError(
                    f"La note de l'élève #{idx + 1} ne peut pas excéder {max_note}."
                )
        
        return self

class StoreNoteResponse(BaseModel):
    success: str

class StoreNoteErrorResponse(BaseModel):
    errors: Any  # Can be string or list