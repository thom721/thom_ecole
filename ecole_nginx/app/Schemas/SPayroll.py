from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


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
        )

    model_config = ConfigDict(from_attributes=True)


class PayrollCreateSchema(BaseModel):
    user_id: str
    montant: float = Field(..., gt=0)
    mois: str = Field(..., min_length=1, max_length=20)
    annee: str = Field(..., min_length=4, max_length=4)
    methode_paiement: str = Field(..., pattern="^(Chèque|Espèce)$")


class PaginatedPayrollResponse(BaseModel):
    data: list[PayrollSchema]
    meta: dict
