# app/schemas/etudiant.py
from pydantic import BaseModel, EmailStr, Field,computed_field
from typing import Optional,List
from datetime import datetime, date
from .Academic import PresenceResponse,AnneeAcademiqueResponse,NiveauResponse,FaculteResponse,ClasseResponse
from .UserSchema import UserResponse

# ============= SCHEMAS ETUDIANT =============
class EtudiantSchema(BaseModel):
    id: str
    identifiant: str
    nom: str
    prenom: str

    class Config:
        from_attributes = True

class EtudiantResponseLive(BaseModel):
    val: Optional[str] = None
    data: List[EtudiantSchema]


class EtudiantBase(BaseModel):
    identifiant: str
    nom: str
    prenom: str
    sexe: str
    date_de_naissance: str
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    adresse: str
    religion: Optional[str] = None
    lieu_de_naissance: Optional[str] = None
    code: Optional[str] = None
    aide_financiere: str = "Aucune"
    nisu: Optional[str] = None
    dernier_etablissement: Optional[str] = None

class EtudiantCreate(EtudiantBase):
    pass

class EtudiantUpdate(BaseModel):
    identifiant: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sexe: Optional[str] = None
    date_de_naissance: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    adresse: Optional[str] = None
    religion: Optional[str] = None
    lieu_de_naissance: Optional[str] = None
    code: Optional[str] = None
    aide_financiere: Optional[str] = None
    nisu: Optional[str] = None
    dernier_etablissement: Optional[str] = None

class EtudiantResponse(EtudiantBase):
    id: str
    photo_base64: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    delete_at: Optional[datetime] = None
    @computed_field
    @property
    def _naissance(self) -> str:
        if self.date_de_naissance:
            if isinstance(self.date_de_naissance, str):
                dt = datetime.fromisoformat(self.date_de_naissance)
            else:
                dt = self.date_de_naissance
            return dt.strftime("%d %b %Y")
        return ""

    responsable: Optional["ResponsableResponse"]=[]
    user: Optional["UserResponse"]=None
    classes_etudiant: Optional[List["ClasseEtudiantSchema"]]=[]
    etudiant_facultes: Optional[List["EtudiantFaculteSchema"]]=[]
    presences: Optional[List["PresenceResponse"]]=[]
    pieces_soumises: Optional[List["PieceSoumiseResponse"]]=[]
    

    class Config:
        from_attributes = True
        from_attributes = True  # <--- c'est super important

