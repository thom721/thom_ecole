# app/routes/etudiant.py
from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session , joinedload
from fastapi.responses import  StreamingResponse
from typing import List,Optional
from sqlalchemy import or_, func, desc
from math import ceil

import random

from app.database import get_db
from app.Models.MModels import Etudiant, Professeur,User,Niveau,AnneeAcademique,Classe,Faculte,User
from app.Models.MRelations import ClasseEtudiant,EtudiantFaculte,Responsable,PieceSoumise,CoursEtudiant
from app.Schemas.Etudiants import EtudiantCreate, EtudiantUpdate, EtudiantResponse,PaginatedResponse,StudentShowResponse 
from app.Models.MFinancials import FraisInscription,Paiement,ParametrePaiement
from app.Models.MSystems import Personnel, Profile
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime  
import base64, uuid, os  
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create
from app.Helper.pdf_personaliser import PDFGenerator
from app.Helper.context import UserContext,ActionContext
import json
from pydantic import Field
from app.Helper.get_real_path import get_app_root


router = APIRouter(prefix="/api/v1", tags=["Étudiants"])

APP_ROOT = get_app_root()
PATH = os.path.join(APP_ROOT, "app", "static")

user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
server_path = os.path.join(
user_profile, "AppData", "Local", ".ecole_360"
        )

