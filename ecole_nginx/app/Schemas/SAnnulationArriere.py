from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class AnnulationArriereRequest(BaseModel):
    paiement_id: str = Field(..., description="ID de la ligne Paiement (année) concernée — étudiant et année académique en sont dérivés côté serveur")
    type_annulation: str = Field(..., description="'partiel' ou 'total'")
    montant_annule: Optional[float] = Field(None, description="Montant à annuler si type_annulation='partiel'")
    ordonne_par: str = Field(..., min_length=2, max_length=255, description="Nom de la personne ayant ordonné l'annulation")
    ordonne_par_fonction: str = Field(..., min_length=2, max_length=255, description="Fonction de cette personne")
    raison: str = Field(..., min_length=20, max_length=150, description="Motif de la dérogation (20 à 150 caractères)")
    contrat_accepte: bool = Field(..., description="Case à cocher de l'attestation, doit être true")

    @field_validator('type_annulation')
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ('partiel', 'total'):
            raise ValueError("type_annulation doit être 'partiel' ou 'total'")
        return v

    @field_validator('contrat_accepte')
    @classmethod
    def validate_contrat(cls, v: bool) -> bool:
        if not v:
            raise ValueError("L'attestation doit être acceptée pour continuer")
        return v

    @model_validator(mode='after')
    def validate_montant_for_partiel(self):
        if self.type_annulation == 'partiel':
            if self.montant_annule is None or self.montant_annule <= 0:
                raise ValueError("Un montant supérieur à 0 est requis pour une annulation partielle")
        return self


class RevokeAnnulationArriereRequest(BaseModel):
    raison: str = Field(..., min_length=20, max_length=150, description="Motif de la révocation (20 à 150 caractères)")


class AnnulationArriereResponse(BaseModel):
    id: str
    etudiant_id: str
    annee_academique_id: str
    annee_academique: str
    type_annulation: str
    montant_annule: float
    ordonne_par: str
    ordonne_par_fonction: str
    executant_nom: str
    executant_role: Optional[str] = None
    raison: str
    statut: str
    annule_le: Optional[str] = None
    annule_raison: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
