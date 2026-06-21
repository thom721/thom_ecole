from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, List
from enum import Enum
import re
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# Regex pour valider les clés de versement
VERSEMENT_KEY_REGEX = re.compile(r"^(\w+)_(\d+)_([a-f0-9-]+)$")

router = APIRouter()

# ==================== SCHEMAS ====================

# ==================== EXEMPLE DE REQUÊTE CORRIGÉE ====================
"""
Pour votre frontend, assurez-vous d'envoyer :

{
    "id": "8e832d8f-8671-489e-8f67-99c632919f79",
    "niveau_id": "e7f8b370-e3c5-11ef-9913-3e7db61a5f8d",
    "classe": null,  // ou omettez complètement cette clé
    "echeance": "Versement",
    "devise": "GDES",
    "anneeAcademique": "8ef65c55-8166-4557-bc2f-5482d605cd76",
    "nb_echeance": 4,  // NOMBRE, pas "4"
    "montant": null,   // ou omettez
    "montant_par": {
        "Versement_1_8ef65c55-8166-4557-bc2f-5482d605cd76": 18000,  // NOMBRE, pas "18000"
        "Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76": 8000,
        "Versement_3_8ef65c55-8166-4557-bc2f-5482d605cd76": 8000,
        "Versement_4_8ef65c55-8166-4557-bc2f-5482d605cd76": 8000
    },
    "accessoires": []
}

Si vous devez envoyer en form-data ou avec des strings, les validators ci-dessus
convertiront automatiquement les chaînes en types appropriés.
"""