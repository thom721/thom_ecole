from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, asc
from app.Models.MFinancials import ParametrePaiement
from app.Models.MModels import Classe,Niveau,Faculte,AnneeAcademique
from app.Schemas.SPaiementParams import PaginatedParametrePaiementResponse,ParametrePaiementCreate,ParametrePaiementResponse,ParametrePaiementUpdate,ParametrePaiementResponseOne
from app.database import get_db
import math  
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, validator
import json
from app.dependencies.Dependencie import validate_exists
import re
from enum  import Enum


# mois = "janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre"
# prefixes = f"Versement|Trimestre|Session|Controle|{mois}"


# VERSEMENT_KEY_REGEX = re.compile(
#     rf"^(?:{prefixes})_[1-9]\d*_[a-f0-9\-]{36}$", 
#     re.IGNORECASE  # <--- Ceci acceptera "Versement" et "versement"
# )

MOIS = (
    "janvier|fevrier|mars|avril|mai|juin|"
    "juillet|aout|septembre|octobre|novembre|decembre"
)

PREFIXES = (
    "Versement|Trimestre|Session|Controle|" + MOIS
)

UUID_REGEX = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

VERSEMENT_KEY_REGEX = re.compile(
    rf"^({PREFIXES})_[1-9]\d*_({UUID_REGEX})$",
    re.IGNORECASE
)


router = APIRouter(prefix="/api/v1", tags=["Paramètres de Paiement"])

