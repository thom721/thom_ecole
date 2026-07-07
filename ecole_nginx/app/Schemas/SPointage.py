from typing import Optional
from pydantic import BaseModel


class PointagePersonneSchema(BaseModel):
    user_id: str
    nom: str
    prenom: str
    type: str
    heure_arrivee: Optional[str] = None
    heure_depart: Optional[str] = None


class PointagePersonnelListResponse(BaseModel):
    data: list[PointagePersonneSchema]


class PointageActionSchema(BaseModel):
    user_id: str


class PointageHistoriqueEntry(BaseModel):
    date: str
    heure_arrivee: Optional[str] = None
    heure_depart: Optional[str] = None
    duree_heures: Optional[float] = None


class PointageHistoriqueResponse(BaseModel):
    data: list[PointageHistoriqueEntry]
    total_heures: float
