# app/schemas/financial.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

# ============= SCHEMAS PAIEMENT =============

class PaiementBase(BaseModel):
    etudiant_id: str
    annee_academique: str
    classe: str
    faculte_id: Optional[str] = None
    cours: Optional[str] = None
    niveau_id: str
    mois: Dict[str, Any]
    paiement_details: Dict[str, Any]
    last_paiement_key: Optional[str] = None

class PaiementCreate(PaiementBase):
    pass

class PaiementUpdate(BaseModel):
    annee_academique: Optional[str] = None
    classe: Optional[str] = None
    faculte_id: Optional[str] = None
    cours: Optional[str] = None
    niveau_id: Optional[str] = None
    mois: Optional[Dict[str, Any]] = None
    paiement_details: Optional[Dict[str, Any]] = None
    last_paiement_key: Optional[str] = None

class PaiementResponse(PaiementBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS PARAMETRE PAIEMENT =============

class ParametrePaiementBase(BaseModel):
    niveau_id: str
    faculte_id: Optional[str] = None
    classe: str
    montant: Optional[Decimal] = None
    devise: str
    nb_echeance: str
    anneeAcademique: Optional[str] = None
    echeance: str
    montant_par: Dict[str, Any]
    accessoires: Optional[Dict[str, Any]] = None

class ParametrePaiementCreate(ParametrePaiementBase):
    pass

class ParametrePaiementUpdate(BaseModel):
    niveau_id: Optional[str] = None
    faculte_id: Optional[str] = None
    classe: Optional[str] = None
    montant: Optional[Decimal] = None
    devise: Optional[str] = None
    nb_echeance: Optional[str] = None
    anneeAcademique: Optional[str] = None
    echeance: Optional[str] = None
    montant_par: Optional[Dict[str, Any]] = None
    accessoires: Optional[Dict[str, Any]] = None

class ParametrePaiementResponse(ParametrePaiementBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS FRAIS INSCRIPTION =============

class FraisInscriptionBase(BaseModel):
    prix: Decimal
    niveau_id: str
    anneeAc: str

class FraisInscriptionCreate(FraisInscriptionBase):
    pass

class FraisInscriptionUpdate(BaseModel):
    prix: Optional[Decimal] = None
    niveau_id: Optional[str] = None
    anneeAc: Optional[str] = None

class FraisInscriptionResponse(FraisInscriptionBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS FRAIS DIVERS =============

class FraisDiversBase(BaseModel):
    anneeAc: str
    niveau_id: str
    description: str
    prix: float

class FraisDiversCreate(FraisDiversBase):
    pass

class FraisDiversUpdate(BaseModel):
    anneeAc: Optional[str] = None
    niveau_id: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = None

class FraisDiversResponse(FraisDiversBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS DEPENSE =============

class DepenseBase(BaseModel):
    description: str
    prix: Decimal
    user_id: str

class DepenseCreate(DepenseBase):
    pass

class DepenseUpdate(BaseModel):
    description: Optional[str] = None
    prix: Optional[Decimal] = None

class DepenseResponse(DepenseBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS VENTE =============

class VenteBase(BaseModel):
    nom: Optional[str] = None
    category: Optional[str] = None
    prix: Optional[Decimal] = None
    quantite: Optional[str] = None
    total: Optional[Decimal] = None
    user_id: str
    etudiant_id: str
    status: str = "En attente"
    order_itemId: int

class VenteCreate(VenteBase):
    pass

class VenteUpdate(BaseModel):
    nom: Optional[str] = None
    category: Optional[str] = None
    prix: Optional[Decimal] = None
    quantite: Optional[str] = None
    total: Optional[Decimal] = None
    status: Optional[str] = None

class VenteResponse(VenteBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS ORDER ITEM =============

class OrderItemBase(BaseModel):
    nom: str
    category: str
    prix: Decimal
    quantite: str
    total: Decimal
    user_id: str
    vente_id: str
    status: bool = True

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    nom: Optional[str] = None
    category: Optional[str] = None
    prix: Optional[Decimal] = None
    quantite: Optional[str] = None
    total: Optional[Decimal] = None
    status: Optional[bool] = None

class OrderItemResponse(OrderItemBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True