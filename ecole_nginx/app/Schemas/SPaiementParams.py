from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, Dict, Any, Union,List
from datetime import datetime 
from decimal import Decimal 
import json, ast


# Schema pour la création
class ParametrePaiementCreate(BaseModel):
    niveau_id: str
    faculte_id: Optional[str] = None
    classe: str = Field(..., max_length=255)
    montant: Optional[Decimal] = None
    devise: str = Field(..., max_length=255)
    nb_echeance: str = Field(..., max_length=255)
    anneeAcademique: Optional[str] = Field(None, max_length=255)
    echeance: str = Field(..., max_length=255)
    montant_par: Dict[str, Any]  # JSON field
    accessoires: Optional[Dict[str, Any]] = None  # JSON field

# Schema pour la mise à jour
class ParametrePaiementUpdate(BaseModel):
    niveau_id: Optional[str] = None
    faculte_id: Optional[str] = None
    classe: Optional[str] = Field(None, max_length=255)
    montant: Optional[Decimal] = None
    devise: Optional[str] = Field(None, max_length=255)
    nb_echeance: Optional[str] = Field(None, max_length=255)
    anneeAcademique: Optional[str] = Field(None, max_length=255)
    echeance: Optional[str] = Field(None, max_length=255)
    montant_par: Optional[Dict[str, Any]] = None
    accessoires: Optional[Dict[str, Any]] = None



class ParametrePaiementResponse(BaseModel):
    id: str
    montant: Optional[str|float|int] = None
    devise: str
    echeance: str
    paiement_par: Optional[str] = None
    montant_par: Dict[str, Any] | None = None

    @field_validator("montant_par", mode="before")
    def parse_montant_par(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return ast.literal_eval(v)
        return v
    niveau_id: str
    faculte_id: Optional[str] = None
    classe: str
    anneeAcademique: str
    nb_echeance: Optional[int] = None
    accessoires: Union[List[Any], Dict[str, Any]] = Field(default_factory=dict)  # Accepte liste ou dict
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Champs des joins
    niveau_name: Optional[str] = None
    nom_classe: Optional[str] = None
    nom_faculte: Optional[str] = None
    anneeAc: str
    
    class Config:
        from_attributes = True

# Schéma pour la pagination
class PaginatedParametrePaiementResponse(BaseModel):
    data: List[ParametrePaiementResponse]
    meta: dict

class ParametrePaiementResponseOne(BaseModel):
    data: ParametrePaiementResponse



#     meta: Dict[str, Any]
# Schema pour la réponse
# class ParametrePaiementResponse(BaseModel):
#     id: str
#     montant: Optional[Decimal] = None
#     devise: str
#     echeance: str
#     montant_par: Dict[str, Any]
#     niveau_id: str
#     faculte_id: Optional[str] = None
#     classe: str
#     anneeAcademique: Optional[str] = None
#     nb_echeance: str
#     accessoires: Optional[Dict[str, Any]] = None
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None
    
#     # Champs des relations (joins)
#     niveau_name: Optional[str] = None
#     nom_classe: Optional[str] = None
#     nom_faculte: Optional[str] = None
#     annee_academique: Optional[str] = None  # from annee_academiques
    
#     # Champ calculé comme dans ton Laravel
#     @computed_field
#     def montant_formatted(self) -> str:
#         """Retourne 'devise montant' si echeance == 'mois', sinon 'Autres'"""
#         if self.echeance == 'mois' and self.montant is not None:
#             return f"{self.devise} {self.montant}"
#         return "Autres"
    
#     class Config:
#         from_attributes = True
#         arbitrary_types_allowed = True  # Pour Decimal

# # Schema pour réponse paginée
# class PaginatedParametrePaiementResponse(BaseModel):
#     data: list[ParametrePaiementResponse]
#     meta: dict