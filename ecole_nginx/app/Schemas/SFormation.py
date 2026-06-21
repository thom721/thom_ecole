from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FormationBase(BaseModel):
    niveau:           str
    titre:            str
    duree:            Optional[str] = None
    couleur:          Optional[str] = '#3b82f6'
    image_url:        Optional[str] = None
    description:      Optional[str] = None
    matieres:         Optional[List[str]] = []
    nb_eleves_classe: Optional[str] = None
    taux_reussite:    Optional[str] = None
    nb_debouches:     Optional[str] = None
    debouches:        Optional[List[str]] = []
    niveau_id:        Optional[str] = None
    faculte_id:       Optional[str] = None
    ordre:            Optional[int] = 0
    is_published:     Optional[bool] = True

class FormationCreate(FormationBase):
    pass

class FormationUpdate(FormationBase):
    pass

class FormationResponse(FormationBase):
    id:         int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
