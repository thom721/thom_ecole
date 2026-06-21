from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, asc
from app.Models.MFinancials import ParametrePaiement
from app.Models.MModels import Classe,Niveau,Faculte,AnneeAcademique,User
from app.Schemas.SPaiementParams import PaginatedParametrePaiementResponse,ParametrePaiementCreate,ParametrePaiementResponse,ParametrePaiementUpdate,ParametrePaiementResponseOne
from app.database import get_db
import math  
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field , field_validator, model_validator
import json
from app.Helper.context import UserContext,ActionContext ,AdminAuthorization
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
import re
from enum  import Enum


# mois = "janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre"
# prefixes = f"Versement|Trimestre|Session|Controle|{mois}"




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
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
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
        # query = (
        #     db.query(
        #         ParametrePaiement.id.label("paiementId"),
        #         ParametrePaiement.montant,
        #         ParametrePaiement.devise,
        #         ParametrePaiement.echeance,
        #         ParametrePaiement.niveau_id,
        #         ParametrePaiement.faculte_id,
        #         ParametrePaiement.classe,
        #         ParametrePaiement.anneeAcademique,
        #         ParametrePaiement.nb_echeance,
        #         ParametrePaiement.montant_par,
        #         ParametrePaiement.accessoires,
        #         ParametrePaiement.created_at,
        #         ParametrePaiement.updated_at,
                
        #         # Champs des relations
        #         NiveauAlias.name.label("name"),
        #         ClasseAlias.nom_classe.label("nom_classe"),
        #         FaculteAlias.nom.label("nom_faculte"),
        #         AnneeAcademiqueAlias.annee_academique.label("annee_academique")
        #     )
        #     .outerjoin(AnneeAcademiqueAlias, 
        #               ParametrePaiement.anneeAcademique == AnneeAcademiqueAlias.id)
        #     .outerjoin(ClasseAlias, 
        #               ParametrePaiement.classe == ClasseAlias.id)
        #     .outerjoin(FaculteAlias, 
        #               ParametrePaiement.faculte_id == FaculteAlias.id)
        #     .outerjoin(NiveauAlias, 
        #               ParametrePaiement.niveau_id == NiveauAlias.id)
        #     .order_by(desc(ParametrePaiement.updated_at))
        #     .order_by(asc(NiveauAlias.name))
        # )

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
                
                # Champs des relations (Jointures strictes)
                NiveauAlias.name.label("name"),
                ClasseAlias.nom_classe.label("nom_classe"),
                FaculteAlias.nom.label("nom_faculte"),
                AnneeAcademiqueAlias.annee_academique.label("annee_txt") # Nouveau label unique
            )
            .join(AnneeAcademiqueAlias, ParametrePaiement.anneeAcademique == AnneeAcademiqueAlias.id)
            .join(ClasseAlias, ParametrePaiement.classe == ClasseAlias.id)
            .join(NiveauAlias, ParametrePaiement.niveau_id == NiveauAlias.id)
            # On garde outerjoin pour la faculté seulement si elle est optionnelle
            .outerjoin(FaculteAlias, ParametrePaiement.faculte_id == FaculteAlias.id)
            .order_by(desc(ParametrePaiement.updated_at))
        )
        
        try:
            if hasattr(NiveauAlias, 'status'):
                query = query.filter(NiveauAlias.status == True)
        except:
            pass 
        
        total = query.count()
        
        skip = (page - 1) * per_page
        results = query.offset(skip).limit(per_page).all()
        
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
                # "anneeAc": str(row.annee_academique) if row.annee_academique else None
                "anneeAc": str(row.annee_txt) if row.annee_txt else "Non définie"
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
        import traceback
        traceback.print_exc()
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
        "anneeAc": result.annee_academique
    } 
    return ParametrePaiementResponseOne(data=item)



