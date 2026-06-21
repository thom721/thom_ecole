from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
 
from datetime import datetime,date

# Schéma pour la ressource Paiement (équivalent à PaiementRessource)
class PaiementResource(BaseModel):
    id: str
    id_: str# = Field(None, alias="id_")
    identifiant: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    annee: str# = Field(..., alias="annee_academique")
    niveaux: Optional[str] = None
    classes: Optional[str] = None
    # mois: Dict[str, Any]
    # accessoires: Dict[str, Any] = Field(..., alias="paiement_details")
    
    class Config:
        from_attributes = True
        populate_by_name = True

# Schéma pour la métadonnée de pagination
class PaginationMeta(BaseModel):
    total: int
    current_page: int
    per_page: int
    total_pages: int
#     has_next: bool
#     has_prev: bool
#     next_page: Optional[int] = None
#     prev_page: Optional[int] = None

# Schéma pour la réponse paginée
class PaginatedPaiementResponse(BaseModel):
    data: List[PaiementResource]
    meta: dict

# Schéma pour les filtres/paramètres de requête
class PaiementFilterParams(BaseModel):
    search: Optional[str] = None
    page: Optional[int] = 1
    per_page: Optional[int] = 16
    annee_academique: Optional[str] = None
    niveau_id: Optional[str] = None
    classe: Optional[str] = None

class PaiementResourceShow(BaseModel):
    id: str  
    etudiant_id: Optional[str] = None  
    annee_academique:Optional[str] = None
    niveau_id: Optional[str] = None
    classe: Optional[str] = None
    mois: Dict[str, Any]
    accessoires: Dict[str, Any] = None
    paiement_details: Dict[str, Any] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

class ShowPaiementResponse(BaseModel):
    show_paiement:PaiementResourceShow
    class Config:
        from_attributes = True

# Modèles Pydantic
class StudentPaymentData(BaseModel):
    studentId: str
    nom: str
    prenom: str
    identifiant: str
    nom_classe: str
    classeId: str
    echeance: Optional[str] = None
    montant: Optional[float] = None
    devise: Optional[str] = None
    name: str
    niveauId: str
    date_debut: Optional[date] = None  # Garde le type date
    annee_academique: str
    anneeId: str
    date_fin: Optional[date] = None  # Garde le type date
    faculte_id: Optional[str] = None
    
    class Config:
        from_attributes = True  # Pour Pydantic v2 (ou from_attributes = True pour v1)

class StudentPaymentResponse(BaseModel):
    data: list[StudentPaymentData]


# Modèles Pydantic pour la requête
class PaymentInfoRequest(BaseModel):
    etudiant: str
    annee_academique: str  # Format: "2024-2025"
    classe: str
    niveau: str
    annee_a: str
    faculte: Optional[str] = None

# Modèles Pydantic pour la réponse
class PaymentInfoData(BaseModel):
    studentId: str
    nom: str
    prenom: str
    aide_financiere: Optional[str] = None
    identifiant: str
    classeId: str
    nom_classe: str
    annee_academique: str
    id: str
    echeance: Optional[str] = None
    devise: Optional[str] = None
    nb_echeance: Optional[str] = None
    montant: Optional[float] = None
    montant_par: Optional[Dict[str, Any]] = None
    # accessoires: Dict[str, Any] = None 
    name: str
    id_niveau: str
    date_debut: date
    date_fin: date
    paiement_details: Optional[Dict[str, Any]] = None
    mois: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class PaymentInfoResponse(BaseModel):
    data: Optional[PaymentInfoData]
    paiementExiste: bool
