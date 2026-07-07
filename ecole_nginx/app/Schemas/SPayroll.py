from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PayrollVersementSchema(BaseModel):
    id: str
    montant: float
    date_versement: str
    methode_paiement: Optional[str] = None
    note: Optional[str] = None

    @classmethod
    def from_model(cls, v):
        return cls(
            id=v.id,
            montant=float(v.montant),
            date_versement=v.date_versement.strftime("%Y-%m-%d"),
            methode_paiement=v.methode_paiement,
            note=v.note,
        )

    model_config = ConfigDict(from_attributes=True)


class PayrollSchema(BaseModel):
    id: str
    user_id: str
    user: str
    montant: float
    mois: str
    annee: str
    methode_paiement: str
    statut: str
    date_versement: Optional[str] = None
    date: str
    type_calcul: str = "fixe"
    montant_du: Optional[float] = None
    remaining_balance: Optional[float] = None
    details_horaires: Optional[list] = None
    heures_pointees_ref: Optional[float] = None
    versements: list[PayrollVersementSchema] = []

    @classmethod
    def from_model(cls, p):
        return cls(
            id=p.id,
            user_id=p.user_id,
            user=p.user.name if p.user else "",
            montant=float(p.montant),
            mois=p.mois,
            annee=p.annee,
            methode_paiement=p.methode_paiement,
            statut=p.statut,
            date_versement=p.date_versement.strftime("%Y-%m-%d %H:%M") if p.date_versement else None,
            date=p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "",
            type_calcul=p.type_calcul or "fixe",
            montant_du=float(p.montant_du) if p.montant_du is not None else None,
            remaining_balance=float(p.remaining_balance) if p.remaining_balance is not None else None,
            details_horaires=p.details_horaires,
            heures_pointees_ref=float(p.heures_pointees_ref) if p.heures_pointees_ref is not None else None,
            versements=[PayrollVersementSchema.from_model(v) for v in (p.versements or [])],
        )

    model_config = ConfigDict(from_attributes=True)


class PayrollLigneHoraireSchema(BaseModel):
    cours_id: str
    heures: float = Field(..., gt=0)


class PayrollCreateSchema(BaseModel):
    user_id: str
    mois: str = Field(..., min_length=1, max_length=20)
    annee: str = Field(..., min_length=4, max_length=4)
    methode_paiement: str = Field(..., pattern="^(Chèque|Espèce)$")
    type_calcul: str = Field("fixe", pattern="^(fixe|horaire)$")
    montant: Optional[float] = Field(None, gt=0)
    # Année académique (AnneeAcademique.id, format utilisé par Programme et
    # ParametrePayroll) — distincte de `annee` (année civile de la période
    # de paie) : un professeur enseigne des cours rattachés à une année
    # académique ("2025/2026"), pas à une année civile.
    annee_academique_id: Optional[str] = None
    details_horaires: Optional[list[PayrollLigneHoraireSchema]] = None


class PayrollVersementCreateSchema(BaseModel):
    payroll_id: str
    montant: float = Field(..., gt=0)
    methode_paiement: str = Field(..., pattern="^(Chèque|Espèce)$")
    note: Optional[str] = None


class PaginatedPayrollResponse(BaseModel):
    data: list[PayrollSchema]
    meta: dict