# PUT mettre à jour
@router.put("/parametrePaiement/{paiement_id}", response_model=ParametrePaiementResponse)
def update_parametre_paiement(
    paiement_id: str,
    parametre: ParametrePaiementUpdate,
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    # Trouver
    db_parametre = db.query(ParametrePaiement).filter(
        ParametrePaiement.id == paiement_id
    ).first()
    
    if not db_parametre:
        raise HTTPException(status_code=404, detail="Paramètre de paiement non trouvé")
    
    # Vérifier niveau si modifié
    UserContext.set_user_id(current_user.id)
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
@router.delete("/delete-parametrePaiement/{parametrePaiement}", status_code=204)
def delete_parametre_paiement(parametrePaiement: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    parametre = db.query(ParametrePaiement).filter(
        ParametrePaiement.id == parametrePaiement
    ).first()
    
    if not parametre:
        raise HTTPException(status_code=404, detail="Paramètre de paiement non trouvé")
    UserContext.set_user_id(current_user.id)
    db.delete(parametre)
    db.commit()
    
    return None


VERSEMENT_KEY_REGEX = re.compile(r"^([A-Za-z]+)_(\d+)_([a-f0-9\-]+)$")

class TypeAccessoire(str, Enum):
    Maillot = "Maillot"
    Badge = "Badge"
    TenueDeSport = "Tenue de Sport"
    Initiale = "Initiale"


class AccessoireSchema(BaseModel):
    prix: float = Field(..., gt=0, description="Prix de l'accessoire")
    type_daccessoire: TypeAccessoire


class ParamPaiementSchema(BaseModel):
    id: Optional[str] = None
    niveau_id: str
    classe: str   # Changé en Optional car votre JSON a None
    echeance: str
    devise: str
    anneeAcademique: str
    nb_echeance: Optional[int] = None
    montant: Optional[float] = None
    montant_par: Dict[str, float]
    accessoires: Optional[List[AccessoireSchema]] = None

    @field_validator("nb_echeance", mode="before")
    @classmethod
    def parse_nb_echeance(cls, v):
        """Convertir la chaîne en entier"""
        if v is None or v == "None":
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"nb_echeance doit être un entier, reçu: {v}")
        return v
    
    # @field_validator("classe", mode="before")
    # @classmethod
    # def parse_nb_echeance(cls, v):
    #     """Convertir la chaîne en entier"""
    #     if v is None or v == "None":
    #         return None
    #     if isinstance(v, str):
    #         try:
    #             return int(v)
    #         except ValueError:
    #             raise ValueError(f"La classe est obligatoire")
    #     return v

    @field_validator("montant", mode="before")
    @classmethod
    def parse_montant(cls, v):
        """Convertir la chaîne 'None' en None et parser les nombres"""
        if v is None or v == "None" or v == "":
            return None
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                raise ValueError(f"montant doit être un nombre, reçu: {v}")
        return v

    @field_validator("montant_par", mode="before")
    @classmethod
    def parse_and_validate_montant_par(cls, v, info):
        """Parser et valider montant_par"""
        if v is None or v == "None":
            return None
        
        # Si c'est une chaîne JSON, la parser
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("montant_par doit être un objet JSON valide")
        
        if not isinstance(v, dict):
            return v
        
        # Convertir les valeurs en float
        parsed_dict = {}
        for key, value in v.items():
            # Valider le format de la clé
            match = VERSEMENT_KEY_REGEX.match(key)
            if not match:
                raise ValueError(
                    f"Clé invalide `{key}`. "
                    f"Format attendu: <type>_<index>_<uuid>"
                )
            
            # Convertir la valeur en float
            try:
                montant_value = float(value) if value not in [None, "None", ""] else 0
                if montant_value <= 0:
                    raise ValueError(f"Le montant pour `{key}` doit être > 0")
                parsed_dict[key] = montant_value
            except (ValueError, TypeError):
                raise ValueError(f"Le montant pour `{key}` doit être un nombre > 0")
        
        # Valider que les UUID correspondent à l'année académique
        annee_id = info.data.get("anneeAcademique")
        if annee_id:
            for key in parsed_dict.keys():
                match = VERSEMENT_KEY_REGEX.match(key)
                key_uuid = match.group(3)  # Le UUID est le 3ème groupe
                
                if key_uuid != str(annee_id):
                    raise ValueError(
                        f"La clé `{key}` ne correspond pas à l'année académique {annee_id}"
                    )
        
        return parsed_dict

    @field_validator("accessoires", mode="before")
    @classmethod
    def parse_accessoires(cls, v):
        """Parser les accessoires depuis JSON si nécessaire"""
        if v is None or v == "None" or v == "" or v == []:
            return []
        
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                raise ValueError("accessoires doit être une liste JSON valide")
        
        return v

    @model_validator(mode="after")
    def check_montant_fields(self):
        """Valider la cohérence entre écheance, montant et montant_par"""
        if self.echeance == "mois":
            if self.montant is None or self.montant <= 0:
                raise ValueError("Montant obligatoire pour une échéance mensuelle")
        else:
            if self.nb_echeance is None or not self.montant_par:
                raise ValueError(
                    "nb_echeance et montant_par obligatoires pour une échéance autre que mensuelle"
                )
        
        return self


# ==================== ROUTE ====================

@router.post("/parametrePaiement")
def store_param_paiement(data: ParamPaiementSchema, db: Session = Depends(get_db),current_user: User = Depends(check_permission("Ajouter parametre"))):
    """
    Créer ou mettre à jour un paramètre de paiement
    """
    # Validation de l'existence des entités référencées
    validate_exists(Niveau, Niveau.id, db, data.niveau_id)
    
    if data.classe:  # Valider seulement si classe est fournie
        validate_exists(Classe, Classe.id, db, data.classe)
    
    # Récupérer l'année académique
    annee = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == data.anneeAcademique
    ).first()
    
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")
    UserContext.set_user_id(current_user.id)
    # Traitement des dates
    start = datetime.strptime(str(annee.date_debut), "%Y-%m-%d")
    end = datetime.strptime(str(annee.date_fin), "%Y-%m-%d")

    # Gestion des montants par mois
    if data.echeance == "mois":
        month_dict = {}
        dt = start
        if not data.montant:
            raise HTTPException(
                status_code=422, 
                detail="montant requis pour cette échéance"
            )
        
        # while dt <= end:
        #     month_name = dt.strftime("%B").capitalize()
        #     month_dict[month_name] = data.montant
            
        #     # Incrémenter le mois correctement
        #     if dt.month == 12:
        #         dt = datetime(dt.year + 1, 1, dt.day)
        #     else:
        #         dt = datetime(dt.year, dt.month + 1, dt.day)
        
        # data.nb_echeance = len(month_dict)
        # data.montant_par = {data.echeance: month_dict}
        # data.montant = None
    # else:
        # Pour les échéances non mensuelles, montant_par est déjà validé
        # data.montant = None
    if not data.montant_par:
        raise HTTPException(
            status_code=422, 
            detail="montant_par requis pour cette échéance"
        )


    from sqlalchemy import and_
    if data.id:
        # 1. On cherche si une AUTRE ligne possède déjà ces critères
        existing_param = db.query(ParametrePaiement).filter(
            and_(
                ParametrePaiement.niveau_id == data.niveau_id,
                ParametrePaiement.anneeAcademique == data.anneeAcademique,
                ParametrePaiement.classe == data.classe,
                ParametrePaiement.id != data.id  # On exclut l'enregistrement actuel
            )
        ).first()

        # 2. Si on trouve quelque chose, on arrête tout
        if existing_param:
            raise HTTPException(
                status_code=400,
                detail="Une configuration de paiement existe déjà pour ce niveau, cette année et cette classe."
            )
    else:
        existing_param = db.query(ParametrePaiement).filter(
            and_(
                ParametrePaiement.niveau_id == data.niveau_id,
                ParametrePaiement.anneeAcademique == data.anneeAcademique,
                ParametrePaiement.classe == data.classe  # On exclut l'enregistrement actuel
            )
        ).first()

        # 2. Si on trouve quelque chose, on arrête tout
        if existing_param:
            raise HTTPException(
                status_code=400,
                detail="Une configuration de paiement existe déjà pour ce niveau, cette année et cette classe."
            )
        # Préparer les accessoires pour JSON
    
    accessoires_json = None
    if data.accessoires:
        accessoires_json = [
            {
                "prix": a.prix,
                "type_daccessoire": a.type_daccessoire.value
            } 
            for a in data.accessoires
        ]
 
    dict_imbrique = {data.echeance: data.montant_par} if data.montant_par else None

    # On le transforme en JSON pour la base de données
    montant_par_json = json.dumps(dict_imbrique) if dict_imbrique else None

    # Données validées pour la base de données
    validated_data = {
        "niveau_id": data.niveau_id,
        "classe": data.classe,
        "echeance": data.echeance,
        "devise": data.devise,
        "anneeAcademique": data.anneeAcademique,
        "nb_echeance": data.nb_echeance,
        "montant": data.montant,
        "montant_par": dict_imbrique,#montant_par_json, 
        "accessoires": accessoires_json if accessoires_json else [] 
    }
        
    # motant_par = json.dumps(data.echeance:data.montant_par if data.montant_par else None)
    # # Données validées pour la base de données
    # validated_data = {
    #     "niveau_id": data.niveau_id,
    #     "classe": data.classe,
    #     "echeance": data.echeance,
    #     "devise": data.devise,
    #     "anneeAcademique": data.anneeAcademique,
    #     "nb_echeance": data.nb_echeance,
    #     "montant": data.montant,
    #     "montant_par": motant_par,#data.montant_par if data.montant_par else None,
    #     "accessoires": accessoires_json if accessoires_json else []
    # }
    try:
        # Mise à jour si ID fourni
        if data.id:
            instance = db.query(ParametrePaiement).filter(
                ParametrePaiement.id == data.id
            ).first()
            
            if not instance:
                raise HTTPException(
                    status_code=404, 
                    detail="Paramètre de paiement introuvable"
                )
            
            # Mettre à jour les champs
            for key, value in validated_data.items():
                setattr(instance, key, value)
            
            db.commit()
            db.refresh(instance)
            
            return {
                "success": True, 
                "id": instance.id,
                "message": "Paramètre mis à jour avec succès"
            }

        # Création ou récupération
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
        
        return {
            "success": True, 
            "id": instance.id,
            "message": "Paramètre créé avec succès"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de l'enregistrement: {str(e)}"
        )


# ==================== FONCTIONS UTILITAIRES ====================

def validate_exists(model, field, db: Session, value):
    """Vérifier qu'une entité existe dans la base de données"""
    if not value:
        return
    
    exists = db.query(model).filter(field == value).first()
    if not exists:
        raise HTTPException(
            status_code=404,
            detail=f"{model.__name__} avec {field.name}={value} introuvable"
        )


def first_or_create(db: Session, model, search: dict, create: dict):
    """
    Récupérer ou créer une instance
    Équivalent de Laravel firstOrCreate
    """
    # Chercher l'instance existante
    query = db.query(model)
    for key, value in search.items():
        query = query.filter(getattr(model, key) == value)
    
    instance = query.first()
    
    if instance:
        # Si trouvée, mettre à jour avec les nouvelles valeurs
        for key, value in create.items():
            setattr(instance, key, value)
        db.commit()
        db.refresh(instance)
        return instance
    
    # Sinon, créer une nouvelle instance
    instance = model(**create)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance

