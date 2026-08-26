# app/routes/academic.py
from fastapi import APIRouter, Depends, HTTPException, status,Query,Header
from sqlalchemy.orm import Session, joinedload 
from typing import List,Optional
from sqlalchemy import or_,select
from sqlalchemy import desc
import math
import secrets
import string
import base64 
from app.utils.students_email import send_activation_email
import os
from pydantic import BaseModel, Field, computed_field
from datetime import datetime, date 
from passlib.context import CryptContext
from app.database import get_db
from app.Models.MModels import AnneeAcademique, Niveau, Faculte, Classe, Cours,Etudiant, Professeur,User
from app.Models.MSystems import Personnel,ModelHasRole,Profile,Role,Permission
from app.Models.MFinancials import SalaireHistorique
from app.Schemas.pagination import PaginatedResponse
from app.utils.pagination import paginate 
from app.Schemas.SOther import ActiveRequest, ChangePasswordRequest,SuccessResponse
from app.Helper import CryptAndDecript
from app.Schemas.Academic import (
    AnneeAcademiqueCreate, AnneeAcademiqueUpdate, AnneeAcademiqueResponse,
    NiveauCreate, NiveauUpdate, NiveauResponse,
    FaculteCreate, FaculteUpdate, FaculteResponse,FaculteResponseOne,
    ClasseCreate, ClasseUpdate, ClasseResponse,PersonnelResponseAll,
    CoursCreate, CoursUpdate, CoursResponse,
    ProfesseurCreate, ProfesseurUpdate, ProfesseurResponse,PersonnelCreate, PersonnelUpdate, PersonnelResponse,ProfesseurResponseShow,PersonnelResponseShow,ProfesseurRequest,ProfesseurResponseAll,ProfesseurResponseMsg,PersonnelResponseMsg,ErrorResponse,PersonnelRequest,PersonnelRequestFirst#,ErrorResponse
) 
from app.Helper.rAuto import *
from app.Helper.context import UserContext,ActionContext
from app.Helper.get_real_path import get_real_path

import bcrypt
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role
from app.services.ServiceAuth import AuthorizationService
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.config import Config

# ============= ROUTES ANNEE ACADEMIQUE =============

router_annee = APIRouter(prefix="/api/v1/annee-academique", tags=["Années Académiques"])

@router_annee.get("", response_model=AnneeAcademiqueResponse)
def get_all_annees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    annees = db.query(AnneeAcademique).order_by(desc(AnneeAcademique.created_at)).offset(skip).limit(limit).all()
    return {"data":annees}

# @router_annee.get("/{annee_id}", response_model=AnneeAcademiqueResponse)
# def get_annee(annee_id: str, db: Session = Depends(get_db)):
#     annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == annee_id).first()
#     if not annee:
#         raise HTTPException(status_code=404, detail="Année académique non trouvée")
#     return annee

# @router_annee.post("/", response_model=AnneeAcademiqueResponse, status_code=201)
# def create_annee(annee: AnneeAcademiqueCreate, db: Session = Depends(get_db)):
#     db_annee = AnneeAcademique(**annee.model_dump())
#     db.add(db_annee)
#     db.commit()
#     db.refresh(db_annee)
#     return db_annee

# @router_annee.put("/{annee_id}", response_model=AnneeAcademiqueResponse)
# def update_annee(annee_id: str, annee: AnneeAcademiqueUpdate, db: Session = Depends(get_db)):
#     db_annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == annee_id).first()
#     if not db_annee:
#         raise HTTPException(status_code=404, detail="Année académique non trouvée")
    
#     for key, value in annee.model_dump(exclude_unset=True).items():
#         setattr(db_annee, key, value)
    
#     db.commit()
#     db.refresh(db_annee)
#     return db_annee

@router_annee.delete("/{annee_id}", status_code=204)
def delete_annee(annee_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    db_annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == annee_id).first()
    if not db_annee:
        raise HTTPException(status_code=404, detail="Année académique non trouvée")
    db.delete(db_annee)
    db.commit()
    return None

# ============= ROUTES NIVEAU =============

router_niveau = APIRouter(prefix="/api/v1/niveau", tags=["Niveaux"])

@router_niveau.get("", response_model=NiveauResponse)
def get_all_niveaux(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    niveaux = db.query(Niveau).filter(Niveau.status == 1).offset(skip).limit(limit).all()
    return {"data": niveaux}

# @router_niveau.get("/{niveau_id}", response_model=NiveauResponse)
# def get_niveau(niveau_id: str, db: Session = Depends(get_db)):
#     niveau = db.query(Niveau).filter(Niveau.id == niveau_id).first()
#     if not niveau:
#         raise HTTPException(status_code=404, detail="Niveau non trouvé")
#     return niveau

# @router_niveau.post("/", response_model=NiveauResponse, status_code=201)
# def create_niveau(niveau: NiveauCreate, db: Session = Depends(get_db)):
#     db_niveau = Niveau(**niveau.model_dump())
#     db.add(db_niveau)
#     db.commit()
#     db.refresh(db_niveau)
#     return db_niveau

# @router_niveau.put("/{niveau_id}", response_model=NiveauResponse)
# def update_niveau(niveau_id: str, niveau: NiveauUpdate, db: Session = Depends(get_db)):
#     db_niveau = db.query(Niveau).filter(Niveau.id == niveau_id).first()
#     if not db_niveau:
#         raise HTTPException(status_code=404, detail="Niveau non trouvé")
    
#     for key, value in niveau.model_dump(exclude_unset=True).items():
#         setattr(db_niveau, key, value)
    
#     db.commit()
#     db.refresh(db_niveau)
#     return db_niveau

# @router_niveau.delete("/{niveau_id}", status_code=204)
# def delete_niveau(niveau_id: str, db: Session = Depends(get_db)):
    # db_niveau = db.query(Niveau).filter(Niveau.id == niveau_id).first()
    # if not db_niveau:
    #     raise HTTPException(status_code=404, detail="Niveau non trouvé")
    # db.delete(db_niveau)
    # db.commit()
    # return None

# ============= ROUTES FACULTE =============

router_faculte = APIRouter(prefix="/api/v1", tags=["Facultés"])

class FaculteSchema(BaseModel):
    id: str | None = None
    nom: str = Field(min_length=4)
    nb_annee: str  = Field(min_length=4)

@router_faculte.get("/get-all-faculte", response_model=FaculteResponse)
def get_all_facultes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    facultes = db.query(Faculte).offset(skip).limit(limit).all()
    return {"data":facultes} 

class AnneeAcademiqueResponse(BaseModel):
    id: str 
    nb_annee: str
    nom: str
    status: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Champ calculé avec @computed_field (Pydantic v2)
    @computed_field
    def status_text(self) -> str:
        """Retourne 'Actif' ou 'Inactif' basé sur status boolean"""
        return 'Actif' if self.status else 'Inactif'
    class Config:
        from_attributes = True
    
class PaginatedAnneeAcademiqueResponse(BaseModel):
    data: list[AnneeAcademiqueResponse]
    meta: dict
@router_faculte.get("/faculte", response_model=PaginatedAnneeAcademiqueResponse)
def get_all_facultes( 
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)):
    
    # facultes = db.query(Faculte).offset(skip).limit(limit).all()
    total = db.query(Faculte).count()
    
    # Calculer skip
    skip = (page - 1) * per_page
    
    # Récupérer avec pagination
    facultes = (
        db.query(Faculte)
        .order_by(desc(Faculte.updated_at))
        .offset(skip)
        .limit(per_page)
        .all()
    )
    
    # Transformer en réponse (Pydantic le fait automatiquement)
    data = [
        AnneeAcademiqueResponse.from_orm(aa)
        for aa in facultes
    ]
    
    # Calculer la dernière page
    last_page = math.ceil(total / per_page) if total else 1
    
    return PaginatedAnneeAcademiqueResponse(
        data=data,
        meta={
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if data else 0,
            "to": skip + len(data) if data else 0
        }
    )

    return {"data":facultes} 