class EtudiantResponseRead(EtudiantBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    delete_at: Optional[datetime] = None
    @computed_field
    @property
    def _naissance(self) -> str:
        if self.date_de_naissance:
            if isinstance(self.date_de_naissance, str):
                dt = datetime.fromisoformat(self.date_de_naissance)
            else:
                dt = self.date_de_naissance
            return dt.strftime("%d %b %Y")
        return ""
    
    class Config:
        from_attributes = True
        from_attributes = True  # <--- c'est super important

        
class PaginatedResponse(BaseModel):
    data: List[EtudiantResponseRead]
    meta: dict

class StudentShowResponse(BaseModel):
    data: EtudiantResponse
# ============= SCHEMAS RESPONSABLE =============

class ResponsableBase(BaseModel):
    nom_responsable: str
    prenom_responsable: str
    email_responsable: Optional[str] = None
    relation_responsable: Optional[str] = None
    sexe_responsable: Optional[str] = None
    telephone_responsable: Optional[str] = None
    metier_responsable: Optional[str] = None
    adresse_responsable: str
    etudiant_id: str

class ResponsableCreate(ResponsableBase):
    pass

class ResponsableUpdate(BaseModel):
    nom_responsable: Optional[str] = None
    prenom_responsable: Optional[str] = None
    email_responsable: Optional[str] = None
    relation_responsable: Optional[str] = None
    sexe_responsable: Optional[str] = None
    telephone_responsable: Optional[str] = None
    metier_responsable: Optional[str] = None
    adresse_responsable: Optional[str] = None

class ResponsableResponse(ResponsableBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= SCHEMAS PIECE SOUMISE =============

class PieceSoumiseBase(BaseModel):
    type_de_document: Optional[str] = None
    document_numero: Optional[str] = None
    document_date_dexpiration: Optional[str] = None
    document_status: Optional[str] = None
    document_image: Optional[str] = None
    document_image_base64: Optional[str] = None
    etudiant_id: Optional[str] = None

class PieceSoumiseCreate(PieceSoumiseBase):
    pass

class PieceSoumiseUpdate(BaseModel):
    type_de_document: Optional[str] = None
    document_numero: Optional[str] = None
    document_date_dexpiration: Optional[str] = None
    document_status: Optional[str] = None
    document_image: Optional[str] = None
    document_image_base64: Optional[str] = None

class PieceSoumiseResponse(PieceSoumiseBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# 1. Corrigez ClasseResponseSchema
class ClasseResponseSchema(BaseModel):
    id: str
    nom_classe: Optional[str] = None
    niveau_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 5. Assurez-vous que ces classes existent (définissez-les avant ou importez)
class AnneeAcademiqueResponse(BaseModel):
    id: str
    annee_academique: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NiveauResponse(BaseModel):
    id: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 4. Corrigez ClasseEtudiantSchema
class ClasseEtudiantSchema(BaseModel):
    id: Optional[str] = Field(None, description="UUID de la relation étudiant-classe")
    etudiant_id: str = Field(..., description="UUID de l'étudiant")
    classes_id: str = Field(..., description="UUID de la classe")
    annee_academique_id: str = Field(..., description="UUID de l'année académique")
    niveau_id: str = Field(..., description="UUID du niveau")
    user_id: Optional[str] = Field(None, description="UUID de l'utilisateur qui a créé/modifié")
    status: bool = Field(True, description="Statut actif/inactif")
    created_at: Optional[datetime] = Field(None, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    # Définissez les relations comme Optional
    classes: Optional[ClasseResponseSchema] = None
    annee_academiques: Optional[AnneeAcademiqueResponse] = None
    niveaux: Optional[NiveauResponse] = None
    
    class Config:
        from_attributes = True


 
# class ClasseEtudiantSchema(BaseModel):
#     id: Optional[str] = Field(None, description="UUID de la relation étudiant-classe")
#     etudiant_id: str = Field(None, description="UUID de l'étudiant")
#     classes_id: str = Field(None, description="UUID de la classe")
#     annee_academique_id: str = Field(None, description="UUID de l'année académique")
#     niveau_id: str = Field(None, description="UUID du niveau")
#     user_id: Optional[str] = Field(None, description="UUID de l'utilisateur qui a créé/modifié")
#     status: bool = Field(True, description="Statut actif/inactif")
#     created_at: Optional[datetime] = Field(None, description="Date de création")
#     updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

#     classes: "ClasseResponse" ={}
#     annee_academiques: "AnneeAcademiqueResponse" ={}
#     niveaux: "NiveauResponse" ={}
 
#     class Config:
#         from_attributes = True

# class ClasseBase(BaseModel):
#     niveau_id: Optional[str]=None
#     nom_classe: Optional[str]=None

# class ClasseCreate(ClasseBase):
#     pass

# class ClasseUpdate(BaseModel):
#     niveau_id: Optional[str] = None
#     nom_classe: Optional[str] = None

# class ClasseResponseSchema(ClasseBase):
#     id: str
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None
#     class Config:
#         from_attributes = True

# class ClasseResponse(ClasseBase):
#     List[ClasseResponseSchema]

class FaculteResponse(BaseModel):
    id: str
    nom: Optional[str] = None
    nb_annee: Optional[str] = None
    status: Optional[bool] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EtudiantFaculteSchema(BaseModel):
    id: Optional[str] = Field(None, description="UUID de la relation étudiant-faculté")
    etudiant_id: str = Field(..., description="UUID de l'étudiant")
    faculte_id: str = Field(None, description="UUID de la faculté")
    niveau_id: str = Field(..., description="UUID du niveau")
    classes_id: str = Field(..., description="UUID de la classe")
    annee_academique_id: str = Field(..., description="UUID de l'année académique")
    created_at: Optional[datetime] = Field(None, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    # Définissez les relations comme Optional
    classes: Optional[ClasseResponseSchema] = None
    annee_academiques: Optional[AnneeAcademiqueResponse] = None
    niveaux: Optional[NiveauResponse] = None
    faculte: Optional[FaculteResponse] = None
    class Config:
        from_attributes = True