# GET paginé avec joins (comme ton Laravel)
@router.get("/parametrePaiement", response_model=PaginatedParametrePaiementResponse) 
def get_parametre_paiements(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    try:
        # Vérifier que les tables existent
        if not hasattr(db, 'query'):
            raise HTTPException(status_code=500, detail="Session de base de données invalide")
        
        # Aliases
        AnneeAcademiqueAlias = aliased(AnneeAcademique)
        ClasseAlias = aliased(Classe)
        FaculteAlias = aliased(Faculte)
        NiveauAlias = aliased(Niveau)
        
        # Construction de la requête
        query = (
            db.query(
                ParametrePaiement.id.label("paiementId"),
                ParametrePaiement.montant,
                ParametrePaiement.devise,
                ParametrePaiement.echeance,
                ParametrePaiement.niveau_id,
                ParametrePaiement.faculte_id,
                ParametrePaiement.classe,
                ParametrePaiement.anneeAcademique,
                ParametrePaiement.nb_echeance,
                ParametrePaiement.montant_par,
                ParametrePaiement.accessoires,
                ParametrePaiement.created_at,
                ParametrePaiement.updated_at,
                
                # Champs des relations
                NiveauAlias.name.label("name"),
                ClasseAlias.nom_classe.label("nom_classe"),
                FaculteAlias.nom.label("nom_faculte"),
                AnneeAcademiqueAlias.annee_academique.label("annee_academique")
            )
            .outerjoin(AnneeAcademiqueAlias, 
                      ParametrePaiement.anneeAcademique == AnneeAcademiqueAlias.id)
            .outerjoin(ClasseAlias, 
                      ParametrePaiement.classe == ClasseAlias.id)
            .outerjoin(FaculteAlias, 
                      ParametrePaiement.faculte_id == FaculteAlias.id)
            .outerjoin(NiveauAlias, 
                      ParametrePaiement.niveau_id == NiveauAlias.id)
            .order_by(desc(ParametrePaiement.updated_at))
            .order_by(asc(NiveauAlias.name))
        )
        
        # Optionnel: Filtre sur Niveau si la colonne status existe
        try:
            if hasattr(NiveauAlias, 'status'):
                query = query.filter(NiveauAlias.status == True)
        except:
            pass  # Ignore si la colonne n'existe pas
        
        # Compter
        total = query.count()
        
        # Pagination
        skip = (page - 1) * per_page
        results = query.offset(skip).limit(per_page).all()
        
        # Transformation des données
        data = []
        for row in results:
            # Gérer accessoires
            accessoires_data = row.accessoires
            if isinstance(accessoires_data, list):
                accessoires_final = {}
            else:
                accessoires_final = accessoires_data or {}
            
            # Gérer montant_par
            montant_par_data = row.montant_par
            if not isinstance(montant_par_data, dict):
                montant_par_data = {}
            
            item = {
                "id": str(row.paiementId), 
                "montant": str(row.devise) + " " + str(row.montant) if str(row.echeance) == "mois" else "Autres",
                "devise": str(row.devise) if row.devise else "",
                "echeance": str(row.echeance) if row.echeance else "",
                "paiement_par": str(row.echeance) if row.echeance else "",
                "montant_par":str(row.montant_par) if row.montant_par else "", #montant_par_data,
                "niveau_id": str(row.niveau_id) if row.niveau_id else "",
                "faculte_id": str(row.faculte_id) if row.faculte_id else None,
                "classe": str(row.nom_classe) if row.classe else "",
                "anneeAcademique": str(row.anneeAcademique) if row.anneeAcademique else "",
                "nb_echeance": int(row.nb_echeance) if row.nb_echeance is not None else None,
                "accessoires": accessoires_final,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "niveau_name": str(row.name) if row.name else None,
                "nom_classe": str(row.nom_classe) if row.nom_classe else None,
                "nom_faculte": str(row.nom_faculte) if row.nom_faculte else None,
                "annee_academique": str(row.annee_academique) if row.annee_academique else None
            }
            data.append(item)
        
        # Calcul des métadonnées
        last_page = math.ceil(total / per_page) if total and per_page > 0 else 1
        
        meta = {
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if data else 0,
            "to": skip + len(data) if data else 0
        }
        
        # Création de la réponse
        response_data = {
            "data": data,
            "meta": meta
        }
        
        return response_data
        
    except Exception as e:
        # Log l'erreur pour debug
        print(f"Erreur dans get_parametre_paiements: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur serveur: {str(e)}"
        ) 



# GET par ID
@router.get("/parametrePaiement/{paiement_id}", response_model=ParametrePaiementResponseOne)
def get_parametre_paiement(paiement_id: str, db: Session = Depends(get_db)):
    AnneeAcademiqueAlias = aliased(AnneeAcademique)
    ClasseAlias = aliased(Classe)
    FaculteAlias = aliased(Faculte)
    NiveauAlias = aliased(Niveau)
    
    result = (
        db.query(
            ParametrePaiement.id.label("paiementId"),
            ParametrePaiement.montant,
            ParametrePaiement.devise,
            ParametrePaiement.echeance,
            ParametrePaiement.niveau_id,
            ParametrePaiement.faculte_id,
            ParametrePaiement.classe,
            ParametrePaiement.anneeAcademique,
            ParametrePaiement.nb_echeance,
            ParametrePaiement.montant_par,
            ParametrePaiement.accessoires,
            ParametrePaiement.created_at,
            ParametrePaiement.updated_at,
            
            NiveauAlias.name.label("name"),
            ClasseAlias.nom_classe.label("nom_classe"),
            FaculteAlias.nom.label("nom_faculte"),
            AnneeAcademiqueAlias.annee_academique.label("annee_academique")
        )
        .outerjoin(AnneeAcademiqueAlias, 
                  ParametrePaiement.anneeAcademique == AnneeAcademiqueAlias.id)
        .outerjoin(ClasseAlias, 
                  ParametrePaiement.classe == ClasseAlias.id)
        .outerjoin(FaculteAlias, 
                  ParametrePaiement.faculte_id == FaculteAlias.id)
        .outerjoin(NiveauAlias, 
                  ParametrePaiement.niveau_id == NiveauAlias.id)
        .filter(ParametrePaiement.id == paiement_id, NiveauAlias.status == True)
        .first()
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Paramètre de paiement non trouvé")
    
    item= {
        "id": result.paiementId,
        "montant": result.montant,
        "devise": result.devise,
        "echeance": result.echeance,
        "montant_par": result.montant_par,
        "niveau_id": result.niveau_id,
        "faculte_id": result.faculte_id,
        "classe": result.classe,
        "anneeAcademique": result.anneeAcademique,
        "nb_echeance": result.nb_echeance,
        "accessoires": result.accessoires,
        "created_at": result.created_at,
        "updated_at": result.updated_at,
        "niveau_name": result.name,
        "nom_classe": result.nom_classe,
        "nom_faculte": result.nom_faculte,
        "annee_academique": result.annee_academique
    } 
    return ParametrePaiementResponseOne(data=item)

# POST créer
# @router.post("/", response_model=ParametrePaiementResponse, status_code=201)
# def create_parametre_paiement(
#     parametre: ParametrePaiementCreate,
#     db: Session = Depends(get_db)
# ):
#     # Vérifier que le niveau existe et est actif
#     niveau = db.query(Niveau).filter(
#         Niveau.id == parametre.niveau_id,
#         Niveau.status == True
#     ).first()
    
#     if not niveau:
#         raise HTTPException(status_code=404, detail="Niveau non trouvé ou inactif")
    
#     # Vérifier faculté si fournie
#     if parametre.faculte_id:
#         faculte = db.query(Faculte).filter(Faculte.id == parametre.faculte_id).first()
#         if not faculte:
#             raise HTTPException(status_code=404, detail="Faculté non trouvée")
    
#     # Créer
#     db_parametre = ParametrePaiement(**parametre.model_dump())
    
#     db.add(db_parametre)
#     db.commit()
#     db.refresh(db_parametre)
    
#     # Retourner avec joins
#     return get_parametre_paiement(db_parametre.id, db)

# PUT mettre à jour
@router.put("/parametrePaiement/{paiement_id}", response_model=ParametrePaiementResponse)
def update_parametre_paiement(
    paiement_id: str,
    parametre: ParametrePaiementUpdate,
    db: Session = Depends(get_db)
):
    # Trouver
    db_parametre = db.query(ParametrePaiement).filter(
        ParametrePaiement.id == paiement_id
    ).first()
    
    if not db_parametre:
        raise HTTPException(status_code=404, detail="Paramètre de paiement non trouvé")
    
    # Vérifier niveau si modifié
    if parametre.niveau_id:
        niveau = db.query(Niveau).filter(
            Niveau.id == parametre.niveau_id,
            Niveau.status == True
        ).first()
        if not niveau:
            raise HTTPException(status_code=404, detail="Niveau non trouvé ou inactif")
    
    # Vérifier faculté si modifiée
    if parametre.faculte_id:
        faculte = db.query(Faculte).filter(Faculte.id == parametre.faculte_id).first()
        if not faculte:
            raise HTTPException(status_code=404, detail="Faculté non trouvée")
    
    # Mettre à jour
    update_data = parametre.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_parametre, field, value)
    
    db.commit()
    db.refresh(db_parametre)
    
    return get_parametre_paiement(db_parametre.id, db)

# DELETE
@router.delete("/parametrePaiement/{paiement_id}", status_code=204)
def delete_parametre_paiement(paiement_id: str, db: Session = Depends(get_db)):
    parametre = db.query(ParametrePaiement).filter(
        ParametrePaiement.id == paiement_id
    ).first()
    
    if not parametre:
        raise HTTPException(status_code=404, detail="Paramètre de paiement non trouvé")
    
    db.delete(parametre)
    db.commit()
    
    return None

class TypeAccessoire(str, Enum):
    Maillot = "Maillot"
    Badge = "Badge"
    TenueDeSport = "Tenue de Sport"
    Initiale = "Initiale"

class AccessoireSchema(BaseModel):
    prix: float
    type_daccessoire: TypeAccessoire
# class AccessoireSchema(BaseModel):
#     prix: float = Field(..., gt=0)
#     type_daccessoire: str = Field(..., patern="^(Maillot|Badge|Tenue de Sport|Initiale)$")

class ParamPaiementSchema(BaseModel):
    id: Optional[str] = None
    niveau_id: str
    classe: str
    echeance: str
    devise: str
    anneeAcademique: str
    nb_echeance: Optional[int] = None
    montant: Optional[float] = None
    montant_par: Optional[Dict[str, float]] = None
    accessoires: Optional[List[AccessoireSchema]] = None
    class Config:
        from_attributes = True

# [str, float]


    # @validator("montant_par")
    # def validate_montant_par_keys(cls, montant_par, values):
    #     if not montant_par:
    #         return montant_par

    #     annee_id = values.get("anneeAcademique")
    #     if not annee_id:
    #         raise ValueError("anneeAcademique est requis pour valider montant_par")
        
    #     for key, value in montant_par.items():
    #         # 1️⃣ format global (Regex)
    #         print(key, value, VERSEMENT_KEY_REGEX)
    #         if not VERSEMENT_KEY_REGEX.match(key):
    #             raise ValueError(
    #                 f"Clé invalide `{key}`. Format attendu: "
    #                 "<type>_<index>_<uuid_annee> (ex: versement_1_uuid...)"
    #             )

    #         parts = key.split("_")
    #         key_uuid = parts[-1]  # L'UUID est toujours le dernier élément
            
    #         if key_uuid != str(annee_id):
    #             raise ValueError(
    #                 f"La clé `{key}` ne correspond pas à l'année académique active ({annee_id})"
    #             )

    #         # 3️⃣ valeur numérique positive
    #         try:
    #             numeric_value = float(value)
    #             if numeric_value <= 0:
    #                 raise ValueError(f"Le montant de `{key}` doit être supérieur à 0")
    #         except (TypeError, ValueError):
    #             raise ValueError(f"Le montant pour `{key}` doit être un nombre valide")

    #     return montant_par

        from pydantic import field_validator

        @field_validator("montant_par")
        @classmethod
        def validate_montant_par_keys(cls, montant_par, info):

            # m = data.get("montant")
            # if m == "None" or m == "" or m is None:
            #     data["montant"] = 0.0
            # else:
            #     try:
            #         data["montant"] = float(m)
            #     except ValueError:
            #         data["montant"] = 0.0
            #     if not montant_par:
            #         return montant_par

            annee_id = info.data.get("anneeAcademique")
            if not annee_id:
                raise ValueError("anneeAcademique est requis")

            for key, value in montant_par.items():
                match = VERSEMENT_KEY_REGEX.match(key)
                if not match:
                    raise ValueError(
                        f"Clé invalide `{key}`. "
                        f"Format attendu: <type>_<index>_<uuid>"
                    )

                key_uuid = match.group(2)

                if key_uuid != str(annee_id):
                    raise ValueError(
                        f"La clé `{key}` ne correspond pas à l'année académique active"
                    )

                try:
                    montant = float(value)
                    if montant <= 0:
                        raise ValueError
                except Exception:
                    raise ValueError(f"Le montant pour `{key}` doit être un nombre > 0")

            return montant_par

 

    @model_validator(mode='before')
    @classmethod
    def calculate_total_and_validate_keys(cls, data):
        montant = data.get("montant", 0)
        return montant
    
    @model_validator(mode="before")
    @classmethod
    def check_montant_fields(cls, values):
        echeance = values.get("echeance")
        montant = values.get("montant")
        nb_echeance = values.get("nb_echeance")
        montant_par = values.get("montant_par")

        if echeance == "mois" and (montant is None or montant <= 0):
            raise ValueError("Montant obligatoire pour une échéance mensuelle")
        if echeance != "mois" and (nb_echeance is None or not montant_par):
            raise ValueError("Montant par échéance obligatoire si autre que mensuelle")
        return values
    



def first_or_create(db: Session, model, search: dict, create: dict):
    instance = db.query(model).filter_by(**search).first()
    if instance:
        return instance
    instance = model(**{**search, **create})
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance

# -------------------------------
# Route FastAPI
# -------------------------------
@router.post("/parametrePaiement")
def store_param_paiement(data: ParamPaiementSchema, db: Session = Depends(get_db)):
    # Récupérer les dates de l'année académique

    validate_exists(Niveau, Niveau.id, db, data.niveau_id) 
    validate_exists(Classe, Classe.id, db, data.classe)
    # validate_exists(AnneeAcademique, AnneeAcademique.id, db, data.anneeAcademique)

    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == data.anneeAcademique).first()
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")

    start = datetime.strptime(str(annee.date_debut), "%Y-%m-%d")
    end   = datetime.strptime(str(annee.date_fin), "%Y-%m-%d")

    # Gestion des montants par mois
    if data.echeance == "mois":
        month_dict = {}
        dt = start
        while dt <= end:
            month_name = dt.strftime("%B").capitalize()
            month_dict[month_name] = data.montant
            dt = datetime(dt.year + (dt.month // 12), ((dt.month % 12) + 1), dt.day)
        data.nb_echeance = len(month_dict)
        data.montant_par = {data.echeance: month_dict}
        data.montant = None
    else:
        # Montant par échéance
        data.montant = None
        if not data.montant_par:
            raise HTTPException(status_code=422, detail="montant_par requis pour cette échéance")

    # Accessoires JSON
    accessoires_json = json.dumps([a.dict() for a in data.accessoires]) if data.accessoires else None

    validated_data = {
        "niveau_id": data.niveau_id,
        "classe": data.classe,
        "echeance": data.echeance,
        "devise": data.devise,
        "anneeAcademique": data.anneeAcademique,
        "nb_echeance": data.nb_echeance,
        "montant": data.montant,
        "montant_par": json.dumps(data.montant_par) if data.montant_par else None,
        "accessoires": accessoires_json
    }


    try:
        # Update si id fourni
        if data.id:
            instance = db.query(ParametrePaiement).filter(ParametrePaiement.id == data.id).first()
            if not instance:
                raise HTTPException(status_code=404, detail="Paramètre de paiement introuvable")
            for k, v in validated_data.items():
                setattr(instance, k, v)
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return {"success": True, "id": instance.id}

      
        instance = first_or_create(
            db,
            ParametrePaiement,
            search={
                "niveau_id": data.niveau_id,
                "classe": data.classe,
                "anneeAcademique": data.anneeAcademique
            },
            create=validated_data
        )
        return {"success": True, "id": instance.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
