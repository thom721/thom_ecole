from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ParametrePayrollSchema(BaseModel):
    id: str
    cours_id: str
    cours_nom: str
    taux_horaire: float
    # AnneeAcademique.id — même convention que Programme.annee_academique.
    annee_academique: str
    annee_academique_label: str = ""

    model_config = ConfigDict(from_attributes=True)


class ParametrePayrollCreateSchema(BaseModel):
    cours_id: str
    taux_horaire: float = Field(..., gt=0)
    annee_academique: str = Field(..., min_length=1, description="AnneeAcademique.id")


class ParametrePayrollUpdateSchema(BaseModel):
    taux_horaire: float = Field(..., gt=0)


class ParametrePayrollListResponse(BaseModel):
    data: list[ParametrePayrollSchema]
