from pydantic import BaseModel, Field
from typing import List, Optional

class ClasseDetailResponse(BaseModel):
    """
    Schéma pour les détails d'une classe
    """
    classe_id: str = Field(..., description="ID de la classe")
    niveau_name: str = Field(..., description="Nom du niveau")
    nom_classe: str = Field(..., description="Nom de la classe")
    annee_academique_id: str = Field(..., description="ID de l'année académique")
    etudiant_count: int = Field(default=0, description="Nombre d'étudiants dans la classe")
    professeur: Optional[str] = Field(None, description="Nom complet du professeur principal")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "classe_id": "123e4567-e89b-12d3-a456-426614174000",
                "niveau_name": "Terminale",
                "nom_classe": "Terminale S1",
                "annee_academique_id": "123e4567-e89b-12d3-a456-426614174001",
                "etudiant_count": 35,
                "professeur": "Dupont Jean"
            }
        }


class DashboardResponse(BaseModel):
    """
    Schéma pour la réponse du dashboard principal
    Contient toutes les statistiques de l'établissement
    """
    etudiant: int = Field(..., description="Nombre total d'étudiants pour l'année académique")
    personnel: int = Field(..., description="Nombre total de personnel")
    cours: int = Field(..., description="Nombre total de cours")
    professeur: int = Field(..., description="Nombre total de professeurs")
    faculte: int = Field(..., description="Nombre total de facultés")
    classes: int = Field(..., description="Nombre total de classes actives")
    paiement: float = Field(..., description="Montant total des paiements du jour")
    devise: str = Field(default="GDES", description="Devise des paiements")
    id_annee: Optional[str] = Field(None, description="ID de l'année académique utilisée")
    classeDetails: List[ClasseDetailResponse] = Field(
        default_factory=list,
        description="Détails de toutes les classes avec leurs statistiques"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "etudiant": 450,
                "personnel": 35,
                "cours": 48,
                "professeur": 28,
                "faculte": 5,
                "classes": 12,
                "paiement": 125000.50,
                "devise": "GDES",
                "id_annee": "123e4567-e89b-12d3-a456-426614174001",
                "classeDetails": [
                    {
                        "classe_id": "123e4567-e89b-12d3-a456-426614174000",
                        "niveau_name": "Terminale",
                        "nom_classe": "Terminale S1",
                        "annee_academique_id": "123e4567-e89b-12d3-a456-426614174001",
                        "etudiant_count": 35,
                        "professeur": "Dupont Jean"
                    }
                ]
            }
        }


class DashboardStatsQuery(BaseModel):
    """
    Schéma pour les paramètres de requête du dashboard
    """
    search: Optional[str] = Field(
        None,
        description="ID de l'année académique à rechercher. Si non fourni, utilise l'année active (status=1)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "search": "123e4567-e89b-12d3-a456-426614174001"
            }
        }