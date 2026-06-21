from pydantic import BaseModel
from typing import List, Optional

class NiveauSchema(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class ClasseSchema(BaseModel):
    id: str
    nom_classe: str
    niveau_id: str

    class Config:
        from_attributes = True

class CoursSchema(BaseModel):
    id: str
    cours_nom: str

    class Config:
        from_attributes = True

class NiveauDetudeSchema(BaseModel):
    id: str
    niveau: str
    name: str
    annee_detude: str

    class Config:
        from_attributes = True

class FaculteSchema(BaseModel):
    id: str
    nom: str

    class Config:
        from_attributes = True

class NiveauResponse(BaseModel):
    niveau: Optional[NiveauSchema]
    niveau_detude: List[NiveauDetudeSchema]
    cours: List[CoursSchema]
    facultes: List[FaculteSchema]
    classe_actuelle: List[ClasseSchema]