@router_faculte.get("/show-faculte/{faculte}", response_model=FaculteResponseOne)
def get_faculte(faculte: str, db: Session = Depends(get_db)):
    faculte = db.query(Faculte).filter(Faculte.id == faculte).first()
    if not faculte:
        raise HTTPException(status_code=404, detail="Faculté non trouvée")
    # return faculte
    return FaculteResponseOne(data=faculte)

@router_faculte.post("/post-faculte")
def store_faculte(data: FaculteSchema, db: Session = Depends(get_db),current_user: User = Depends(check_permission("Ajouter parametre"))):

    if data.id:
        exists = db.query(Faculte).filter(
            Faculte.nom == data.nom,
            Faculte.id != data.id
        ).first()
    else:
        exists = db.query(Faculte).filter(
            Faculte.nom == data.nom
        ).first()

    if data.nom in (None, ''):
        raise HTTPException(status_code=422, detail="Cette classe n'est pas valide")

    if exists:
        raise HTTPException(422, "Le nom existe déjà")

  
    if data.id:
        faculte = db.query(Faculte).filter(Faculte.id == data.id).first()
        if not faculte:
            raise HTTPException(404, "Faculté introuvable")

        faculte.nom = data.nom
        faculte.nb_annee = data.nb_annee

    else:
        faculte = Faculte(
            nom=data.nom,
            nb_annee=data.nb_annee
        )
        db.add(faculte)

    db.commit()
    db.refresh(faculte)

    return {"success": True, "id": faculte.id}


    # if data.id:
    #     faculte = db.query(Faculte).filter(Faculte.id == data.id).first()
    #     if not faculte:
    #         raise HTTPException(404, "Faculté introuvable")

    #     faculte.nom = data.nom
    #     faculte.nb_annee = data.nb_annee

    # else:
    #     faculte = first_or_create(
    #         db,
    #         Faculte,
    #         search={"nom": data.nom}, 
    #         create={"nb_annee": data.nb_annee}
    #     )

    # db.commit()
    # return {"success": "success"}



@router_faculte.delete("delete-faculte/{faculte}", status_code=204)
def delete_faculte(faculte: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    db_faculte = db.query(Faculte).filter(Faculte.id == faculte).first()
    if not db_faculte:
        raise HTTPException(status_code=404, detail="Faculté non trouvée")
    db.delete(db_faculte)
    db.commit()
    return None

# ============= ROUTES CLASSE =============

router_classe = APIRouter(prefix="/api/v1", tags=["Classes"])

# @router_classe.get("/cl-load-asses_")#, response_model=ClasseResponse
# def get_all_classes(db: Session = Depends(get_db)):
#     classes = db.query(Classe).all()
#     print(classes)
#     return {"data":classes} 

@router_classe.get("/cl-load-asses_")
def get_all_classes(db: Session = Depends(get_db)):
    count = db.query(Classe).count()
    classes = db.query(Classe).all()
    print(f"Count: {count}")
    # print(f"Classes: {classes}")
    return {"data": classes}

# ===================================     PROFESSEUR ===========================
 

router_professeur = APIRouter(prefix="/api/v1", tags=["Professeurs"]) 

@router_professeur.get("/professeur",response_model=PaginatedResponse[ProfesseurResponse])
def get_professeurs(
    page: int = 1,
    per_page: int = 10,
    search: str | None = Query(None, description="Recherche par nom, prénom ou email"),
    db: Session = Depends(get_db)
):
    # query = (
    #     db.query(Professeur)
    #     .options(joinedload(Professeur.user))
    #     .order_by(Professeur.created_at.desc())
    # )

    query = (
        db.query(Professeur)
        .options(joinedload(Professeur.user))
    )

    # 🔍 SEARCH
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Professeur.nom.ilike(search_term),
                Professeur.prenom.ilike(search_term),
                Professeur.user.has(
                    User.email.ilike(search_term)
                )
            )
        )

    query = query.order_by(Professeur.created_at.desc())

    professeurs, meta = paginate(query, page, 10)

    return PaginatedResponse(
        data=professeurs,
        meta=meta
    )

@router_professeur.get("/professeur/{professeur_id}", response_model=ProfesseurResponseShow)
def get_professeur(professeur_id: str, db: Session = Depends(get_db)):
    # prof = db.query(Professeur).filter(Professeur.id == professeur_id).first()
    prof = (
        db.query(Professeur)
        .options(joinedload(Professeur.user))
        .filter(Professeur.id == professeur_id)
        .first()
    )
    if not prof:
        raise HTTPException(status_code=404, detail="Professeur non trouvé")
    
    return ProfesseurResponseShow(data=prof)


