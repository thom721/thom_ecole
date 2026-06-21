# app/schemas/academic.py
from pydantic import BaseModel, computed_field,Field,EmailStr,validator,model_validator
from typing import Optional,List,Dict
from datetime import datetime, date
from .UserSchema import UserResponse

# ============= SCHEMAS ANNEE ACADEMIQUE =============

class AnneeAcademiqueBase(BaseModel):
    date_debut: date
    date_fin: date
    niveau_detude: str
    annee_academique: str
    status: bool = True



class AnneeAcademiqueCreate(AnneeAcademiqueBase):
    pass

class AnneeAcademiqueUpdate(BaseModel):
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    niveau_detude: Optional[str] = None
    annee_academique: Optional[str] = None
    status: Optional[bool] = None

class AnneeAcademiqueSchema(AnneeAcademiqueBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AnneeAcademiqueResponse(BaseModel):
    data:List[AnneeAcademiqueSchema]

    class Config:
        from_attributes = True

# ============= SCHEMAS NIVEAU =============

class NiveauBase(BaseModel):
    name: Optional[str]=None
    status: bool = True

class NiveauCreate(NiveauBase):
    pass

class NiveauUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None

class NiveauResponseShema(NiveauBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class NiveauResponse(NiveauBase):
    data: List[NiveauResponseShema]
    
    class Config:
        from_attributes = True

# ============= SCHEMAS FACULTE =============

class FaculteBase(BaseModel):
    nom: str
    nb_annee: str
    status: bool = False

class FaculteCreate(FaculteBase):
    pass

class FaculteUpdate(BaseModel):
    nom: Optional[str] = None
    nb_annee: Optional[str] = None
    status: Optional[bool] = None

class FaculteResponseSchema(FaculteBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class FaculteResponse(BaseModel):
    data: List[FaculteResponseSchema]
    
    class Config:
        from_attributes = True

 

class FaculteResponseOne(BaseModel):
    data: FaculteResponseSchema
    
    class Config:
        from_attributes = True

# ============= SCHEMAS CLASSE =============

class ClasseBase(BaseModel):
    niveau_id: Optional[str]=None
    nom_classe: Optional[str]=None

class ClasseCreate(ClasseBase):
    pass

class ClasseUpdate(BaseModel):
    niveau_id: Optional[str] = None
    nom_classe: Optional[str] = None

class ClasseResponseSchema(ClasseBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ClasseResponse(ClasseBase):
    data: List[ClasseResponseSchema]
    


# ============= SCHEMAS COURS =============

class CoursBase(BaseModel):
    cours_nom: str
    note_de_passage: Optional[str] = None
    coefficients: Optional[str] = None
    niveau_id: Optional[str] = None
    type_matiere: str = "base"

class CoursCreate(CoursBase):
    pass

class CoursUpdate(BaseModel):
    cours_nom: Optional[str] = None
    note_de_passage: Optional[str] = None
    coefficients: Optional[str] = None
    niveau_id: Optional[str] = None
    type_matiere: Optional[str] = None

class CoursResponse(CoursBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS PROFESSEUR =============

class ProfesseurBase(BaseModel):
    nom: str
    prenom: str
    sexe: str
    email: str
    telephone: str
    adresse: str
    matiere_enseignee: Optional[str] = None
    status: bool = False

class ProfesseurCreate(ProfesseurBase):
    pass

class ProfesseurUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sexe: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    matiere_enseignee: Optional[str] = None
    status: Optional[bool] = None

class ProfesseurResponse(ProfesseurBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: UserResponse | None

    @computed_field
    @property
    def status_(self) -> str:
        if self.user and self.user.status:
            return "Actif"
        return "Inactif"
    
    class Config:
        from_attributes = True

class ProfesseurResponseShow(BaseModel):
    data:ProfesseurResponse

class ProfesseurResponseAll(BaseModel):
    List[ProfesseurResponse]

class ProfesseurRequest(BaseModel):
    id: Optional[str] = None
    nom: str = Field(..., min_length=3)
    prenom: str = Field(..., min_length=3)
    sexe: str = Field(..., min_length=1)
    email: EmailStr
    telephone: str = Field(..., min_length=5)
    adresse: str = Field(..., min_length=5)
    matiere_enseignee: Optional[str] = None
    notification: bool = False

    @validator('sexe')
    def validate_sexe(cls, v):
        if v.upper() not in ['M', 'F', 'MASCULIN', 'FEMININ', 'HOMME', 'FEMME']:
            raise ValueError('Le sexe doit être M, F, Masculin, Feminin, Homme ou Femme')
        return v


class ProfesseurResponseMsg(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    errors: dict

# ============= SCHEMAS PERSONNEL =============

class PersonnelBase(BaseModel):
    nom: str
    prenom: str
    sexe: str
    email: str
    telephone: str
    adresse: str
    matiere_enseignee: Optional[str] = None
    status: bool = False

class PersonnelCreate(PersonnelBase):
    pass

class PersonnelUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sexe: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    matiere_enseignee: Optional[str] = None
    status: Optional[bool] = None

class PersonnelResponse(PersonnelBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: UserResponse | None

    @computed_field
    @property
    def status_(self) -> str:
        if self.user and self.user.status:
            return "Actif"
        return "Inactif"
    
    class Config:
        from_attributes = True

class PersonnelResponseShow(BaseModel):
    data:PersonnelResponse

class PersonnelResponseAll(BaseModel):
    List[PersonnelResponse] 

class PersonnelRequestFirst(BaseModel):
    id: Optional[str] = None
    nom: str = Field(..., min_length=3)
    prenom: str = Field(..., min_length=3)
    sexe: Optional[str] = None
    email: EmailStr
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    role: Optional[str] = None
    first: bool = True 
    password: str 

class PersonnelRequest(BaseModel):
    id: Optional[str] = None
    nom: str = Field(..., min_length=3)
    prenom: str = Field(..., min_length=3)
    sexe: str = Field(..., min_length=1)
    email: EmailStr
    telephone: str = Field(..., min_length=5)
    adresse: str = Field(..., min_length=5)
    role: str
    first: bool = False  # Indique si c'est le premier utilisateur (admin)
    password: Optional[str] = None  # Requis uniquement si first=True
    
    
    @validator('sexe')
    def validate_sexe(cls, v, values):
        if v and v.upper() not in ['M', 'F', 'MASCULIN', 'FEMININ', 'HOMME', 'FEMME']:
            raise ValueError('Le sexe doit être M, F, Masculin, Feminin, Homme ou Femme')
        return v

# Modèle Pydantic pour la réponse
class PersonnelResponseMsg(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    errors: dict

class ProfesseurResponseSchema(BaseModel):
    id: str
    nom: Optional[str] = None
    prenom: Optional[str] = None 
    class Config:
        from_attributes = True

class simpleProfesseurResponse(BaseModel):
    prof: List[ProfesseurResponseSchema]

# ============= SCHEMAS PROGRAMME =============

class ProgrammeBase(BaseModel):
    professeur_id: str
    Cours_id: str
    Faculte_id: Optional[str] = None
    class_: Optional[str] = None
    niveau_id: str
    session: Optional[str] = None
    heure: Optional[str] = None
    annee_academique: str
    jours: Optional[str] = None
    coefficients: Optional[str] = None
    note_de_passage: Optional[str] = None

class ProgrammeCreate(ProgrammeBase):
    pass

class ProgrammeUpdate(BaseModel):
    professeur_id: Optional[str] = None
    Cours_id: Optional[str] = None
    Faculte_id: Optional[str] = None
    class_: Optional[str] = None
    niveau_id: Optional[str] = None
    session: Optional[str] = None
    heure: Optional[str] = None
    annee_academique: Optional[str] = None
    jours: Optional[str] = None
    coefficients: Optional[str] = None
    note_de_passage: Optional[str] = None

class ProgrammeResponse(ProgrammeBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
        
    class Config:
        from_attributes = True

# ============= SCHEMAS NOTE =============

class NoteBase(BaseModel):
    etudiant_id: str
    annee_academique: str
    annee_detude: str
    niveau_detude: str
    matiere: str
    note: float
    section: str
    status: str
    cours_id: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    annee_academique: Optional[str] = None
    annee_detude: Optional[str] = None
    niveau_detude: Optional[str] = None
    matiere: Optional[str] = None
    note: Optional[float] = None
    section: Optional[str] = None
    status: Optional[str] = None
    cours_id: Optional[str] = None

class NoteResponse(NoteBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS PRESENCE =============

class PresenceBase(BaseModel):
    etudiant_id: str
    classes_id: str
    annee_academique_id: str
    date_daujourdhui: datetime
    valeur: bool

class PresenceCreate(PresenceBase):
    pass

class PresenceUpdate(BaseModel):
    valeur: Optional[bool] = None

class PresenceResponse(PresenceBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