@router.get("/etudiant", response_model=PaginatedResponse)
def get_all_etudiants(
    search: Optional[str] = Query(None, description="Recherche par nom, prénom ou identifiant"),
    sort_by: Optional[str] = Query("nom", description="Champ de tri: nom, prenom, identifiant, created_at"),
    sort_order: Optional[str] = Query("asc", description="Ordre de tri: asc ou desc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    """
    Récupère la liste des étudiants avec pagination, recherche et tri.
    """
    # Construire la requête de base
    query = db.query(Etudiant).filter(Etudiant.delete_at.is_(None))
    
    # Appliquer la recherche
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Etudiant.nom.ilike(search_pattern),
                Etudiant.prenom.ilike(search_pattern),
                Etudiant.identifiant.ilike(search_pattern)
            )
        )
     
    sort_column = getattr(Etudiant, sort_by, Etudiant.nom)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
     
    total = query.count()
     
    skip = (page - 1) * per_page
    last_page = ceil(total / per_page) if total else 1
     
    etudiants = query.offset(skip).limit(per_page).all()
    
    return PaginatedResponse(
        data=etudiants,
        meta={
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if etudiants else 0,
            "to": skip + len(etudiants) if etudiants else 0
        }
    )



@router.get("/etudiant/{etudiant_id}", response_model=StudentShowResponse)
def get_etudiant(etudiant_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    """Récupérer un étudiant par ID"""
    etudiant = db.query(Etudiant).filter(
        Etudiant.id == etudiant_id,
        Etudiant.delete_at.is_(None)
    ).first()
    
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )
    return StudentShowResponse(data=etudiant) 

@router.get("/etudiant/identifiant/{identifiant}", response_model=EtudiantResponse)
def get_etudiant_by_identifiant(identifiant: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    """Récupérer un étudiant par identifiant"""
    etudiant = db.query(Etudiant).filter(
        Etudiant.identifiant == identifiant,
        Etudiant.delete_at.is_(None)
    ).first()
    
    if not etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )
    return etudiant


@router.delete("/etudiant/{etudiant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_etudiant(etudiant_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    """Supprimer un étudiant (soft delete)"""
    from datetime import datetime
    
    db_etudiant = db.query(Etudiant).filter(
        Etudiant.id == etudiant_id,
        Etudiant.delete_at.is_(None)
    ).first()
    
    if not db_etudiant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant non trouvé"
        )
    
    db_etudiant.delete_at = datetime.utcnow()
    db.commit()
    return None
from typing import Union
from fastapi import Body

class SearchStudent(BaseModel):
    data:List[EtudiantResponse]
@router.post("/search/etudiant/", response_model=SearchStudent)
def search_etudiants(
    val: Union[str, dict] = Body(...),
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    """Rechercher des étudiants par critères"""
    query = db.query(Etudiant).filter(Etudiant.delete_at.is_(None))
     
    if isinstance(val, dict):
        search_val = val.get("val", "")
    else:
        search_val = val
    
    # if nom:
    #     query = query.filter(Etudiant.nom.ilike(f"%{nom}%"))
    # if prenom:
    #     query = query.filter(Etudiant.prenom.ilike(f"%{prenom}%"))
    if not search_val:
        raise HTTPException(status_code=400, detail="Le paramètre 'val' est requis")
    
    etudiants = db.query(Etudiant)\
        .filter(
            or_(
                Etudiant.identifiant.ilike(f"%{search_val}%"),
                Etudiant.nom.ilike(f"%{search_val}%"),
                Etudiant.prenom.ilike(f"%{search_val}%"),
                Etudiant.code.ilike(f"%{search_val}%")
            )
        )\
        .limit(10)\
        .all()
     
    return SearchStudent(data=etudiants) 

class DocumentSchema(BaseModel):
    type_de_document: str
    document_numero: Optional[str] = None
    document_date_dexpiration: Optional[date] = None
    document_status: Optional[str] = None
    document_image: Optional[str] = None   

class ResponsableSchema(BaseModel):
    nom_responsable: Optional[str] = None
    prenom_responsable: Optional[str] = None
    adresse_responsable: Optional[str] = None

    email_responsable: Optional[str] = None
    relation_responsable: Optional[str] = None
    sexe_responsable: Optional[str] = None
    telephone_responsable: Optional[str] = None
    metier_responsable: Optional[str] = None


class EtudiantSchema(BaseModel):
    id: Optional[str] = None

    nom: str = Field(min_length=3)
    prenom: str = Field(min_length=3)
    sexe: str = Field(min_length=1)
    date_de_naissance: datetime #Optional[datetime] = None
    lieu_de_naissance: str = Field(min_length=3)
    adresse: str = Field(min_length=3)

    religion: Optional[str] = None
    telephone: Optional[str] = None
    aide_financiere: Optional[str] = None
    nisu: Optional[str] = None
    dernier_etablissement: Optional[str] = None
    delete_at: Optional[str] = None

    email: Optional[EmailStr] = None

    faculte_id: Optional[str] = None
    niveau_id: str = Field(min_length=36)
    annee_academique_id: str = Field(min_length=36)
    classe_actuelle_id: str = Field(min_length=36)

    # responsable: Optional[ResponsableSchema] = None
    nom_responsable: Optional[str] = None
    prenom_responsable: Optional[str] = None
    adresse_responsable: Optional[str] = None

    email_responsable: Optional[str] = None
    relation_responsable: Optional[str] = None
    sexe_responsable: Optional[str] = None
    telephone_responsable: Optional[str] = None
    metier_responsable: Optional[str] = None

    documentss: Optional[List[DocumentSchema]] = []

    @field_validator('email', mode='before')
    @classmethod
    def transform_empty_to_none(cls, v):
        if v == "":
            return None
        return v 

    # @field_validator('faculte_id', mode='before')
    # @classmethod
    # def transform_empty_to_none(cls, v):
    #     if v == "":
    #         return None
    #     return v 

    @field_validator("date_de_naissance", mode="before")
    @classmethod
    def validate_date_naissance(cls, v):
        # 1. Conversion du texte en objet date
        parsed_date = None
        if isinstance(v, (date, datetime)):
            parsed_date = v.date() if isinstance(v, datetime) else v
        elif isinstance(v, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    parsed_date = datetime.strptime(v, fmt).date()
                    break
                except ValueError:
                    continue
        
        if not parsed_date:
            raise ValueError("Format de date invalide (AAAA-MM-JJ ou JJ/MM/AAAA)")

        # 2. Sécurité : Pas de date dans le futur
        aujourdhui = date.today()
        if parsed_date > aujourdhui:
            raise ValueError("La date de naissance ne peut pas être dans le futur.")

        # 3. Sécurité : Âge minimum (ex: l'enfant doit avoir au moins 2 ans)
        age = aujourdhui.year - parsed_date.year - ((aujourdhui.month, aujourdhui.day) < (parsed_date.month, parsed_date.day))
        
        if age < 2:
            raise ValueError(f"L'élève est trop jeune ({age} an(s)). L'âge minimum est de 2 ans.")
            
        return parsed_date

def update_or_create(db, model, search: dict, data: dict):
    instance = db.query(model).filter_by(**search).first()
    if instance:
        for k, v in data.items():
            setattr(instance, k, v)
        return instance, False
    instance = model(**{**search, **data})
    db.add(instance)
    return instance, True

def generate_unique_code(db):
    while True:
        code = f"1-{random.randint(0,99999):05d}"
        if not db.query(Etudiant).filter_by(identifiant=code).first():
            return code

def generate_uuid():
    return str(uuid.uuid4())

@router.post("/etudiant")
def store_etudiant(
    data: EtudiantSchema,
    db: Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    UPLOAD_DIR = "app/static/"
          
    validate_exists(Niveau, Niveau.id, db, data.niveau_id) 
    validate_exists(Classe, Classe.id, db, data.classe_actuelle_id)
    validate_exists(AnneeAcademique, AnneeAcademique.id, db, data.annee_academique_id)
     
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == data.annee_academique_id).first()
    # user_id=null
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")
 
    aujourdhui = date.today()
     
    if annee.date_fin and annee.date_fin < aujourdhui:
        raise HTTPException(
            status_code=400, 
            detail=f"Impossible d'inscrire un élève dans une année passée ({annee.annee_academique})."
        )
    UserContext.set_user_id(current_user.id)
    if data.id:
        if not user_has_permission(current_user,"Modifier etudiant",db):
            raise HTTPException(
            status_code=403, 
            detail=f"Action impossible : l'autorisation vous est refusée."
        ) 
    else:
        if not user_has_permission(current_user,"Ajouter etudiant",db):
            raise HTTPException(
            status_code=403, 
            detail=f"Action impossible : l'autorisation vous est refusée."
        )

   
    niveau = db.query(Niveau).filter_by(id=data.niveau_id).first()
    if not niveau:
        raise HTTPException(404, "Niveau introuvable")

    if niveau.name in ["Universitaire", "Technique"] and not data.faculte_id:
        validate_exists(Faculte, Faculte.id, db, data.faculte_id)
        raise HTTPException(422, "La faculté est obligatoire")

    try:
        etudiant_data = data.model_dump(exclude={"documentss", "faculte_id", "niveau_id","annee_academique_id","classe_actuelle_id","nom_responsable",
        "prenom_responsable","adresse_responsable","email_responsable","relation_responsable","sexe_responsable","telephone_responsable","metier_responsable"})
     
     
        if data.id:  
            # user_id = None          
            etudiant = db.query(Etudiant).filter_by(id=data.id).first()
            if not etudiant:
                raise HTTPException(404, "Étudiant introuvable 3")
            for k, v in etudiant_data.items():
                setattr(etudiant, k, v)
        else:
            user_id = current_user.id
            etudiant_data["identifiant"] = generate_unique_code(db)
            etudiant_data["id"] = generate_uuid()
            etudiant = Etudiant(**etudiant_data)
            db.add(etudiant)
            db.flush()
        

        # =====================c
        # =====================  
        count_student = db.query(ClasseEtudiant).filter(ClasseEtudiant.etudiant_id == etudiant.id).count()
        if niveau.name in ["Universitaire", "Technique"]:
            update_or_create(
                db,
                EtudiantFaculte,
                search={
                    "etudiant_id": etudiant.id,
                    "annee_academique_id": data.annee_academique_id,
                    "niveau_id": data.niveau_id,
                },
                data={
                    "classes_id": data.classe_actuelle_id,
                    "faculte_id": data.faculte_id,
                },
            )
        else:
            update_or_create(
                db,
                ClasseEtudiant,
                search={
                    "etudiant_id": etudiant.id,
                    "annee_academique_id": data.annee_academique_id,
                    "niveau_id": data.niveau_id,
                },
                data={
                    "user_id": current_user.id if count_student == 0 else None,
                    "classes_id": data.classe_actuelle_id,
                },
            )



            # même condition Laravel
        if data.nom_responsable and data.prenom_responsable and data.adresse_responsable:
            update_or_create(
                db,
                Responsable,
                search={
                    "etudiant_id": etudiant.id,
                },
                data={
                    "nom_responsable": data.nom_responsable,
                    "prenom_responsable": data.prenom_responsable,
                    "email_responsable": data.email_responsable,
                    "relation_responsable": data.relation_responsable,
                    "sexe_responsable": data.sexe_responsable,
                    "telephone_responsable": data.telephone_responsable,
                    "metier_responsable": data.metier_responsable,
                    "adresse_responsable": data.adresse_responsable,
                },
            )

        # ===================== 
        # =====================
        for doc in data.documentss or []:
            if not doc.type_de_document:
                continue

            file_path = None
            if doc.document_image and "base64" in doc.document_image:
                header, encoded = doc.document_image.split(",", 1)
                ext = header.split("/")[1].split(";")[0]
                filename = f"{uuid.uuid4()}.{ext}"
                # folder = "documents"
                os.makedirs(UPLOAD_DIR, exist_ok=True)

                # os.makedirs(folder, exist_ok=True)
                file_path = f"documents/{filename}"


                with open(f"{UPLOAD_DIR}/{file_path}", "wb") as f:
                    f.write(base64.b64decode(encoded))

                # with open(file_path, "wb") as f:
                #     f.write(base64.b64decode(encoded))

            update_or_create(
                db,
                PieceSoumise,
                search={
                    "etudiant_id": etudiant.id,
                    "type_de_document": doc.type_de_document,
                },
                data={
                    "document_image_base64":doc.document_image,
                    "document_numero": doc.document_numero,
                    "document_date_dexpiration": doc.document_date_dexpiration,
                    "document_status": 1,
                    "document_image": file_path,
                },
            )

        db.commit()
        return {"success": "Opération réussie"}

    except Exception as e:
        db.rollback()
        
        raise HTTPException(422, str(e))

@router.post("/student-register")
def store_etudiant(
    data: EtudiantSchema,
    db: Session = Depends(get_db)
):
    UPLOAD_DIR = "app/static/"
          
    validate_exists(Niveau, Niveau.id, db, data.niveau_id) 
    validate_exists(Classe, Classe.id, db, data.classe_actuelle_id)
    validate_exists(AnneeAcademique, AnneeAcademique.id, db, data.annee_academique_id)
     
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == data.annee_academique_id).first()

    if data.email: 
        check_email = db.query(
            select(Etudiant.email)
            .where(Etudiant.email == data.email)
            .exists()
        ).scalar() 
        if check_email:
             raise HTTPException(status_code=404, detail="Cet email est déjà utilisé.")
        
        email_exists_in_users = db.query(
            select(User.email)
            .where(User.email == data.email)
            .exists()
        ).scalar()
        
        email_exists_in_professeurs = db.query(
            select(Professeur.id)
            .where(Professeur.email == data.email)
            .exists()
        ).scalar()

        email_exists_in_personnels = db.query(
            select(Personnel.id)
            .where(Personnel.email == data.email)
            .exists()
        ).scalar()
        if email_exists_in_users or email_exists_in_professeurs or email_exists_in_personnels:
            raise HTTPException(status_code=404, detail="Cet email est déjà utilisé.")
           
    
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")
 
    aujourdhui = date.today()
     
    if annee.date_fin and annee.date_fin < aujourdhui:
        raise HTTPException(
            status_code=400, 
            detail=f"Impossible d'inscrire un élève dans une année passée ({annee.annee_academique})."
        )
    ActionContext.set_action("Connect Autorisation") 
   
    niveau = db.query(Niveau).filter_by(id=data.niveau_id).first()
    if not niveau:
        raise HTTPException(404, "Niveau introuvable")

    if niveau.name in ["Universitaire", "Technique"] and not data.faculte_id:
        validate_exists(Faculte, Faculte.id, db, data.faculte_id)
        raise HTTPException(422, detail="La faculté ou l'Option est obligatoire")

    try:
        # ===================== 
        # =====================
        etudiant_data = data.model_dump(exclude={"documentss", "faculte_id", "niveau_id","annee_academique_id","classe_actuelle_id","nom_responsable",
        "prenom_responsable","adresse_responsable","email_responsable","relation_responsable","sexe_responsable","telephone_responsable","metier_responsable"})
     
        etudiant_data["identifiant"] = generate_unique_code(db)
        etudiant_data["id"] = generate_uuid()
        etudiant = Etudiant(**etudiant_data)
        db.add(etudiant)
        db.flush()
        

        if niveau.name in ["Universitaire", "Technique"]:
            update_or_create(
                db,
                EtudiantFaculte,
                search={
                    "etudiant_id": etudiant.id,
                    "annee_academique_id": data.annee_academique_id,
                    "niveau_id": data.niveau_id,
                },
                data={
                    "classes_id": data.classe_actuelle_id,
                    "faculte_id": data.faculte_id,
                },
            )
        else:
            update_or_create(
                db,
                ClasseEtudiant,
                search={
                    "etudiant_id": etudiant.id,
                    "annee_academique_id": data.annee_academique_id,
                    "niveau_id": data.niveau_id,
                },
                data={
                    "classes_id": data.classe_actuelle_id,
                },
            )



            # même condition Laravel
        if data.nom_responsable and data.prenom_responsable and data.adresse_responsable:
            update_or_create(
                db,
                Responsable,
                search={
                    "etudiant_id": etudiant.id,
                },
                data={
                    "nom_responsable": data.nom_responsable,
                    "prenom_responsable": data.prenom_responsable,
                    "email_responsable": data.email_responsable,
                    "relation_responsable": data.relation_responsable,
                    "sexe_responsable": data.sexe_responsable,
                    "telephone_responsable": data.telephone_responsable,
                    "metier_responsable": data.metier_responsable,
                    "adresse_responsable": data.adresse_responsable,
                },
            )

        # ===================== 
        # =====================
        for doc in data.documentss or []:
            # if not doc.type_de_document:
            #     continue
            if doc.type_de_document and not doc.document_image:
                raise HTTPException(422, detail="Le document est obligatoire")
 

            file_path = None
            if doc.document_image and "base64" in doc.document_image:
                header, encoded = doc.document_image.split(",", 1)
                ext = header.split("/")[1].split(";")[0]
                filename = f"{uuid.uuid4()}.{ext}"
                # folder = "documents"
                os.makedirs(UPLOAD_DIR, exist_ok=True)

                # os.makedirs(folder, exist_ok=True)
                file_path = f"documents/{filename}"


                with open(f"{UPLOAD_DIR}/{file_path}", "wb") as f:
                    f.write(base64.b64decode(encoded))

                # with open(file_path, "wb") as f:
                #     f.write(base64.b64decode(encoded))

            update_or_create(
                db,
                PieceSoumise,
                search={
                    "etudiant_id": etudiant.id,
                    "type_de_document": doc.type_de_document,
                },
                data={
                    "document_image_base64":doc.document_image,
                    "document_numero": doc.document_numero,
                    "document_date_dexpiration": doc.document_date_dexpiration,
                    "document_status": 1,
                    "document_image": file_path,
                },
            )

        db.commit()
        return {"success": "Opération réussie","identifiant":etudiant.identifiant,"id":etudiant.id}

    except Exception as e:
        db.rollback()
        
        raise HTTPException(422, str(e))


@router.delete("/delete-student/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
   
    try:
        # Utilisation d'un bloc de transaction
        with db.begin():
            # Supprimer les classes liées
            db.query(ClasseEtudiant).filter(ClasseEtudiant.etudiant_id == student_id).delete()
            
            # Supprimer les responsables liés
            # (Assure-toi que le modèle Responsable est importé)
            db.query(Responsable).filter(Responsable.etudiant_id == student_id).delete()
            
            # Supprimer l'étudiant
            student = db.query(Etudiant).get(student_id)
            if student:
                db.delete(student)
            else:
                raise HTTPException(status_code=404, detail="Étudiant introuvable 4")

        return {"success": "Opération réussie"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")
    



# router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()

# @router.get("/print-recu-inscrit/{student_id}")
# @router.post("/print-recu-inscrit/{student_id}")
# @router.api_route("/print-recu-inscrit/{student_id}", methods=["GET", "POST"])
@router.api_route("/print-recu-inscrit/{student_id}", methods=["GET", "POST"], response_model=StudentShowResponse)
def impression_fiche(student_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    # 1. Récupération de l'étudiant avec ses relations (équivalent de with())
    # student = db.query(Etudiant).options(
    #     joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.classes),
    #     joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.niveaux),
    #     joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.annee_academiques)
    # ).filter(Etudiant.id == student_id).first()
 

    student = db.query(Etudiant).options(
        # 1. Chargement de la partie "Classe" (ton code existant)
        joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.classes),
        joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.niveaux),
        joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.annee_academiques),
        
        # 2. Chargement de la partie "Faculté" (la nouvelle table)
        joinedload(Etudiant.etudiant_facultes).joinedload(EtudiantFaculte.faculte),
        joinedload(Etudiant.etudiant_facultes).joinedload(EtudiantFaculte.niveaux),
        joinedload(Etudiant.etudiant_facultes).joinedload(EtudiantFaculte.annee_academiques),
        joinedload(Etudiant.etudiant_facultes).joinedload(EtudiantFaculte.classes)
    ).filter(Etudiant.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    # 2. Logique pour récupérer les frais
    frais_prix = 1000  # Valeur par défaut
    if student.classes_etudiant:
        # On prend le premier enregistrement de classe_etudiant (comme ton [0] en PHP)
        classe_info = student.classes_etudiant[0]
        print('classe_info.niveau_id')
        print(classe_info.niveau_id)
        print(classe_info.annee_academique_id)
        print('classe_info.niveau_id')
        
        frais = db.query(FraisInscription).filter(
            FraisInscription.niveau_id == classe_info.niveau_id,
            FraisInscription.anneeAc == classe_info.annee_academique_id
        ).first()
        
        if frais:
            frais_prix = frais.prix
    else:
        classe_info = student.etudiant_facultes[0]
        frais = db.query(FraisInscription).filter(
            FraisInscription.niveau_id == classe_info.niveau_id,
            FraisInscription.anneeAc == classe_info.annee_academique_id
        ).first()
        
        if frais:
            frais_prix = frais.prix

    try:
        info_ecole = db.query(Profile).first()
        is_fac = len(student.etudiant_facultes) > 0

        data = {
            "data_student": student,
            "date": datetime.now().strftime("%d/%m/%Y"),
            "info": info_ecole,
            "recu": {
                "numero": "REC-000123",
                "montant": frais_prix
            },
            "is_faculte": is_fac,
        }

        # return data
    
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
            template_file="inscrit.html",  # Votre template Jinja2
            data=data,
            output_filename="inscrit.pdf"
        )
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=inscrit.pdf"
               }
          )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# class StudentDetails(BaseModel):
#     student_id
@router.post("/student-print-details")
def print_student_details(payload: dict, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    student_id = payload.get("student_id")
    if not student_id:
        raise HTTPException(status_code=400, detail="student_id manquant")

    # Récupération avec Parcours + Notes
    student = db.query(Etudiant).options(
        joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.classes),
        joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.niveaux),
        joinedload(Etudiant.classes_etudiant).joinedload(ClasseEtudiant.annee_academiques),
        # On charge les notes liées à chaque inscription annuelle
        joinedload(Etudiant.cours_etudiants),#.joinedload(ClasseEtudiant.notes), 
        joinedload(Etudiant.responsable) 
    ).filter(Etudiant.id == student_id).first()

    # TRI : On trie le parcours du plus ancien au plus récent
    if student and student.classes_etudiant:
        student.classes_etudiant.sort(key=lambda x: x.annee_academiques.annee_academique)

    
    # parcours_traite = []
    parcours_analyse = []
    derniere_moyenne = None

    for cours in student.cours_etudiants:
        try:
            full_data = json.loads(cours.data_etudiant)
            notes_etudiant = full_data.get(student.identifiant, {})
        except:
            continue

        all_averages = []
        # Extraction et calcul des moyennes par matière
        for cat in notes_etudiant.values():
            for m_nom, m_details in cat.items():
                n = m_details.get('notes', {})
                # Calcul moyenne sur les mois présents
                vals = [v for v in n.values() if isinstance(v, (int, float))]
                if vals:
                    moy = sum(vals) / len(vals)
                    all_averages.append({"nom": m_nom, "moy": moy})

        if not all_averages:
            continue

        # Calculs statistiques
        moyenne_annuelle = sum(a['moy'] for a in all_averages) / len(all_averages)
        top_matiere = max(all_averages, key=lambda x: x['moy'])
        low_matiere = min(all_averages, key=lambda x: x['moy'])
        
        # Détermination de la progression
        tendance = "Nouveau"
        if derniere_moyenne is not None:
            tendance = "En progression 📈" if moyenne_annuelle > derniere_moyenne else "En régression 📉"
        classe = db.query(Classe).filter(Classe.id==cours.classe).first()
        status_annee = db.query(AnneeAcademique).filter(AnneeAcademique.annee_academique==cours.annee_academique).first()
        parcours_analyse.append({
            "annee": cours.annee_academique,
            "classe": classe.nom_classe if classe else "",
            "annee_academique": status_annee if status_annee else "",
            "moyenne_gen": round(moyenne_annuelle, 2),
            "top": top_matiere,
            "low": low_matiere,
            "tendance": tendance,
            "details_bruts": notes_etudiant
        })
        derniere_moyenne = moyenne_annuelle


    # 2. Infos de l'école pour l'en-tête
    info_ecole = db.query(Profile).first()
    data = {
            "data_student": student,
            "date": datetime.now().strftime("%d/%m/%Y"),#student.created_at.strftime("%d/%m/%Y") if student else ,
            "info": info_ecole,
            # "notes_dict": notes_dict,
            "parcours":parcours_analyse,
            "derniere_moyenne":derniere_moyenne
            
        }
    # return data
    try: 

        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
            template_file="student_details.html",  # Votre template Jinja2
            data=data,
            output_filename="student_details.pdf"
        )
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                     "Content-Disposition": f"attachment; filename=fiche_{student.nom}.pdf"
               }
          )

        # 6. Retour du fichier binaire
        return Response(
            content=pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=fiche_{student.nom}.pdf"
            }
        ) 

    except Exception as e:
        # print(f"Erreur PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")
    

@router.post("/student-specific-details")
def get_specific_student_details(payload: dict, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    student_id = payload.get("student_id")
    classe_id = payload.get("classe_id")
    annee_id = payload.get("annee_id")

    if not all([student_id, classe_id, annee_id]):
        raise HTTPException(status_code=400, detail="Paramètres manquants")

    # 1. Récupérer l'étudiant et l'année cible
    student = db.query(Etudiant).filter(Etudiant.id == student_id).first()
    target_annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == annee_id).first()

    if not student or not target_annee:
        raise HTTPException(status_code=404, detail="Étudiant ou Année introuvable")

    # 2. Récupérer UNIQUEMENT le cours qui correspond au clic (Filtre précis)
    # On utilise target_annee.annee_academique (le nom ex: "2025-2026")
    specific_cours = db.query(CoursEtudiant).filter(
        CoursEtudiant.etudiant_id == student_id,
        CoursEtudiant.classe == classe_id,
        CoursEtudiant.annee_academique == target_annee.annee_academique
    ).all() # On prend all() au cas où il y a plusieurs entrées, mais généralement first() suffit

    parcours_analyse = []
    derniere_moyenne = None

    for cours in specific_cours:
        try:
            full_data = json.loads(cours.data_etudiant)
            notes_etudiant = full_data.get(student.identifiant, {})
        except:
            continue

        all_averages = []
        for cat in notes_etudiant.values():
            for m_nom, m_details in cat.items():
                n = m_details.get('notes', {})
                vals = [v for v in n.values() if isinstance(v, (int, float))]
                if vals:
                    moy = sum(vals) / len(vals)
                    all_averages.append({"nom": m_nom, "moy": round(moy, 2)})

        if not all_averages:
            continue

        moyenne_annuelle = sum(a['moy'] for a in all_averages) / len(all_averages)
        top_matiere = max(all_averages, key=lambda x: x['moy'])
        low_matiere = min(all_averages, key=lambda x: x['moy'])
        
        # Récupération du nom de la classe pour l'UI
        classe_info = db.query(Classe).filter(Classe.id == cours.classe).first()

        parcours_analyse.append({
            "annee": cours.annee_academique,
            "classe": classe_info.nom_classe if classe_info else "N/A",
            "moyenne_gen": round(moyenne_annuelle, 2),
            "top": top_matiere,
            "low": low_matiere,
            "details_bruts": notes_etudiant
        })
        derniere_moyenne = moyenne_annuelle

    # 3. Logique de paiement (Calculée à la volée pour cette classe/année)
    paiement_info = get_paiement_logic_summary(student_id, classe_id, annee_id,target_annee.annee_academique, db)
    p = paiement_info.get("paiement_details") if paiement_info else {}
    print(paiement_info)
    return {
        # "data_student": {
        #     "nom": student.nom,
        #     "prenom": student.prenom,
        #     "identifiant": student.identifiant
        # },
        "parcours": parcours_analyse,
        "paiement_details": p,
        "mois": p
    }
def get_paiement_logic_summary(student_id, classe_id, annee_id, target_annee_id,db):

    # echeances_prevues = db.query(ParametrePaiement).filter(
    #     ParametrePaiement.classe == classe_id, 
    #     ParametrePaiement.anneeAcademique == annee_id
    # ).order_by(ParametrePaiement.created_at).all()
    # print(echeances_prevues)
    # 2. Récupérer tous les paiements déjà effectués par l'étudiant pour ce parcours
    paiements = db.query(Paiement.paiement_details,Paiement.paiement_details).filter(
        Paiement.etudiant_id == student_id,
        Paiement.classe == classe_id,
        Paiement.annee_academique == target_annee_id
    ).first()
     
    total_verse = paiements.paiement_details if paiements else {}  
  
    # status_paiement = {} # Utilisation du dictionnaire pour l'unicité

    # 3. Algorithme de répartition
    # for ech in echeances_prevues:
    #     label = ech.libelle # ex: "1er Versement"
    #     montant_du = ech.montant

    #     if reservoir >= montant_du:
    #         status_paiement[label] = f"Acqt: {label}"
    #         reservoir -= montant_du
    #     elif reservoir > 0:
    #         status_paiement[label] = f"Avns: {label}"
    #         reservoir = 0 # Le réservoir est vide après cette avance
    #     else:
    #         status_paiement[label] = f"Du: {label}"
    # {"student_id": "ab18960e-b8d5-45b3-acbe-0f73ae15afe0", "classe_id": "99a7f658-351b-401a-b5e1-a8ddf7e553ad", "annee_id": "8b0f7424-e2db-42f6-a64d-d1d1ea2f68d8"}
 
    return total_verse
# {
#         "total_verse": total_verse #.paiement_details if total_verse else {},
#         # "balance_restante": sum(e.montant for e in echeances_prevues) - total_verse,
#         # "liste_status": list(status_paiement.values()),
#         # "historique_transactions": [
#         #     {"date": p.created_at.strftime("%d-%m-%Y"), "montant": p.montant} 
#         #     for p in paiements
#         # ]
#     }

class BadgeImageUpdate(BaseModel):
    etudiant_id: str
    image_base64: str  # La chaîne envoyée par PySide6

 

@router.patch("/save-badge-image")
def save_badge_image(data: BadgeImageUpdate, db: Session = Depends(get_db)):
    UPLOAD_DIR = f"{server_path}/uploads/badges"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # 1. Chercher l'étudiant
    etudiant = db.query(Etudiant).filter(Etudiant.id == data.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    ActionContext.set_action('Connect Autorisation')
    try:
        # 2. Nettoyer la chaîne base64 (au cas où il y aurait le préfixe data:image/jpeg;base64,)
        header, encoded = data.image_base64.split(",", 1) if "," in data.image_base64 else (None, data.image_base64)
        image_data = base64.b64decode(encoded)

        # 3. Définir le chemin du fichier
        file_name = f"badge_{etudiant.id}.jpg"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # 4. Sauvegarder sur le disque
        with open(file_path, "wb") as f:
            f.write(image_data)

        # 5. Mettre à jour la base de données
        etudiant.photo_base64 = data.image_base64 # On stocke la chaîne
        etudiant.photo_path = file_path           # On stocke le chemin
        
        db.commit()
        
        return {"message": "Photo mise à jour avec succès", "path": file_path}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de l'image: {str(e)}")


class EtudiantSchemaUpdate(BaseModel):
    id: str
    nom: str = Field(min_length=3)
    prenom: str = Field(min_length=3)
    sexe: Optional[str] = None
    date_de_naissance: Optional[datetime] = None
    lieu_de_naissance: Optional[str] = None
    adresse: Optional[str] = None
    username:Optional[str] = None
    religion: Optional[str] = None
    telephone: Optional[str] = None
    photo_url:Optional[str] = None
    email: Optional[EmailStr] = None

    # responsable: Optional[ResponsableSchema] = None
    nom_responsable: Optional[str] = None
    prenom_responsable: Optional[str] = None
    adresse_responsable: Optional[str] = None

    email_responsable: Optional[str] = None
    relation_responsable: Optional[str] = None
    sexe_responsable: Optional[str] = None
    telephone_responsable: Optional[str] = None
    metier_responsable: Optional[str] = None

    @field_validator('email', mode='before')
    @classmethod
    def transform_empty_to_none(cls, v):
        if v == "":
            return None
        return v
    @field_validator("date_de_naissance", mode="before")
    @classmethod
    def validate_date_naissance(cls, v):
        # 1. Conversion du texte en objet date
        parsed_date = None
        if isinstance(v, (date, datetime)):
            parsed_date = v.date() if isinstance(v, datetime) else v
        elif isinstance(v, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    parsed_date = datetime.strptime(v, fmt).date()
                    break
                except ValueError:
                    continue
        
        if not parsed_date:
            raise ValueError("Format de date invalide (AAAA-MM-JJ ou JJ/MM/AAAA)")

        # 2. Sécurité : Pas de date dans le futur
        aujourdhui = date.today()
        if parsed_date > aujourdhui:
            raise ValueError("La date de naissance ne peut pas être dans le futur.")

        # 3. Sécurité : Âge minimum (ex: l'enfant doit avoir au moins 2 ans)
        age = aujourdhui.year - parsed_date.year - ((aujourdhui.month, aujourdhui.day) < (parsed_date.month, parsed_date.day))
        
        if age < 2:
            raise ValueError(f"L'élève est trop jeune ({age} an(s)). L'âge minimum est de 2 ans.")
            
        return parsed_date

@router.put("/student/profile")
def update_student_profile(
    data: EtudiantSchemaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    UserContext.set_user_id(current_user.id)

    email_exists_in_users = db.query(
        select(User.id)
        .where(User.email == data.email)
        .where(User.userable_id != data.id)
        .exists() 
    ).scalar()
        
    email_exists_in_professeurs = db.query(
        select(Professeur.id)
        .where(Professeur.email == data.email)
        .exists()
    ).scalar()

    email_exists_in_personnels = db.query(
        select(Personnel.id)
        .where(Personnel.email == data.email)
        .exists()
    ).scalar()
    if email_exists_in_users or email_exists_in_professeurs or email_exists_in_personnels:
        raise HTTPException(status_code=404, detail="Cet email est déjà utilisé.")
    try: 
        etudiant_data = data.model_dump(exclude={"nom_responsable",
        "prenom_responsable","adresse_responsable","email_responsable","relation_responsable","sexe_responsable","telephone_responsable","metier_responsable","username","photo_url"})

        user = db.query(User).filter(User.userable_id == data.id).first()
        if not user:
            raise HTTPException(404, "Utilisateur non trouvé")
         
        # ✅ Vérifier si le username existe déjà (chez un autre utilisateur)
        if data.username and data.username != user.username:
            existing = db.query(User).filter(
                User.username == data.username,
                User.id != user.id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris")

        if data.id:            
            etudiant = db.query(Etudiant).filter_by(id=data.id).first()
            if not etudiant:
                raise HTTPException(404, "Étudiant introuvable 1")
            for k, v in etudiant_data.items():
                setattr(etudiant, k, v)

        if data.nom_responsable and data.prenom_responsable and data.adresse_responsable:
            update_or_create(
                db,
                Responsable,
                search={"etudiant_id": etudiant.id},
                data={
                    "nom_responsable": data.nom_responsable,
                    "prenom_responsable": data.prenom_responsable,
                    "email_responsable": data.email_responsable,
                    "relation_responsable": data.relation_responsable,
                    "sexe_responsable": data.sexe_responsable,
                    "telephone_responsable": data.telephone_responsable,
                    "metier_responsable": data.metier_responsable,
                    "adresse_responsable": data.adresse_responsable,
                },
            )
        
        UPLOAD_DIR = "app/static/profile"
        file_path = None 
        if data.photo_url and "base64" in data.photo_url:
            # ✅ Supprimer l'ancienne photo si elle existe
            if user.profile_photo_path:
                old_file = f"{UPLOAD_DIR}/{user.profile_photo_path}"
                if os.path.exists(old_file):
                    os.remove(old_file)

            header, encoded = data.photo_url.split(",", 1)
            ext = header.split("/")[1].split(";")[0]
            filename = f"{uuid.uuid4()}.{ext}"
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            file_path = f"student/{filename}"

            with open(f"{UPLOAD_DIR}/{file_path}", "wb") as f:
                f.write(base64.b64decode(encoded))

        update_or_create(
            db,
            User,
            search={"userable_id": data.id},
            data={
                "username": data.username,
                "email": data.email,
                # ✅ Ne pas écraser la photo si aucune nouvelle n'est envoyée
                **({"profile_photo_path": file_path} if file_path else {})
            },
        )

        db.commit()
        return {"success": "Opération réussie"}
      
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.put("/student/profile11")
def update_student_profile(
    data: EtudiantSchemaUpdate,
    db: Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    UserContext.set_user_id(current_user.id)
    try: 
        etudiant_data = data.model_dump(exclude={"nom_responsable",
        "prenom_responsable","adresse_responsable","email_responsable","relation_responsable","sexe_responsable","telephone_responsable","metier_responsable","username","photo_url"})


        user = db.query(User).filter(User.userable_id == data.id).first()

        if not user:
            raise HTTPException(404, "Utilisateur non trouvé")
         
        if data.id:            
            etudiant = db.query(Etudiant).filter_by(id=data.id).first()
            if not etudiant:
                raise HTTPException(404, "Étudiant introuvable 2")
            for k, v in etudiant_data.items():
                setattr(etudiant, k, v)

        if data.nom_responsable and data.prenom_responsable and data.adresse_responsable:
            update_or_create(
                db,
                Responsable,
                search={
                    "etudiant_id": etudiant.id,
                },
                data={
                    "nom_responsable": data.nom_responsable,
                    "prenom_responsable": data.prenom_responsable,
                    "email_responsable": data.email_responsable,
                    "relation_responsable": data.relation_responsable,
                    "sexe_responsable": data.sexe_responsable,
                    "telephone_responsable": data.telephone_responsable,
                    "metier_responsable": data.metier_responsable,
                    "adresse_responsable": data.adresse_responsable,
                },
            )
        
        
        # UPLOAD_DIR = f"{PATH}/profile/student"
        UPLOAD_DIR = "app/static/profile"
        file_path = None 
        if data.photo_url:             
            if data.photo_url and "base64" in data.photo_url:
                header, encoded = data.photo_url.split(",", 1)
                ext = header.split("/")[1].split(";")[0]
                filename = f"{uuid.uuid4()}.{ext}"
                
                os.makedirs(UPLOAD_DIR, exist_ok=True)

                # os.makedirs(folder, exist_ok=True)
                file_path = f"student/{filename}"


                with open(f"{UPLOAD_DIR}/{file_path}", "wb") as f:
                    f.write(base64.b64decode(encoded))
                    
        update_or_create(
            db,
            User,
            search={
                "userable_id": data.id,
            },
            data={
                "username": data.username,
                "email": data.email,
                "profile_photo_path": file_path
            },
        )
        # user.username = data.username
        # user.email = data.email
        # user.profile_photo_path = file_path

        db.commit()

        return {"success": "Opération réussie"}
      
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"{str(e)}")