@router_professeur.post("/professeur", response_model=ProfesseurResponseMsg)
async def store_professeur(
    request: ProfesseurRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer ou mettre à jour un professeur
    """
    UserContext.set_user_id(user.id)
    try:
        # Validation de l'unicité de l'email
        email_exists_in_users = False
        email_exists_in_professeurs = False
        email_exists_in_personnels = False
        
        if request.id:
            ActionContext.set_action('update')
            # Cette fiche peut être liée à un Personnel dans un sens ou
            # l'autre ("casquette enseignante" d'un Personnel, ou fiche
            # Professeur réelle avec sa propre "casquette administrative"
            # Personnel) — dans les deux cas les deux fiches partagent
            # volontairement le même email (voir _sync_shadow_professeur/
            # _sync_shadow_personnel), il faut donc exclure ce Personnel lié
            # des vérifications d'unicité ci-dessous, sinon la mise à jour
            # de cette fiche se bloque elle-même avec "email déjà utilisé".
            linked_personnel_id = db.query(Professeur.personnel_id).filter(Professeur.id == request.id).scalar()
            shadow_personnel_id = db.query(Personnel.id).filter(Personnel.professeur_id == request.id).scalar()

            # Vérifier si l'email existe pour un autre utilisateur
            email_exists_in_users = db.query(
                select(User.id)
                .where(User.email == request.email)
                .where(User.userable_id != request.id)
                .exists()
            ).scalar()

            email_exists_in_professeurs = db.query(
                select(Professeur.id)
                .where(Professeur.email == request.email)
                .where(Professeur.id != request.id)
                .exists()
            ).scalar()

            personnels_query = (
                select(Personnel.id)
                .where(Personnel.email == request.email)
                .where(Personnel.id != request.id)
            )
            if linked_personnel_id:
                personnels_query = personnels_query.where(Personnel.id != linked_personnel_id)
            if shadow_personnel_id:
                personnels_query = personnels_query.where(Personnel.id != shadow_personnel_id)
            email_exists_in_personnels = db.query(personnels_query.exists()).scalar()
            if not user_has_permission(user,"Modifier professeur",db):
                raise HTTPException(
                status_code=403, 
                detail=f"Action impossible : l'autorisation vous est refusée."
            ) 
        else:
            ActionContext.set_action('create')
            # Vérifier si l'email existe déjà
            email_exists_in_users = db.query(
                select(User.id)
                .where(User.email == request.email)
                .exists()
            ).scalar()
            
            email_exists_in_professeurs = db.query(
                select(Professeur.id)
                .where(Professeur.email == request.email)
                .exists()
            ).scalar()

            email_exists_in_personnels = db.query(
                select(Personnel.id)
                .where(Personnel.email == request.email)
                .exists()
            ).scalar()
            if not user_has_permission(user,"Ajouter professeur",db):
                raise HTTPException(
                status_code=403, 
                detail=f"Action impossible : l'autorisation vous est refusée."
            ) 
        
        if email_exists_in_users or email_exists_in_professeurs or email_exists_in_personnels:
            return ErrorResponse(
                errors={"email": ["Cet email est déjà utilisé."]}
            )
        

        try:
            alphabet = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(8))
            password = temp_password if Config.check_internet_connection() else "@#Itsme1"
            hashed_password = CryptAndDecript.hash_password(password) 

            if request.id:
                # Mise à jour du professeur existant
                professeur = db.query(Professeur).filter(Professeur.id == request.id).first()
                
                if not professeur:
                    raise HTTPException(status_code=404, detail="Professeur non trouvé")
                
                # Mettre à jour les données du professeur
                ancien_salaire = professeur.salaire_fixe
                professeur.nom = request.nom
                professeur.prenom = request.prenom
                professeur.sexe = request.sexe
                professeur.email = request.email
                professeur.telephone = request.telephone
                professeur.adresse = request.adresse
                professeur.matiere_enseignee = request.matiere_enseignee
                professeur.type_paiement = request.type_paiement
                professeur.salaire_fixe = request.salaire_fixe
                if request.salaire_fixe is not None and request.salaire_fixe != ancien_salaire:
                    db.add(SalaireHistorique(
                        employe_type="professeur",
                        employe_id=professeur.id,
                        ancien_montant=ancien_salaire,
                        nouveau_montant=request.salaire_fixe,
                        modifie_par=user.id,
                    ))

                # Vérifier si l'utilisateur existe
                if professeur.user:
                    professeur.user.name = request.prenom
                    professeur.user.email = request.email
                else:
                    # Créer l'utilisateur si notification est activée
                    if request.notification:
                        new_user = User(
                            name=request.prenom,
                            email=request.email,
                            password=hashed_password,
                            userable_type="App\\Models\\Professeur",
                            userable_id=professeur.id
                        )
                        db.add(new_user)
                        db.flush()
                        
                        # Assigner le rôle
                        role = db.query(Role).filter(
                            Role.name.in_(["teacher", "professeur"])
                        ).first()
                        
                        if role:
                            user_role = ModelHasRole(role_id=role.id,model_type="App\\Models\\User", model_id=new_user.id)
                            db.add(user_role)
                        db.commit()

                        if Config.check_internet_connection(): 
                            profile = db.query(Profile).first()
                            school_name = profile.nom if profile else ""
                            send_activation_email(professeur.email, professeur.prenom, professeur.nom, professeur.email, temp_password,platform=school_name, role="professeur")
                            

                        else:
                            raise HTTPException(
                                status_code=503,
                                detail=f"Impossible d'envoyer l'e-mail de notification (pas de connexion internet).il sera envoyé dès que possible."
                            )
                db.commit()
                return ProfesseurResponseMsg(message="Operation reussie")
                
            else:
                # Création d'un nouveau professeur
                professeur = Professeur(
                    nom=request.nom,
                    prenom=request.prenom,
                    sexe=request.sexe,
                    email=request.email,
                    telephone=request.telephone,
                    adresse=request.adresse,
                    matiere_enseignee=request.matiere_enseignee,
                    type_paiement=request.type_paiement,
                    salaire_fixe=request.salaire_fixe
                )
                db.add(professeur)
                db.flush()
                
                # Créer l'utilisateur si notification est activée
                if request.notification:
                    new_user = User(
                    name=request.prenom,
                    email=request.email,
                    password=hashed_password,
                    userable_type="App\\Models\\Professeur",
                    userable_id=professeur.id
                    )
                    db.add(new_user)
                    db.flush()
                    
                    # Assigner le rôle
                    role = db.query(Role).filter(
                        Role.name.in_(["teacher", "professeur"])
                    ).first()
                    
                    if role:
                        user_role = ModelHasRole(role_id=role.id,model_type="App\\Models\\User", model_id=new_user.id)
                        db.add(user_role)
                        db.flush()

                    if Config.check_internet_connection():
                        # Récupérer le nom de l'école
                        profile = db.query(Profile).first()
                        school_name = profile.nom if profile else "Notre École"

                        send_activation_email(professeur.email, professeur.prenom, professeur.nom, professeur.email, temp_password,platform=school_name, role="professeur")

                        db.commit()
                        return ProfesseurResponseMsg(message="Operation reussie")
                    else:
                        db.commit()
                        return ProfesseurResponseMsg(message="Operation reussie")
                        # raise HTTPException(
                        #     status_code=503,
                        #     detail=f"Impossible d'envoyer l'e-mail de notification (pas de connexion internet).il sera envoyé dès que possible.."
                        # )
                
                
                db.commit()
            
            return ProfesseurResponseMsg(message="Operation reussie")
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=422, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router_professeur.patch("/active-teacher", response_model=SuccessResponse)
async def active_teacher(
    request: ActiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Modifier professeur"))  # Vérification admin
):
    """Active ou désactive un professeur"""
    UserContext.set_user_id(current_user.id)
    
    try:
        # Vérifier si le professeur existe
        professeur = db.query(Professeur).filter(Professeur.id == request.id).first()
        if not professeur:
            raise HTTPException(status_code=404, detail="Professeur non trouvé")
        
        # Chercher l'utilisateur associé
        user = db.query(User).filter(User.userable_id == request.id).first()
        
        if user:
            # Inverser le statut
            ActionContext.set_action('activated') if int(user.status) else ActionContext.set_action('deactivated')
            user.status = not int(user.status)
            db.commit()
            return SuccessResponse(
                success="Opération réussie",
                status=user.status
            )
        else:
            alphabet = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(8)) 
            password = temp_password if Config.check_internet_connection() else "@#Itsme1"
            hashed_password = CryptAndDecript.hash_password(password)  

            ActionContext.set_action('create in user')
            # Créer un nouvel utilisateur
            hashed_password = CryptAndDecript.hash_password("@#Itsme1")  
            
            new_user = User(
                name=professeur.prenom,
                email=professeur.email,
                status=True,
                password=hashed_password, #.decode('utf-8'),
                userable_id=professeur.id,
                userable_type="App\\Models\\Professeur"
            )
            db.add(new_user)
            db.flush()
            # db.commit()
            # db.refresh(new_user)
            
            # Assigner le rôle "professeur"
            role = db.query(Role).filter(Role.name.in_(["teacher", "professeur"])).first()
            if role:
                user_role = ModelHasRole(role_id=role.id,model_type="App\\Models\\User", model_id=new_user.id)
                db.add(user_role)
                if Config.check_internet_connection():
                    profile = db.query(Profile).first()
                    school_name = profile.nom if profile else "Notre École"

                    send_activation_email(professeur.email, professeur.prenom, professeur.nom, professeur.email, temp_password,platform=school_name, role="professeur")
            
            db.commit()
            
            return SuccessResponse(
                success="Utilisateur créé et activé",
                status=True
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_professeur.patch("/change-password-teacher", response_model=SuccessResponse)
async def change_password_teacher(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Modifier professeur"))
):
    """Change le mot de passe d'un professeur"""
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action('update password')
    try:
        # Vérifier l'ID
        if not request.professeur_id:
            raise HTTPException(status_code=422, detail="ID professeur requis")
        
        # Chercher l'utilisateur
        user = db.query(User).filter(User.userable_id == request.professeur_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Vérifier que le nouveau mot de passe est différent de l'ancien
        if bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=422, detail="Le nouveau mot de passe doit être différent de l'ancien")
        
        # Mettre à jour le mot de passe
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password.decode('utf-8')
        db.commit()
        
        return SuccessResponse(success="Mot de passe changé avec succès")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# change-password-teacher
# ===================================     PERSONNEL  ===========================
 

router_personnel = APIRouter(prefix="/api/v1", tags=["Personnel"])

_ROLES_ENSEIGNANTS = ("teacher", "enseignant")

# Rôles qui ne représentent pas une fonction de type Personnel (poste
# administratif/technique) : rôles système génériques (admin/user/student)
# et les rôles enseignants eux-mêmes. Tout le reste (Comptable, Secrétaire
# général, Responsable pédagogique, Surveillant, ...) est une fonction de
# type "personnel" — voir _sync_shadow_personnel.
_ROLES_NON_PERSONNEL = _ROLES_ENSEIGNANTS + ("admin", "user", "student")


def _role_is_enseignant(db: Session, role_id: str) -> bool:
    role = db.query(Role).filter(Role.id == role_id).first()
    return bool(role) and role.name.strip().lower() in _ROLES_ENSEIGNANTS


def _role_is_personnel(db: Session, role_id: str) -> bool:
    role = db.query(Role).filter(Role.id == role_id).first()
    return bool(role) and role.name.strip().lower() not in _ROLES_NON_PERSONNEL


def _sync_shadow_professeur(db: Session, personnel: Personnel, is_enseignant: bool) -> None:
    """Si le rôle assigné à ce Personnel est teacher/Enseignant, garantit
    l'existence d'une fiche Professeur "casquette enseignante" liée (aucun
    User propre — le Personnel garde son seul compte de connexion) afin
    qu'il soit assignable dans Programme (professeur_id) et suive ses
    cours/heures comme un vrai professeur (cours-payroll, heures-pointees,
    bilan mensuel...). Ne fait rien si le rôle n'est pas enseignant — une
    fiche déjà créée n'est jamais supprimée (préserve l'historique
    Programme/Payroll qui la référence), juste désactivée (status=False)
    si le rôle change vers autre chose. Appelé depuis store_personnel (un
    seul rôle) ET depuis RRolePermission.py:assign_role_to_user (rôles
    modifiables aussi depuis l'onglet Rôles de Profile, indépendamment du
    formulaire Personnel — il faut synchroniser depuis les deux chemins)."""
    professeur = db.query(Professeur).filter(Professeur.personnel_id == personnel.id).first()

    if is_enseignant:
        if professeur:
            professeur.nom = personnel.nom
            professeur.prenom = personnel.prenom
            professeur.sexe = personnel.sexe
            professeur.telephone = personnel.telephone
            professeur.adresse = personnel.adresse
            # Garder l'email de la fiche "casquette enseignante" aligné sur
            # le vrai email du Personnel s'il a changé depuis la création.
            professeur.email = personnel.email
            professeur.status = True
        else:
            db.add(Professeur(
                nom=personnel.nom,
                prenom=personnel.prenom,
                sexe=personnel.sexe,
                # Email réel du Personnel : aucun risque de collision avec
                # un login, puisque l'authentification passe par
                # User.email (table séparée) et non par Professeur.email —
                # cette fiche n'a de toute façon pas de User propre. Un
                # placeholder synthétique ici n'apportait rien et rendait
                # la fiche illisible dans la liste des professeurs.
                email=personnel.email,
                telephone=personnel.telephone,
                adresse=personnel.adresse,
                status=True,
                personnel_id=personnel.id,
            ))
    elif professeur:
        professeur.status = False


def _sync_shadow_personnel(db: Session, professeur: Professeur, is_personnel: bool) -> None:
    """Symétrique de _sync_shadow_professeur, pour le cas inverse : un
    Professeur avec son propre compte de connexion qui reçoit un rôle non-
    enseignant (Comptable, Secrétaire général, Responsable pédagogique...).
    Garantit l'existence d'une fiche Personnel "casquette administrative"
    liée (aucun User propre — le Professeur garde son seul compte) afin
    qu'il apparaisse dans la liste Personnel avec un salaire_fixe distinct
    de sa paie de professeur. Appelé uniquement depuis
    RRolePermission.py:assign_role_to_user — contrairement à Personnel,
    ProfesseurRequest (store_professeur) ne porte pas de champ rôle, un
    professeur ne peut changer de rôle que depuis l'onglet Rôles de
    Profile. Personnel n'a pas de colonne status (contrairement à
    Professeur) : il n'y a donc pas d'équivalent "désactiver" ici si le
    rôle repasse à enseignant/admin — la fiche déjà créée est seulement
    laissée telle quelle (jamais supprimée, pour préserver l'historique
    Payroll qui la référence)."""
    personnel = db.query(Personnel).filter(Personnel.professeur_id == professeur.id).first()

    if is_personnel:
        if personnel:
            personnel.nom = professeur.nom
            personnel.prenom = professeur.prenom
            personnel.sexe = professeur.sexe
            personnel.telephone = professeur.telephone
            personnel.adresse = professeur.adresse
            personnel.email = professeur.email
        else:
            db.add(Personnel(
                nom=professeur.nom,
                prenom=professeur.prenom,
                sexe=professeur.sexe,
                email=professeur.email,
                telephone=professeur.telephone,
                adresse=professeur.adresse,
                professeur_id=professeur.id,
            ))


@router_personnel.get("/personnel",response_model=PaginatedResponse[PersonnelResponse])
def get_personnels(
    page: int = 1,
    search: str | None = Query(None, description="Recherche par nom, prénom ou email"),
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    query = (
        db.query(Personnel)
        .options(joinedload(Personnel.user))
        .order_by(Personnel.created_at.desc())
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Personnel.nom.ilike(search_term),
                Personnel.prenom.ilike(search_term),
                Personnel.user.has(
                    User.email.ilike(search_term)
                )
            )
        )

    personnels, meta = paginate(query, page, per_page)

    return PaginatedResponse(
        data=personnels,
        meta=meta
    )


@router_personnel.get("/personnel/{personnel_id}", response_model=PersonnelResponseShow)
def get_personnel(personnel_id: str, db: Session = Depends(get_db)):
    personnel = (
        db.query(Personnel)
        # Option A : Chargement imbriqué avec des points
        .options(joinedload(Personnel.user).joinedload(User.roles)) 
        
        # Option B (Alternative) : 
        # .options(joinedload(Personnel.user, User.roles))
        
        .filter(Personnel.id == personnel_id)
        .first()
    )
    
    if not personnel:
        raise HTTPException(status_code=404, detail="personnel non trouvé")
        
    return PersonnelResponseShow(data=personnel)

@router_personnel.post("/personnel", response_model=PersonnelResponseMsg)
async def store_personnel(
    request: PersonnelRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer ou mettre à jour un personnel
    """
    
    UserContext.set_user_id(user.id)
    try:
        # Validation de l'unicité de l'email
        email_exists_in_users = False
        email_exists_in_personnels = False
        
        if request.id:
            ActionContext.set_action('update')
            # Si cette fiche est la "casquette administrative" d'un
            # Professeur (voir _sync_shadow_personnel), elle partage
            # volontairement le même email que le compte de connexion de ce
            # Professeur — l'exclure sinon la mise à jour de cette fiche se
            # bloque elle-même avec "email déjà utilisé".
            linked_professeur_id = db.query(Personnel.professeur_id).filter(Personnel.id == request.id).scalar()

            # Vérifier si l'email existe pour un autre utilisateur
            users_query = (
                select(User.id)
                .where(User.email == request.email)
                .where(User.userable_id != request.id)
            )
            if linked_professeur_id:
                users_query = users_query.where(
                    or_(User.userable_type != "App\\Models\\Professeur", User.userable_id != linked_professeur_id)
                )
            email_exists_in_users = db.query(users_query.exists()).scalar()

            email_exists_in_personnels = db.query(
                select(Personnel.id)
                .where(Personnel.email == request.email)
                .where(Personnel.id != request.id)
                .exists()
            ).scalar()
            if not user_has_permission(user,"Modifier personnel",db):
                raise HTTPException(
                status_code=403, 
                detail=f"Action impossible : l'autorisation vous est refusée."
            ) 
        else:
            ActionContext.set_action('create')
            # Vérifier si l'email existe déjà
            email_exists_in_users = db.query(
                select(User.id)
                .where(User.email == request.email)
                .exists()
            ).scalar()
            
            email_exists_in_personnels = db.query(
                select(Personnel.id)
                .where(Personnel.email == request.email)
                .exists()
            ).scalar()
            if not user_has_permission(user,"Ajouter personnel",db):
                raise HTTPException(
                status_code=403, 
                detail=f"Action impossible : l'autorisation vous est refusée."
            ) 
        
        if email_exists_in_users or email_exists_in_personnels:
            raise HTTPException(
                status_code=422,
                detail={"errors": {"email": ["Cet email est déjà utilisé."]}}
            )
        
        # Préparer les données validées
        validated_data = request.dict(exclude_none=True)
        
        # Gestion du premier utilisateur (admin)
        if request.first:
            # Récupérer le rôle admin
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if not admin_role:
                raise HTTPException(status_code=404, detail="Rôle admin non trouvé")
            
            validated_data['sexe'] = ""
            validated_data['telephone'] = "0000 000 00"
            validated_data['adresse'] = "Mon Adresse"
            validated_data['role'] = admin_role.id
        else:
            # Vérifier que le rôle existe
            role_exists = db.query(
                select(Role.id)
                .where(Role.id == request.role)
                .exists()
            ).scalar()
            
            if not role_exists:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": {"role": ["Le rôle spécifié n'existe pas."]}}
                )

        
        # Début de la transaction
        try:
            if request.id:
                # ========================================
                # MISE À JOUR DU PERSONNEL EXISTANT
                # ========================================
                personnel = db.query(Personnel).filter(Personnel.id == request.id).first()
                
                if not personnel:
                    raise HTTPException(status_code=404, detail="Personnel non trouvé")
                
                # Mettre à jour les données du personnel (exclure id et role)
                ancien_salaire = personnel.salaire_fixe
                personnel.nom = request.nom
                personnel.prenom = request.prenom
                personnel.sexe = request.sexe
                personnel.email = request.email
                personnel.telephone = request.telephone
                personnel.adresse = request.adresse
                personnel.salaire_fixe = request.salaire_fixe
                if request.salaire_fixe is not None and request.salaire_fixe != ancien_salaire:
                    db.add(SalaireHistorique(
                        employe_type="personnel",
                        employe_id=personnel.id,
                        ancien_montant=ancien_salaire,
                        nouveau_montant=request.salaire_fixe,
                        modifie_par=user.id,
                    ))

                # Vérifier si l'utilisateur existe
                try:
                    if personnel.user:
                        personnel.user.name = request.prenom
                        personnel.user.email = request.email
                        
                        # Synchroniser les rôles
                        # Supprimer les anciens rôles
                        if validated_data['role']:
                            db.query(ModelHasRole).filter(
                                ModelHasRole.model_id == personnel.user.id,
                                ModelHasRole.model_type == "App\\Models\\User"
                            ).delete()
                            
                            # Ajouter le nouveau rôle
                            new_role = ModelHasRole(
                                role_id=validated_data['role'],
                                model_type="App\\Models\\User",
                                model_id=personnel.user.id
                            )
                            db.add(new_role)
                    
                    db.commit()
                except Exception as  e:
                    logger.error(f"Erreur lors de la2 création1: {str(e)}")
                    db.rollback()
                    raise HTTPException(
                        status_code=422,
                        detail={"errors": str(e)}
                    )
                db.commit()
            else:
                alphabet = string.ascii_letters + string.digits
                temp_password = ''.join(secrets.choice(alphabet) for _ in range(8))
                password = temp_password if Config.check_internet_connection() else "@#Itsme1"
                hashed_password = CryptAndDecript.hash_password(password) 
                try:
                    logger.info(f"Création du personnel personnel: {request.dict()}")
                    
                    # Créer le personnel (exclure role)
                    personnel = Personnel(
                        nom=request.nom,
                        prenom=request.prenom,
                        sexe=request.sexe,
                        email=request.email,
                        telephone=request.telephone,
                        adresse=request.adresse,
                        salaire_fixe=request.salaire_fixe
                    )
                    db.add(personnel)
                    db.flush()
                    
                    # Créer l'utilisateur associé
                    password_to_use = request.password if request.first else "@#Itsme1"
                    
                    new_user = User(
                        name=request.prenom,
                        email=request.email,
                        password=hashed_password,
                        userable_type="App\\Models\\Personnel",
                        userable_id=personnel.id
                    )
                    db.add(new_user)
                    db.flush()
                    
                    # Assigner le rôle
                    user_role = ModelHasRole(
                        role_id=validated_data['role'],
                        model_type="App\\Models\\User",
                        model_id=new_user.id
                    )
                    db.add(user_role)
                    
                    # URL de connexion (à adapter)
                    url = "https://votre-domaine.com/login"

                    db.commit()

                except Exception as e:
                    logger.error(f"Erreur lors de la création: {str(e)}")
                    db.rollback()
                    raise HTTPException(
                        status_code=422,
                        detail={"errors": str(e)}
                    )

                # Envoi de l'email d'activation : volontairement hors de la
                # transaction ci-dessus. Le personnel est déjà enregistré
                # (commit fait) ; un échec SMTP ne doit pas faire perdre la
                # création (l'email n'est pas critique).
                if not request.first:
                    try:
                        if not Config.check_internet_connection():
                            logger.warning("Pas de connexion internet. Email non envoyé.")
                        else:
                            profile = db.query(Profile).first()
                            school_name = profile.nom if profile else "Notre École"
                            send_activation_email(
                                request.email, request.prenom, request.nom, request.email,
                                temp_password, platform=school_name, role="personnel"
                            )
                    except Exception as email_error:
                        logger.error(f"Échec d'envoi de l'email d'activation pour {request.email}: {email_error}")

            if not request.first:
                _sync_shadow_professeur(db, personnel, _role_is_enseignant(db, validated_data['role']))
                db.commit()

            return PersonnelResponseMsg(message="Operation reussie")
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur transaction: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail={"errors": str(e)}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur globale: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={"errors": str(e)}
        )

@router_personnel.post("/first-account", response_model=PersonnelResponseMsg, status_code=200)
async def store_personnel(
    request: PersonnelRequestFirst,
    db: Session = Depends(get_db)
):
    """
    Créer ou mettre à jour un personnel
    """ 
    ActionContext.set_action('Connect Autorisation')
    try:
        # Validation de l'unicité de l'email
        email_exists_in_users = False
        email_exists_in_personnels = False
        
        # Vérifier si l'email existe déjà
        email_exists_in_users = db.query(
            select(User.id)
            .where(User.email == request.email)
            .exists()
        ).scalar()
        
        email_exists_in_personnels = db.query(
            select(Personnel.id)
            .where(Personnel.email == request.email)
            .exists()
        ).scalar()
        
        if email_exists_in_users or email_exists_in_personnels:
            raise HTTPException(
                status_code=422,
                detail={"errors": {"email": ["Cet email est déjà utilisé."]}}
            )
        
        # Préparer les données validées
        validated_data = request.dict(exclude_none=True)
 
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            raise HTTPException(status_code=404, detail="Rôle admin non trouvé")
        
        validated_data['sexe'] = "M"
        validated_data['telephone'] = "0000 000 00"
        validated_data['adresse'] = "Mon Adresse"
        validated_data['role'] = admin_role.id
 
 
        try: 
            # ========================================
            # CRÉATION D'UN NOUVEAU PERSONNEL
            # ========================================
            try: 
                personnel = Personnel(
                    nom=request.nom,
                    prenom=request.prenom,
                    sexe=validated_data['sexe'],
                    email=request.email,
                    telephone=validated_data['telephone'],
                    adresse=validated_data['adresse']
                )
                db.add(personnel)
                db.flush()
                
                # Créer l'utilisateur associé
                password_to_use = request.password
                
                new_user = User(
                    name=request.prenom,
                    email=request.email,
                    password=CryptAndDecript.hash_password(password_to_use),
                    password_changed_at=datetime.utcnow(),
                    userable_type="App\\Models\\Personnel",
                    userable_id=personnel.id
                )
                db.add(new_user)
                db.flush()
                
                # Assigner le rôle
                # user_role = ModelHasRole(
                #     role_id=validated_data['role'],
                #     model_type="App\\Models\\User",
                #     model_id=new_user.id
                # )
                # db.add(user_role)

                all_permissions = db.query(Permission).all()
                all_roles = db.query(Role).all()

                sync_roles(db, new_user, all_roles)
                sync_permissions(db, new_user, all_permissions)

                # 'Controllers/education.png' (ancien chemin) n'existe que sur
                # l'installateur Windows natif (Controllers/ voisin de app/,
                # jamais copié dans l'image Docker — voir Dockerfile, COPY app
                # ./app seulement). app/Controller/education.png est identique
                # et déjà présent partout (Docker + build Nuitka), donc résolu
                # via get_real_path() plutôt qu'un chemin relatif au cwd.
                min_icon = get_real_path(os.path.join('app', 'Controller', 'education.png'))
                new_profile = Profile(
                    nom="Gestion d'école 360",
                    email='gestion.ecole@infinisoftware.cloud',
                    ligne1='+509 48453903',
                    ligne2="509 43542632",
                    adresse='#48 Delmas 75, Haïti',
                    logo_image_path='logo_path',
                    logo_image_base64=get_base64_encoded_image(min_icon)
                ) 
                db.add(new_profile)                
                # db.refresh(new_profile)
                db.commit()
                
            except Exception as e:
                logger.error(f"Erreur lors de la création: {str(e)}")
                db.rollback()
                raise HTTPException(
                    status_code=422,
                    detail={"errors": str(e)}
                )
            
            return PersonnelResponseMsg(message="Operation reussie")
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            import traceback
            traceback.print_exc()
            logger.error(f"Erreur transaction: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail={"errors": str(e)}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur globale: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={"errors": str(e)}
        )
 
def get_base64_encoded_image(chemin_image):
    """Convertit une image en Base64"""
    with open(chemin_image, "rb") as image_file:
        image_data = image_file.read()
    
        encoded_string = base64.b64encode(image_data).decode("utf-8", errors="ignore") 
        extension = chemin_image.split('.')[-1].lower() 
    return f"data:image/{extension};base64,{encoded_string}"
    
@router_personnel.patch("/active-personnel", response_model=SuccessResponse)
async def active_personnel(
    request: ActiveRequest,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("Modifier personnel")) 
):
    UserContext.set_user_id(current_user.id)
    """Active ou désactive un personnel"""
    try:
        personnel = db.query(Personnel).filter(Personnel.id == request.id).first()
        if not personnel:
            raise HTTPException(status_code=404, detail="Personnel non trouvé")
        
        user = db.query(User).filter(User.userable_id == request.id).first()
        
        if user:
            # print(user.status, not user.status)
            ActionContext.set_action('activated') if int(user.status) else ActionContext.set_action('deactivated')
            user.status = not int(user.status)
            db.commit()
            return SuccessResponse(
                success="Opération réussie",
                status=user.status
            )
        else:
            check_connect()
            alphabet = string.ascii_letters + string.digits
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(8))
            password = temp_password if Config.check_internet_connection() else "@#Itsme1"
            hashed_password = CryptAndDecript.hash_password(password) 

            UserContext.set_user_id(current_user.id)
            ActionContext.set_action('create in user')
            # hashed_password = CryptAndDecript.hash_password("@#Itsme1") #bcrypt.hashpw("@#Itsme1".encode('utf-8'), bcrypt.gensalt())
            
            new_user = User(
                name=personnel.prenom,
                email=personnel.email,
                status=True,
                password=hashed_password,#.decode('utf-8'),
                userable_id=personnel.id,
                userable_type="App\\Models\\Personnel"
            )
            db.add(new_user)
            db.commit()
            role = db.query(Role).filter(Role.name.in_(["user"])).first()
            if role:
                user_role = ModelHasRole(role_id=role.id,model_type="App\\Models\\User", model_id=new_user.id)
                db.add(user_role)
                if Config.check_internet_connection():
                    profile = db.query(Profile).first()
                    school_name = profile.nom if profile else "Notre École"

                       
                    send_activation_email(personnel.email, personnel.prenom, personnel.nom, personnel.email, temp_password,platform=school_name, role="personnel")
            db.commit()
            
            return SuccessResponse(
                success="Utilisateur créé et activé",
                status=True
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_personnel.patch("/change-password-personnel", response_model=SuccessResponse)
async def change_password_personnel(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Modifier personnel"))
):
    """Change le mot de passe d'un personnel"""
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action('update password')
    try:
        if not request.personnel_id:
            raise HTTPException(status_code=422, detail="ID personnel requis")
        
        user = db.query(User).filter(User.userable_id == request.personnel_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        if bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=422, detail="Le nouveau mot de passe doit être différent de l'ancien")
        
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password.decode('utf-8')
        db.commit()
        
        return SuccessResponse(success="Mot de passe changé avec succès")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router_personnel.patch("/active-etudiant", response_model=SuccessResponse)
async def active_student(
    request: ActiveRequest,
    db: Session = Depends(get_db),
    current_user = Depends(check_permission("Modifier etudiant")) 
):
    UserContext.set_user_id(current_user.id)
    
    etudiant = db.query(Etudiant).filter(Etudiant.id == request.id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    user = db.query(User).filter(User.userable_id == request.id).first()

    try:
        check_connect()
        
        # ✅ Si user existe déjà → juste activer/désactiver
        if user:
            ActionContext.set_action('activated') if int(user.status) else ActionContext.set_action('deactivated')
            user.status = not int(user.status)
            db.commit()
            return SuccessResponse(success="Opération réussie", status=user.status)

        # ✅ Seulement si user n'existe pas → vérifier email avant création
        if not etudiant.email:
            raise HTTPException(status_code=404, detail="L'étudiant doit avoir une adresse email")

        email_exists_in_users = db.query(
            select(User.id).where(User.email == etudiant.email).exists()
        ).scalar()

        email_exists_in_professeurs = db.query(
            select(Professeur.id).where(Professeur.email == etudiant.email).exists()
        ).scalar()

        email_exists_in_personnels = db.query(
            select(Personnel.id).where(Personnel.email == etudiant.email).exists()
        ).scalar()

        if email_exists_in_users or email_exists_in_professeurs or email_exists_in_personnels:
            raise HTTPException(status_code=404, detail="Cet email est déjà utilisé.")

        # ✅ Création du user
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(9))
        password = temp_password if Config.check_internet_connection() else "@#Itsme1"
        print(temp_password)
        print(temp_password)
        print(temp_password)
        hashed_password = CryptAndDecript.hash_password(password)

        UserContext.set_user_id(current_user.id)
        ActionContext.set_action('create in user')

        new_user = User(
            name=etudiant.prenom,
            email=etudiant.email,
            status=True,
            password=hashed_password,
            userable_id=etudiant.id,
            userable_type="App\\Models\\Etudiant"
        )
        db.add(new_user)
        db.flush()
        role = db.query(Role).filter(Role.name.in_(["student"])).first()

        if role:
            user_role = ModelHasRole(role_id=role.id, model_type="App\\Models\\User", model_id=new_user.id)
            db.add(user_role)
            if Config.check_internet_connection():
                profile = db.query(Profile).first()
                school_name = profile.nom if profile else "Notre École"
                send_activation_email(
                    to_email=etudiant.email,
                    prenom=etudiant.prenom,
                    nom=etudiant.nom,
                    email=etudiant.email,
                    password=temp_password,
                    platform=school_name,
                )
        db.commit()
        return SuccessResponse(success="Utilisateur créé et activé", status=True)

    except HTTPException:
        raise  # ✅ Laisse passer les HTTPException sans les attraper
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erreur")

# @router_personnel.patch("/active-etudiant", response_model=SuccessResponse)
# async def active_student(
#     request: ActiveRequest,
#     db: Session = Depends(get_db),
#     current_user = Depends(check_permission("Modifier etudiant")) 
# ):
#     UserContext.set_user_id(current_user.id)
#     """Active ou désactive un personnel"""
#     alphabet = string.ascii_letters + string.digits
#     temp_password = ''.join(secrets.choice(alphabet) for _ in range(9))
#     password = temp_password if Config.check_internet_connection() else "@#Itsme1"
#     hashed_password = CryptAndDecript.hash_password(password) 

#     etudiant = db.query(Etudiant).filter(Etudiant.id == request.id).first()
#     if not etudiant:
#         raise HTTPException(status_code=404, detail="Étudiant non trouvé")

#     user = db.query(User).filter(User.userable_id == request.id).first()

#     if not etudiant.email:
#         raise HTTPException(status_code=404, detail="l'étudiant doit avoir une adresse email ou modifier son profile et ajouter un nom d'utilisateur")
    
#     email_exists_in_users = db.query(
#         select(User.id)
#         .where(User.email == etudiant.email)
#         .exists()
#     ).scalar()
    
#     email_exists_in_professeurs = db.query(
#         select(Professeur.id)
#         .where(Professeur.email == etudiant.email)
#         .exists()
#     ).scalar()

#     email_exists_in_personnels = db.query(
#         select(Personnel.id)
#         .where(Personnel.email == etudiant.email)
#         .exists()
#     ).scalar()
    
#     if email_exists_in_users or email_exists_in_professeurs or email_exists_in_personnels:
#         raise HTTPException(status_code=404, detail="Cet email est déjà utilisé.")
#     try:
#         check_connect()
#         if user:
#             ActionContext.set_action('activated') if int(user.status) else ActionContext.set_action('deactivated')
#             user.status = not int(user.status)
 
#             db.commit()
#             return SuccessResponse(
#                 success="Opération réussie",
#                 status=user.status
#             )
#         else:            
#             UserContext.set_user_id(current_user.id)
#             ActionContext.set_action('create in user')
            
#             new_user = User(
#                 name=etudiant.prenom,
#                 email=etudiant.email,
#                 status=True,
#                 password=hashed_password,
#                 userable_id=etudiant.id,
#                 userable_type="App\\Models\\Etudiant"
#             )
#             db.add(new_user)
#             role = db.query(Role).filter(Role.name.in_(["student"])).first()
            
#             if role:
#                 user_role = ModelHasRole(role_id=role.id,model_type="App\\Models\\User", model_id=new_user.id)
#                 db.add(user_role)
#                 if Config.check_internet_connection():
#                     profile = db.query(Profile).first()
#                     school_name = profile.nom if profile else "Notre École"

#                     send_activation_email(
#                     to_email  = etudiant.email,
#                     prenom    = etudiant.prenom,
#                     nom       = etudiant.nom,
#                     email     = etudiant.email,
#                     password  = temp_password,  # mot de passe en clair avant hashage
#                     platform=school_name,
#                 )
#             db.commit()
#             return SuccessResponse(
#                 success="Utilisateur créé et activé",
#                 status=True
#             )
            
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail=str(e))

class UserchemaUpdate(BaseModel):
    id:str
    nom:str
    prenom:str
    email:str
    username:str
@router_personnel.patch("/user/profile", response_model=PersonnelResponseMsg)
async def update_student_profile(
    data: UserchemaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    UserContext.set_user_id(current_user.id)
    try:
        user = db.query(User).filter(User.userable_id == data.id).first()
        if not user:
            raise HTTPException(404, "Utilisateur non trouvé")
        
        if data.username and data.username != user.username:
            existing = db.query(User).filter(
                User.username == data.username,
                User.id != user.id
            ).first()

            if existing:
                raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris")
        
        if user.userable_type == 'App\\Models\\Personnel':
            personnel = db.query(Personnel).filter_by(id=user.userable_id).first()
            if personnel:
                personnel.nom = data.nom
                personnel.prenom = data.prenom
                personnel.email = data.email

                if personnel.user:
                    personnel.user.username = data.username
                    personnel.user.email = data.email
                    db.commit()                        
                return PersonnelResponseMsg(message="Operation reussie")
            
        elif user.userable_type == 'App\\Models\\Professeur':          
            professeur = db.query(Professeur).filter_by(id=user.userable_id).first()
            if professeur:
                professeur.nom = data.nom
                professeur.prenom = data.prenom
                professeur.email = data.email
                if professeur.user:
                    professeur.user.username = data.username
                    professeur.user.email = data.email
                    db.commit() 
                return PersonnelResponseMsg(message="Operation reussie")
        else:    
            raise HTTPException(404, "Utilisateur introuvable")
    except Exception as e:
        # print(e)
        # import traceback
        # traceback.print_exc()
        # logger.error(f"Erreur transaction: {str(e)}")
        raise HTTPException(404, "Utilisateur introuvable")


class SetPinRequest(BaseModel):
    pin: str = Field(..., pattern=r'^\d{6}$', description="Code PIN à 6 chiffres")


@router_personnel.get("/user/pin-status")
async def get_pin_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Indique si l'utilisateur courant a déjà défini un PIN — ne renvoie
    jamais le hash, seulement un booléen (utilisé par "Mon compte")."""
    return {"has_pin": bool(current_user.code_pin)}


@router_personnel.patch("/user/pin", response_model=PersonnelResponseMsg)
async def set_user_pin(
    data: SetPinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Définit/modifie le PIN d'autorisation — réservé aux rôles admin/
    Comptable, seuls habilités à approuver un retour ou une suppression
    pour le compte d'un autre utilisateur (cf. /auth/autorisation-access-pin)."""
    UserContext.set_user_id(current_user.id)
    if not user_has_role(current_user, ['admin', 'Comptable'], db):
        raise HTTPException(
            status_code=403,
            detail="Seuls les rôles admin ou Comptable peuvent définir un PIN d'autorisation.",
        )

    # Chaque PIN doit identifier un seul admin/Comptable sans ambiguïté
    # (/auth/autorisation-access-pin s'arrête au premier qui correspond) —
    # on vérifie donc l'unicité ici, mais sans jamais révéler qu'il s'agit
    # d'une collision (juste "code pin incorrect") pour ne pas laisser un
    # tiers déduire qu'un PIN donné est déjà pris par quelqu'un d'autre.
    others = (
        db.query(User)
        .join(ModelHasRole, ModelHasRole.model_id == User.id)
        .join(Role, Role.id == ModelHasRole.role_id)
        .filter(
            ModelHasRole.model_type == "App\\Models\\User",
            Role.name.in_(['admin', 'Comptable']),
            User.code_pin.isnot(None),
            User.id != current_user.id,
        )
        .distinct()
        .all()
    )
    if any(AuthorizationService.verify_password(data.pin, o.code_pin) for o in others):
        raise HTTPException(status_code=422, detail="Code PIN incorrect, choisissez-en un autre.")

    current_user.code_pin = CryptAndDecript.hash_password(data.pin)
    db.commit()
    return PersonnelResponseMsg(message="PIN enregistré avec succès")


def check_connect():
    import socket
    import smtplib

    host = "smtp.hostinger.com"
    user = "noreply@infini-software.cloud"
    password = "@Janvier1991"

    # Test 1 : résolution DNS
    print("Test 1 : Résolution DNS...")
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ DNS OK → {ip}")
    except Exception as e:
        print(f"❌ DNS échoué : {e}")
    
    # Test 2 : port 465
    print("\nTest 2 : Port 465 (SSL)...")
    try:
        with smtplib.SMTP_SSL(host, 465, timeout=10) as server:
            server.login(user, password)
            print("✅ Port 465 OK")
    except Exception as e:
        print(f"❌ Port 465 échoué : {e}")
    
    # Test 3 : port 587
    print("\nTest 3 : Port 587 (STARTTLS)...")
    try:
        with smtplib.SMTP(host, 587, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(user, password)
            print("✅ Port 587 OK")
    except Exception as e:
        print(f"❌ Port 587 échoué : {e}")