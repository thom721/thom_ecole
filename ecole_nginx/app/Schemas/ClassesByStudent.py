# app/schemas/etudiant.py (ajoutez ces schémas au fichier existant)
from pydantic import BaseModel, Field, UUID4
from typing import Optional,List

# ... (schémas existants) ...

# ============= SCHEMAS POUR ÉTUDIANTS PAR CLASSE =============

class StudentsByClasseRequest(BaseModel):
    """
    Schéma pour la requête de récupération des étudiants par classe.
    Utilisé pour la validation des données POST.
    """
    classe_id: str = Field(
        ..., 
        description="UUID de la classe",
        min_length=36,
        max_length=36
    )
    annee_id: str = Field(
        ..., 
        description="UUID de l'année académique",
        min_length=36,
        max_length=36
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "classe_id": "123e4567-e89b-12d3-a456-426614174000",
                "annee_id": "223e4567-e89b-12d3-a456-426614174001"
            }
        }


class EtudiantClasseResponse(BaseModel):
    """
    Schéma pour la réponse des étudiants dans une classe.
    Contient les informations de base de l'étudiant et son statut dans la classe.
    """
    id: str = Field(..., description="UUID de l'étudiant")
    identifiant: str = Field(..., description="Identifiant unique de l'étudiant")
    nom: str = Field(..., description="Nom de famille de l'étudiant")
    prenom: str = Field(..., description="Prénom de l'étudiant")
    sexe: str = Field(..., description="Sexe de l'étudiant (M/F)")
    id_cls_etudiant: str = Field(
        ..., 
        description="UUID de l'enregistrement dans classes_etudiants"
    )
    status_cls_etudiant: bool = Field(
        ..., 
        description="Statut de l'étudiant dans la classe (True=actif, False=inactif)"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "identifiant": "ETU001",
                "nom": "Doe",
                "prenom": "John",
                "sexe": "M",
                "id_cls_etudiant": "323e4567-e89b-12d3-a456-426614174002",
                "status_cls_etudiant": True
            }
        }

class EtudiantClasseResponseAll(BaseModel):
    data:List[EtudiantClasseResponse]
    class Config:
        from_attributes = True

class ClasseStatisticsResponse(BaseModel):
    """
    Schéma pour les statistiques d'une classe.
    """
    classe_id: str = Field(..., description="UUID de la classe")
    annee_id: str = Field(..., description="UUID de l'année académique")
    classe_nom: str = Field(..., description="Nom de la classe")
    annee_academique: str = Field(..., description="Libellé de l'année académique")
    total_etudiants: int = Field(..., description="Nombre total d'étudiants")
    repartition_sexe: dict = Field(
        ..., 
        description="Répartition des étudiants par sexe"
    )
    repartition_status: dict = Field(
        ..., 
        description="Répartition des étudiants par statut"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "classe_id": "123e4567-e89b-12d3-a456-426614174000",
                "annee_id": "223e4567-e89b-12d3-a456-426614174001",
                "classe_nom": "Terminale S1",
                "annee_academique": "2024-2025",
                "total_etudiants": 35,
                "repartition_sexe": {
                    "M": 18,
                    "F": 17
                },
                "repartition_status": {
                    "True": 33,
                    "False": 2
                }
            }
        }


class EtudiantClasseDetailResponse(EtudiantClasseResponse):
    """
    Schéma étendu avec plus de détails sur l'étudiant.
    """
    telephone: Optional[str] = Field(None, description="Numéro de téléphone")
    email: Optional[str] = Field(None, description="Email de l'étudiant")
    adresse: str = Field(..., description="Adresse de l'étudiant")
    date_de_naissance: str = Field(..., description="Date de naissance")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "identifiant": "ETU001",
                "nom": "Doe",
                "prenom": "John",
                "sexe": "M",
                "id_cls_etudiant": "323e4567-e89b-12d3-a456-426614174002",
                "status_cls_etudiant": True,
                "telephone": "+50912345678",
                "email": "john.doe@example.com",
                "adresse": "123 Rue Example",
                "date_de_naissance": "2000-01-01"
            }
        }


# ============= SCHEMAS POUR FILTRAGE AVANCÉ =============

class StudentsByClasseFilters(BaseModel):
    """
    Schéma pour le filtrage avancé des étudiants par classe.
    """
    classe_id: str = Field(..., description="UUID de la classe")
    annee_id: str = Field(..., description="UUID de l'année académique")
    sexe: Optional[str] = Field(None, description="Filtrer par sexe (M/F)")
    status: Optional[bool] = Field(None, description="Filtrer par statut")
    nom_search: Optional[str] = Field(None, description="Recherche dans le nom")
    prenom_search: Optional[str] = Field(None, description="Recherche dans le prénom")
    
    class Config:
        json_schema_extra = {
            "example": {
                "classe_id": "123e4567-e89b-12d3-a456-426614174000",
                "annee_id": "223e4567-e89b-12d3-a456-426614174001",
                "sexe": "M",
                "status": True,
                "nom_search": "Doe"
            }
        }


class BulkStudentStatusUpdate(BaseModel):
    """
    Schéma pour la mise à jour en masse du statut des étudiants.
    """
    etudiant_ids: list[str] = Field(
        ..., 
        description="Liste des UUIDs des étudiants à mettre à jour"
    )
    new_status: bool = Field(..., description="Nouveau statut à appliquer")
    
    class Config:
        json_schema_extra = {
            "example": {
                "etudiant_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "223e4567-e89b-12d3-a456-426614174001"
                ],
                "new_status": False
            }
        }


class StudentClasseAssignment(BaseModel):
    """
    Schéma pour assigner un étudiant à une classe.
    """
    etudiant_id: str = Field(..., description="UUID de l'étudiant")
    classe_id: str = Field(..., description="UUID de la classe")
    annee_id: str = Field(..., description="UUID de l'année académique")
    niveau_id: str = Field(..., description="UUID du niveau")
    status: bool = Field(default=True, description="Statut initial")
    
    class Config:
        json_schema_extra = {
            "example": {
                "etudiant_id": "123e4567-e89b-12d3-a456-426614174000",
                "classe_id": "223e4567-e89b-12d3-a456-426614174001",
                "annee_id": "323e4567-e89b-12d3-a456-426614174002",
                "niveau_id": "423e4567-e89b-12d3-a456-426614174003",
                "status": True
            }
        }