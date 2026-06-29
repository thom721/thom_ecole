from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime,date
import json 
from dateutil.relativedelta import relativedelta
import logging
from app.Models.MModels import Etudiant,Niveau,Classe,AnneeAcademique,Faculte,User
from app.Models.MRelations import ClasseEtudiant
from app.Models.MFinancials import ParametrePaiement, Paiement,PaiementStatut
from collections import OrderedDict
from app.Models.MSystems import Log, Profile
import uuid as uuid_lib
from app.database import get_db
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
logger = logging.getLogger(__name__)
from app.Helper.context import UserContext,ActionContext
from sqlalchemy.orm.attributes import flag_modified

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class PaiementDetails(BaseModel):
    depot: Optional[float] = None
    depot_et_avance: Optional[float] = None
    montant: Optional[float] = None
    status: Optional[int] = None
    total_verse: Optional[float] = None
    total_annuel: Optional[float] = None
    device: Optional[float] = None
    employer: Optional[str] = None
    balance: Optional[float] = None
    avance: Optional[float] = None

class PaymentSaveInfoRequest(BaseModel):
    niveau_id: str = Field(..., description="ID du niveau")
    etudiant_id: str = Field(..., description="ID de l'étudiant")
    identifiant: str = Field(..., description="Identifiant de l'étudiant")
    classe: str = Field(..., description="ID de la classe")
    echeance: str = Field(..., description="Type d'échéance")
    prenom: str = Field(..., description="Prénom de l'étudiant")
    nom: str = Field(..., description="Nom de l'étudiant")
    index_paiement: Optional[str] = None
    devise: Optional[str] = None
    annee_academique: str = Field(..., description="Année académique")
    mois: Optional[Dict[str, Any]] = None
    paiement_details: PaiementDetails
    faculte_id: Optional[str] = None
    accessoires: Optional[Dict[str, bool]] = None
    must_refresh_paiement: Optional[bool] = False
    
    @field_validator('echeance')
    @classmethod
    def validate_echeance(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError("L'échéance doit contenir uniquement des lettres")
        return v
    
    @field_validator('identifiant')
    @classmethod
    def validate_identifiant(cls, v: str) -> str:
        # Valide alpha_dash: lettres, chiffres, tirets et underscores
        if not all(c.isalnum() or c in ['-', '_'] for c in v):
            raise ValueError("L'identifiant doit contenir uniquement des lettres, chiffres, tirets et underscores")
        return v
    
    @model_validator(mode='after')
    def validate_depot_required(self):
        """Valider que depot est requis si must_refresh_paiement est False"""
        if not self.must_refresh_paiement and self.paiement_details.depot is None:
            raise ValueError("Vous devez ajouter le montant")
        return self

class PaymentSaveInfoResponse(BaseModel):
    route: str
    id: str
    keys: int
    openInNewTab: bool

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def transform_payments(data: Any, type_bourse: str) -> Dict[str, Any]:
    """Transforme les paiements selon le type de bourse"""
    datas = data if isinstance(data, dict) else json.loads(data) if isinstance(data, str) else {}
    status = {}
    
    if not isinstance(datas, dict) or not datas:
        return status
    
    for key, payments in datas.items():
        if not isinstance(payments, dict):
            continue
        
        payment_keys = list(payments.keys())
        if not payment_keys:
            continue
            
        last_payment_key = payment_keys[-1]
        
        for payment_key, value in payments.items():
            if key != 'mois':
                parts = payment_key.split('_')
                if len(parts) < 3:
                    continue
                
                type_ = parts[0]
                versement_number = int(parts[1])
                
                is_last = payment_key == last_payment_key
                
                value_ = int(value)
                
                # Calcul selon le type de bourse
                if type_bourse == 'Bourse':
                    val_final = 0
                elif type_bourse == '1/4 Bourse':
                    val_final = int((value_ / 4) * 3)
                else:  # Démie Bourse
                    val_final = int(value_ / 2)
                
                global_calcul = value_ if (versement_number == 1 or type_bourse == 'Aucune') else val_final
                
                # Déterminer le suffixe
                if is_last:
                    suffix = 'er' if versement_number == 1 else 'ème'
                else:
                    if versement_number == 1:
                        suffix = 'ère' if type_ == 'Session' else 'er'
                    else:
                        suffix = 'ème'
                
                status[f"{versement_number}{suffix} {type_}"] = global_calcul
            else:
                status[payment_key] = value
    
    return status

def supprimer_dernier_paiement(
    paiement_details: Dict[str, Any],
    cle_soumise: str,
    data: Any,
    request_mois: Dict[str, Any],
    data_month_field: Dict[str, Any],
    db: Session
) -> tuple[bool, Optional[str]]:
    """Supprime le dernier paiement si c'est celui soumis"""
    
    try:
        # Vérifier si la clé soumise existe
        if 'info_paiement' not in paiement_details or cle_soumise not in paiement_details['info_paiement']:
            return False, "Clé de paiement introuvable"
        
        # Récupérer toutes les clés de paiement
        cles_paiement = list(paiement_details['info_paiement'].keys())
        
        # Trier par date (décroissant)
        cles_paiement.sort(
            key=lambda x: datetime.strptime(x.replace('/', '-'), '%d-%m-%Y %H:%M'),
            reverse=True
        )
        
        derniere_cle = cles_paiement[0]
        
        # Vérifier que c'est bien le dernier paiement
        if derniere_cle != cle_soumise:
            return False, "Seul le dernier paiement peut être modifié"
        
        # Récupérer le log
        last_key = data.last_paiement_key
        log = db.query(Log).filter(Log.paiement_key == last_key).first()
        
        if not log:
            logger.info("Aucun log à restaurer")
            return False, "Aucun log à restaurer"
        
        # Parser les anciennes valeurs
        old_values = log.old_values
        if isinstance(old_values, str):
            try:
                old_values = json.loads(old_values) if old_values else {}
            except json.JSONDecodeError:
                logger.error("JSON mal formé dans old_values")
                return False, "Erreur de format dans les anciennes valeurs"
        
        # Parser les nouvelles valeurs
        new_values = log.new_values
        if isinstance(new_values, str):
            new_values = json.loads(new_values) if new_values else {}
        
        # Si oldValues est vide (première création)
        if not old_values:
            # Supprimer les mois du dernier paiement
            if 'mois' in data_month_field and derniere_cle in paiement_details['info_paiement']:
                for key in paiement_details['info_paiement'][derniere_cle].keys():
                    if key in data_month_field['mois']:
                        del data_month_field['mois'][key]
                        if 'mois' in paiement_details:
                            paiement_details['mois'].pop(key, None)
            
            # Supprimer le paiement
            del paiement_details['info_paiement'][derniere_cle]
            return True, None
        
        # Restaurer les mois
        if 'mois' in paiement_details:
            for key in paiement_details['info_paiement'][derniere_cle].keys():
                if key in paiement_details['mois']:
                    if 'mois' in data_month_field:
                        data_month_field['mois'].pop(key, None)
                    paiement_details['mois'].pop(key, None)
        
        # Supprimer le paiement
        del paiement_details['info_paiement'][derniere_cle]
        
        logger.info("Paiement supprimé avec succès")
        return True, None
        
    except Exception as e:
        logger.error(f"Erreur dans supprimer_dernier_paiement: {str(e)}", exc_info=True)
        return False, str(e)

# ============================================================================
# VÉRIFICATION DES ARRIÉRÉS
# ============================================================================

def _check_arrears_previous_year(
    etudiant_id: str, current_annee_id: str, db: Session
) -> tuple:
    """
    Vérifie si l'étudiant a des versements non soldés pour l'année académique
    qui précède immédiatement l'année courante.

    Cas ignorés (→ False, None) :
      - Première année à l'établissement (≤ 1 inscription enregistrée)
      - Pas inscrit l'année précédente (gap year, nouveau cycle, etc.)
      - Aucune année précédente dans la base

    Retourne (has_arrears: bool, message: str | None).
    """
    # 1. Première année à l'établissement ?
    n_inscriptions = (
        db.query(ClasseEtudiant)
        .filter(ClasseEtudiant.etudiant_id == etudiant_id)
        .count()
    )
    if n_inscriptions <= 1:
        return False, None

    # 2. Récupérer l'année courante (besoin de date_debut pour ordonner)
    current_annee = (
        db.query(AnneeAcademique)
        .filter(AnneeAcademique.id == current_annee_id)
        .first()
    )
    if not current_annee:
        return False, None

    # 3. Année académique immédiatement précédente (la plus récente avant N)
    prev_annee = (
        db.query(AnneeAcademique)
        .filter(AnneeAcademique.date_debut < current_annee.date_debut)
        .order_by(AnneeAcademique.date_debut.desc())
        .first()
    )
    if not prev_annee:
        return False, None

    # 4. L'étudiant était-il inscrit l'année précédente ?
    prev_enrollment = (
        db.query(ClasseEtudiant)
        .filter(
            ClasseEtudiant.etudiant_id == etudiant_id,
            ClasseEtudiant.annee_academique_id == prev_annee.id,
        )
        .first()
    )
    if not prev_enrollment:
        # Pas inscrit l'an passé (gap, nouveau cycle) → pas d'arriéré à vérifier
        return False, None

    # 5. Paiement de l'année précédente
    prev_paiement = (
        db.query(Paiement)
        .filter(
            Paiement.etudiant_id == etudiant_id,
            Paiement.annee_academique == prev_annee.annee_academique,
        )
        .first()
    )
    if not prev_paiement:
        return True, (
            f"L'étudiant n'a aucun paiement enregistré pour l'année "
            f"{prev_annee.annee_academique}. Régularisez la situation avant "
            f"d'accepter un paiement pour l'année en cours."
        )

    # 6. Vérification principale via paiement_details → info_paiement
    pd_data = (
        json.loads(prev_paiement.paiement_details)
        if isinstance(prev_paiement.paiement_details, str)
        else prev_paiement.paiement_details
    )
    inner = pd_data.get("paiement_details", {})
    info_paiement = inner.get("info_paiement", {})

    if info_paiement:
        valid = [
            (k, v)
            for k, v in info_paiement.items()
            if v.get("status") != "retourné"
        ]
        if valid:
            try:
                valid.sort(
                    key=lambda x: datetime.strptime(
                        x[0].replace("/", "-"), "%d-%m-%Y %H:%M"
                    )
                )
            except ValueError:
                pass
            _, last = valid[-1]
            total_verse = int(last.get("total_verse") or 0)
            total_annuel = int(last.get("total_annuel") or 0)

            if last.get("status") == "Acquitté" or (
                total_annuel > 0 and total_verse >= total_annuel
            ):
                return False, None  # Entièrement soldé

            devise = inner.get("devise", "")
            reste = max(0, total_annuel - total_verse)
            return True, (
                f"L'étudiant a un solde impayé de {reste} {devise} "
                f"pour l'année {prev_annee.annee_academique}. "
                f"Régularisez avant d'accepter un paiement pour l'année en cours."
            )

    # 7. Secours : comparer nombre de versements attendus vs payés
    mois_data = (
        json.loads(prev_paiement.mois)
        if isinstance(prev_paiement.mois, str)
        else prev_paiement.mois
    )
    paid_keys = mois_data.get("mois", {})

    prev_param = (
        db.query(ParametrePaiement)
        .filter(
            ParametrePaiement.niveau_id == prev_enrollment.niveau_id,
            ParametrePaiement.classe == prev_enrollment.classes_id,
            ParametrePaiement.anneeAcademique == prev_annee.id,
        )
        .first()
    )
    if not prev_param:
        if not paid_keys:
            return True, (
                f"Impossible de vérifier les versements de l'année "
                f"{prev_annee.annee_academique}. Contactez l'administration."
            )
        return False, None

    montant_par = (
        json.loads(prev_param.montant_par)
        if isinstance(prev_param.montant_par, str)
        else prev_param.montant_par
    )
    expected = montant_par.get(prev_param.echeance, {})
    n_expected = len(expected)
    n_paid = len(paid_keys)

    if n_paid >= n_expected:
        return False, None

    return True, (
        f"L'étudiant a des arriérés non soldés pour l'année "
        f"{prev_annee.annee_academique} "
        f"({n_paid}/{n_expected} versement(s) acquitté(s)). "
        f"Régularisez avant d'accepter un paiement pour l'année en cours."
    )


# ============================================================================
# ROUTER
# ============================================================================
router_paie = APIRouter(prefix="/api/v1", tags=["Paiements"])

@router_paie.post("/post-payment-save", response_model=PaymentSaveInfoResponse)
async def payment_save_info(
    request: PaymentSaveInfoRequest,
    user:User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enregistrer ou mettre à jour les informations de paiement d'un étudiant
    
    Gère:
    - Les nouveaux paiements
    - Les modifications de paiements existants
    - Les bourses (Bourse, 1/4 Bourse, Démie Bourse, Aucune)
    - Les accessoires
    - Les versements multiples
    """
    # logger.warning("\n\n\n\n info_paiement vide ou invalide:", request)
    # print(request)
    UserContext.set_user_id(user.id)
    try:
        # Définir le timezone
        # datetime.now() utilisera automatiquement le timezone système
        
        # Vérifier les autorisations
        if not user_has_permission(user, "Ajouter paiement", db):
            raise HTTPException(status_code=404, detail="Vous n\'avez pas les permissions requise.")
        
        # Générer la date et UUID
        date_with_hours = datetime.now().strftime('%d-%m-%Y %H:%M')
        last_paiement_key = str(uuid_lib.uuid4())
        current_date = datetime.now().date()
        
        # Vérifier que l'étudiant existe
        etudiant_exists = db.query(
            select(Etudiant.id).where(Etudiant.id == request.etudiant_id).exists()
        ).scalar()
        
        if not etudiant_exists:
            raise HTTPException(
                status_code=422,
                detail="L'étudiant spécifié n'existe pas"
            )
        
        # Récupérer l'année académique
        annee_id = db.query(AnneeAcademique.id).filter(
            AnneeAcademique.annee_academique == request.annee_academique
        ).scalar()
        
        if not annee_id:
            raise HTTPException(
                status_code=422,
                detail="Année académique introuvable"
            )
        
        # Contrôle des arriérés — uniquement pour un nouveau paiement (pas une
        # modification d'un versement existant) et seulement si l'établissement
        # a activé la politique is_receive_arriere dans son profil.
        if not request.index_paiement:
            profile = db.query(Profile).first()
            if profile and profile.is_receive_arriere:
                has_arrears, arrears_msg = _check_arrears_previous_year(
                    request.etudiant_id, annee_id, db
                )
                if has_arrears:
                    raise HTTPException(status_code=422, detail=arrears_msg)

        # Récupérer les paramètres de paiement
        data_pay = db.query(ParametrePaiement).filter(
            ParametrePaiement.niveau_id == request.niveau_id,
            ParametrePaiement.classe == request.classe,
            ParametrePaiement.anneeAcademique == annee_id
        ).first()
        
        if not data_pay:
            raise HTTPException(
                status_code=422,
                detail="Paramètres de paiement non configurés pour ce niveau et cette classe"
            )
        
        # Parser les versements
        montant_par_data = json.loads(data_pay.montant_par) if isinstance(data_pay.montant_par, str) else data_pay.montant_par
        versements = montant_par_data.get(data_pay.echeance, {})
        
        # Récupérer le type de bourse
        type_bourse = db.query(Etudiant.aide_financiere).filter(
            Etudiant.id == request.etudiant_id
        ).scalar() or 'Aucune'
        
        # Trier les versements (clé format "Type_numéro", e.g. "Scolarité_1")
        def _versement_sort_key(item):
            try:
                return int(item[0].split('_')[1])
            except (IndexError, ValueError):
                return 0

        versements_sorted = OrderedDict(
            sorted(versements.items(), key=_versement_sort_key)
        )
        
        # Calculer les montants selon le type de bourse
        montants = [int(v) for v in versements_sorted.values()]
        
        if type_bourse == 'Bourse':
            montant_to_pay = montants[0]
        elif type_bourse == '1/4 Bourse':
            montant_to_pay = montants[0] + sum(montants[1:]) * 3 // 4
        elif type_bourse == 'Démie Bourse':
            montant_to_pay = montants[0] + sum(montants[1:]) // 2
        else:
            montant_to_pay = sum(montants)
        
        # Préparer les données validées
        validated_data = {
            'niveau_id': request.niveau_id,
            'etudiant_id': request.etudiant_id,
            # 'identifiant': request.identifiant,
            'classe': request.classe,
            # 'echeance': request.echeance,
            # 'prenom': request.prenom,
            # 'nom': request.nom,
            'annee_academique': request.annee_academique,
            'last_paiement_key': last_paiement_key,
            'faculte_id': request.faculte_id
        }

        
 
        
        # Initialiser paiement_details
        paiement_details_dict = request.paiement_details.dict(exclude_none=True)
        paiement_details_dict['total_annuel'] = montant_to_pay
        paiement_details_dict['employer'] = user.name
        paiement_details_dict['devise'] = data_pay.devise
        paiement_details_dict['aide_financiere'] = type_bourse
        paiement_details_dict['status_paiement'] = []
        paiement_details_dict['edit_by_id'] = ''
        paiement_details_dict['return_by_id'] = ''
        paiement_details_dict['edit_by'] = ''
        paiement_details_dict['return_by'] = ''
        
        request_mois = {}
        request_accessoires = {}
        
        # Transformer les paiements pour vérification
        check_echeance = transform_payments(data_pay.montant_par, type_bourse)
        
        # Vérifier si un paiement existe déjà
        data = db.query(Paiement).filter(
            Paiement.niveau_id == request.niveau_id,
            Paiement.etudiant_id == request.etudiant_id,
            Paiement.annee_academique == request.annee_academique
        ).first()

        if request.index_paiement:
            ActionContext.set_action('update')
        else:
            ActionContext.set_action('create')
        
        if data:
            # ============================================================
            # MISE À JOUR D'UN PAIEMENT EXISTANT
            # ============================================================
            
            details = request.paiement_details.dict(exclude_none=True)
            
            # Parser les données existantes
            data_payment = json.loads(data.paiement_details) if isinstance(data.paiement_details, str) else data.paiement_details
            data_month_field = json.loads(data.mois) if isinstance(data.mois, str) else data.mois
            # print("\n\ndata_month_field")
            # print(data.mois)
            # print(data.paiement_details)
            # print("data_month_field\n\n")
            # Récupérer le dernier type de bourse
            details_etudiant = data_payment.get('paiement_details', {}).get('details_etudiant', {})
            if isinstance(details_etudiant, str):
                details_etudiant = json.loads(details_etudiant)
            
            last_bourse_type = details_etudiant.get('aide_financiere', type_bourse)
            
            # Gestion de la modification de paiement
            if request.index_paiement and last_bourse_type == type_bourse:
                user_has_permission(user, "Modifier paiement", db)
                # set_perso_action("update")
                print('if not success:  1')
                paiement_details_dict['edit_by_id'] = user.id
                paiement_details_dict['edit_by'] = user.name
                paiement_details_dict['return_by_id'] = ''
                paiement_details_dict['return_by'] = ''
                
                # Supprimer le dernier paiement
                # success, error_msg = supprimer_dernier_paiement(
                #     data_payment['paiement_details'],
                #     request.index_paiement,
                #     data,
                #     request_mois,
                #     data_month_field,
                #     db
                # )
                
                # if not success:
                #     raise HTTPException(
                #         status_code=422,
                #         detail={"errors": f"Seul le dernier paiement peut être modifié. {error_msg or ''}"}
                #     )
            else:
                pass
                # set_perso_action("create")
            
            # Parser les accessoires
            accessoires = json.loads(data_pay.accessoires) if isinstance(data_pay.accessoires, str) else data_pay.accessoires or {}
            
            # Récupérer le dernier paiement non retourné
            info_paiement = data_payment.get('paiement_details', {}).get('info_paiement', {})
            last_info = None
            
            for date_key in reversed(list(info_paiement.keys())):
                entry = info_paiement[date_key]
                if entry.get('status', '') != 'retourné':
                    last_info = entry
                    break
            
            if last_info:
                new_payment = last_info.get('depot_et_avance', 0)
                total_verse = last_info.get('total_verse', 0)
                total_annuel = last_info.get('total_annuel', 0)
            else:
                logger.warning("info_paiement vide ou invalide")
                new_payment = 0
                total_verse = 0
                total_annuel = 0
            
            paiement_details_dict['avance'] = f"{int(details.get('depot', 0))} + {int(new_payment)}"
            
            remaining_depot = int(details.get('depot', 0)) + int(new_payment)
            acquitte_paie = int(details.get('depot', 0)) + int(new_payment)
            
            # Traitement des accessoires
            total_accessoires = 0
            # end_accessoir = list(data_payment.get('paiement_details', {}).get('accessoires', {}).values())
            paiement_details = data_payment.get("paiement_details", {})
            accessoires = paiement_details.get("accessoires", {})

            # if not isinstance(accessoires, list):
            #     raise ValueError("accessoires doit être une liste")

            end_accessoir = accessoires

            end_accessoir = end_accessoir[-1] if end_accessoir else {}
            
            if isinstance(end_accessoir, str):
                end_accessoir = json.loads(end_accessoir)
            
            if request.accessoires and accessoires:
                for accessoire in accessoires:
                    type_acc = accessoire.get("type_daccessoire")
                    if type_acc and type_acc not in end_accessoir and request.accessoires.get(type_acc):
                        total_accessoires += float(accessoire.get("prix", 0))
                        if 'accessoire' not in request_accessoires:
                            request_accessoires['accessoire'] = {}
                        request_accessoires['accessoire'][type_acc] = request.accessoires[type_acc]
                
                if remaining_depot < total_accessoires:
                    raise HTTPException(
                        status_code=422,
                        detail="Le montant est insuffisant pour les accessoires choisis"
                    )
            
            # Calculer les versements
            status = transform_payments(data_pay.montant_par, type_bourse)
            paiement_details_dict['total_verse'] = int(total_verse) + int(details.get('depot', 0))
            
            # Gestion du changement de type de bourse
            if (last_bourse_type != type_bourse and 
                data_month_field.get('mois') and 
                len(data_month_field.get('mois', {})) > 1):
                # Recalculer tous les paiements avec le nouveau type de bourse
                payment_info_without_help = json.loads(data.paiement_details) if isinstance(data.paiement_details, str) else data.paiement_details
                
                info___ = payment_info_without_help.get('paiement_details', {}).get('info_paiement', {})
                
                # Trier par date
                info_sorted = OrderedDict(
                    sorted(
                        info___.items(),
                        key=lambda x: datetime.strptime(x[0].replace('/', '-'), '%d-%m-%Y %H:%M')
                    )
                )
                
                info_keys = list(info_sorted.keys())
                info_index = 0
                versements_payes = {}
                
                for current_key in info_keys:
                    details__ = info_sorted[current_key]
                    if details__.get('status') == 'retourné':
                        continue
                    details__['status_paiement'] = []                    

                    if details__.get('status') == 'Acquitté':
                        if details__.get("total_verse", 0) >= montant_to_pay:
                            # details__['status'] = 'Acquitté'
                            details__['remise'] = details__["total_verse"] - montant_to_pay if details__["total_verse"] >= montant_to_pay else 0
                        # continue
                    
                    last_payment_avance = 0
                    if info_index > 0:
                        prev_key = info_keys[info_index - 1]
                        last_payment_avance = int(info_sorted[prev_key].get('depot_et_avance', 0))
                    
                    depot_courant = int(details__.get('depot', 0)) + last_payment_avance
                     
                    for key, value in versements_sorted.items():
                        if key in versements_payes:
                            continue
                        
                        value_ = int(value)
                        get_versement_place = key.split('_')[1]
                        
                        # Calcul selon bourse
                        if type_bourse == 'Bourse':
                            val_final = 0
                        elif type_bourse == '1/4 Bourse':
                            val_final = int((value_ / 4) * 3)
                        else:
                            val_final = int(value_ / 2)
                        
                        global_calcul = value_ if (get_versement_place == '1' or type_bourse == 'Aucune') else val_final
                        
                        
                        if depot_courant >= global_calcul:
                            status[key] = value
                            request_mois[key] = global_calcul
                            
                            versement_num = key.split('_')[1]
                            versement_type = key.split('_')[0]
                            suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                            
                            # if 'status_paiement' not in details__:
                            #     details__['status_paiement'] = []
                            # v = {suffix} {versement_type}
                            # status_dict[label] = f"Acqt: {label}"
                            details__['status_paiement'].append(f"Acqt: {suffix} {versement_type}")
                            # details__['status_paiement'] = list(set(details__['status_paiement']))
                            
                            details__['depot'] = info_sorted[current_key].get('depot', 0)
                            depot_courant -= global_calcul
                            
                            details__['aide_financiere'] = type_bourse
                            details__['total_annuel'] = montant_to_pay
                            details__[key] = global_calcul
                            
                            versements_payes[key] = True
                        else:
                            versement_num = key.split('_')[1]
                            versement_type = key.split('_')[0]
                            suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                       
                            details__['status_paiement'].append(f"Avns: {suffix} {versement_type}")
                        
                        
                            details__['depot_et_avance'] = depot_courant
                            details__['balance'] = global_calcul - depot_courant
                            details__['aide_financiere'] = type_bourse
                            details__['total_annuel'] = montant_to_pay
                            
                            info_index += 1
                            break
                        
                    details__['aide_financiere'] = type_bourse
                    details__['total_annuel'] = montant_to_pay
                    details__['edit_by_id'] = user.id
                    details__['edit_by'] = user.name
                    details__['return_by_id'] = ''
                    details__['return_by'] = ''
                    
                    if details__.get("total_verse", 0) >= montant_to_pay:
                        details__['status'] = 'Acquitté'
                        details__['remise'] = details__["total_verse"] - montant_to_pay if details__["total_verse"] >= montant_to_pay else 0

                    # info_sorted[current_key] = details__
                    payment_info_without_help['paiement_details']['info_paiement'] = info_sorted
                
                # Récupérer les infos de classe/niveau/faculté
                classe = db.query(Classe.nom_classe).filter(Classe.id == request.classe).scalar()
                niveau = db.query(Niveau.name).filter(Niveau.id == request.niveau_id).scalar()
                faculte = db.query(Faculte.nom).filter(Faculte.id == request.faculte_id).scalar() if request.faculte_id else None
                
                payment_info_without_help['paiement_details']['details_etudiant'] = {
                    'identifiant': request.identifiant,
                    'nom': request.nom,
                    'prenom': request.prenom,
                    'aide_financiere': type_bourse,
                    'classe': classe,
                    'niveau': niveau,
                    'faculte': faculte,
                    'annee_academique': request.annee_academique
                }
                # data.paiement_details['paiement_details']['info_paiement'] = info_sorted
                payment_info_without_help['paiement_details']['mois'] = request_mois
                payment_info_without_help['paiement_details']['check_echeance'] = check_echeance
                payment_info_without_help['paiement_details']['aide_financiere'] = type_bourse
                
                # Merge accessoires
                if 'accessoires' not in payment_info_without_help['paiement_details']:
                    payment_info_without_help['paiement_details']['accessoires'] = {}
                
                for key, value in request_accessoires.items():
                    if key not in payment_info_without_help['paiement_details']['accessoires']:
                        payment_info_without_help['paiement_details']['accessoires'][key] = {}
                    payment_info_without_help['paiement_details']['accessoires'][key].update(value)
                
                data.paiement_details = payment_info_without_help    
                # data.paiement_details['paiement_details']['info_paiement'] = info_sorted    
                # print(f"\n\n\n\n{payment_info_without_help}\n\n\n\n\n")       
                flag_modified(data, "paiement_details")

                data.mois = {'mois': request_mois} 
                flag_modified(data, "mois")

                data.last_paiement_key = last_paiement_key
                db.commit()
                
            else:
                if remaining_depot > total_annuel:
                    raise HTTPException(
                    status_code=422,
                    detail="Le versement en cours dépasse le montant total annuel."
                ) 
                for key, value in versements_sorted.items():
                    if key not in data_month_field.get('mois', {}):
                        value_ = int(value)
                        get_versement_place = key.split('_')[1]
                        
                        # Calcul selon bourse
                        if type_bourse == 'Bourse':
                            val_final = 0
                        elif type_bourse == '1/4 Bourse':
                            val_final = int((value_ / 4) * 3)
                        else:
                            val_final = int(value_ / 2)
                        
                        global_calcul = value_ if (get_versement_place == '1' or type_bourse == 'Aucune') else val_final
                        
                        if remaining_depot >= global_calcul:
                            status[key] = value
                            request_mois[key] = global_calcul
                            
                            versement_num = key.split('_')[1]
                            versement_type = key.split('_')[0]
                            suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                            
                            paiement_details_dict['status_paiement'].append(f"Acqt: {suffix} {versement_type}")
                            remaining_depot -= global_calcul
                        else:
                            paiement_details_dict['depot_et_avance'] = remaining_depot
                            paiement_details_dict['balance'] = global_calcul - remaining_depot if global_calcul > remaining_depot else remaining_depot - global_calcul
                            
                            if remaining_depot > 0:
                                versement_num = key.split('_')[1]
                                versement_type = key.split('_')[0]
                                suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                                paiement_details_dict['status_paiement'].append(f"Avns: {suffix} {versement_type}")
                            break
                
                # Mise à jour check_echeance si non existant
                # if 'check_echeance' not in data_payment.get('paiement_details', {}):
                data_payment['paiement_details']['check_echeance'] = check_echeance
                # On récupère les données existantes en s'assurant que c'est un dict
                m = data_month_field.get('mois', {})
                m1 = request_mois
                # print(f"\ndata_month0000000000000_field\n\n{m}\n\n\n")
                # print(f"\nreque----------------st_mois\n\n{m1}\n\n\n")
                # return
                existing_months = data_month_field.get('mois')
                if not isinstance(existing_months, dict):
                    existing_months = {}

                # # On récupère les nouveaux mois de la requête
                # request_months = request.mois if hasattr(request, 'mois') else {}
                if not isinstance(request_mois, dict):
                    request_mois = {}

                # # Fusion sécurisée
                new_data_for_month = {**existing_months, **request_mois}

                # new_data_for_month = {**data_month_field.get('mois', {}), **request_mois}
                
                # Récupérer les infos
                classe = db.query(Classe.nom_classe).filter(Classe.id == request.classe).scalar()
                niveau = db.query(Niveau.name).filter(Niveau.id == request.niveau_id).scalar()
                faculte = db.query(Faculte.nom).filter(Faculte.id == request.faculte_id).scalar() if request.faculte_id else None

                data_payment['paiement_details']['details_etudiant'] = {
                    'identifiant': request.identifiant,
                    'nom': request.nom,
                    'prenom': request.prenom,
                    'aide_financiere': type_bourse,
                    'classe': classe,
                    'niveau': niveau,
                    'faculte': faculte,
                    'annee_academique': request.annee_academique
                }
            # Merge mois
            if 'mois' not in data_payment['paiement_details']:
                data_payment['paiement_details']['mois'] = {}
            if not isinstance(data_payment['paiement_details'].get('mois'), dict):
                data_payment['paiement_details']['mois'] = {}
            data_payment['paiement_details']['mois'].update(request_mois)
            
            # Merge accessoires
            if 'accessoires' not in data_payment['paiement_details']:
                data_payment['paiement_details']['accessoires'] = {}
            
            for key, value in request_accessoires.items():
                if key not in data_payment['paiement_details']['accessoires']:
                    data_payment['paiement_details']['accessoires'][key] = {}
                data_payment['paiement_details']['accessoires'][key].update(value)
            
            # Vérifier si acquitté
            if acquitte_paie >= montant_to_pay:
                paiement_details_dict['status'] = 'Acquitté'
            
            # Ajouter le nouveau paiement
            print(paiement_details_dict, request_mois)
            date_key = request.index_paiement if request.index_paiement else date_with_hours
            data_payment['paiement_details']['info_paiement'][date_key] = {
                **paiement_details_dict,
                **request_mois
            }
            
            # Sauvegarder
            # data.paiement_details = json.dumps(data_payment)
            # data.mois = json.dumps({'mois': new_data_for_month})
            if last_bourse_type == type_bourse or len(data_month_field.get('mois', {})) <= 1: 
                data.paiement_details = data_payment
                flag_modified(data, "paiement_details")

                data.mois = {'mois': new_data_for_month}
                flag_modified(data, "mois")

                data.last_paiement_key = last_paiement_key
                db.commit()
            else:
              print('data.paiement_details = data_payment')
            #   print(len(data_month_field.get('mois', {})))
            #   print('data.paiement_details = data_payment')

                # data.paiement_details = data_payment
                # data.mois = {'mois': new_data_for_month}
                # data.last_paiement_key = last_paiement_key
                # db.commit()

    
        else:
            # ============================================================
            # NOUVEAU PAIEMENT
            # ============================================================
            pass
            # set_perso_action("create")
            
            # Parser les accessoires
            accessoires = json.loads(data_pay.accessoires) if isinstance(data_pay.accessoires, str) else data_pay.accessoires or {}
            
            details = request.paiement_details.dict(exclude_none=True)
            paiement_details_dict['devise'] = data_pay.devise
            
            status = transform_payments(data_pay.montant_par, type_bourse)
            
            remaining_depot = int(details.get('depot', 0))
            acquitt_p = int(details.get('depot', 0))

            if remaining_depot > montant_to_pay:
                raise HTTPException(
                    status_code=422,
                    detail="Le versement en cours dépasse le montant total annuel."
                )
            # Traitement des accessoires
            total_accessoires = 0
            if request.accessoires and accessoires:
                for accessoire in accessoires:
                    type_acc = accessoire.get("type_daccessoire")
                    if type_acc and request.accessoires.get(type_acc):
                        total_accessoires += float(accessoire.get("prix", 0))
                        if 'accessoire' not in request_accessoires:
                            request_accessoires['accessoire'] = {}
                        request_accessoires['accessoire'][type_acc] = request.accessoires[type_acc]
                
                if remaining_depot < total_accessoires:
                    raise HTTPException(
                        status_code=422,
                        detail="Le montant est insuffisant pour les accessoires choisis"
                    )
            
            paiement_details_dict['total_verse'] = remaining_depot
            
            # Calculer les versements
            for key, value in versements_sorted.items():
                value_ = int(value)
                get_versement_place = key.split('_')[1]
                
                # Calcul selon bourse
                if type_bourse == 'Bourse':
                    val_final = 0
                elif type_bourse == '1/4 Bourse':
                    val_final = int((value_ / 4) * 3)
                else:
                    val_final = int(value_ / 2)
                
                global_calcul = value_ if (get_versement_place == '1' or type_bourse == 'Aucune') else val_final
                
                if remaining_depot >= global_calcul:
                    status[key] = True
                    request_mois[key] = global_calcul
                    
                    versement_num = key.split('_')[1]
                    versement_type = key.split('_')[0]
                    suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                    
                    paiement_details_dict['status_paiement'].append(f"Acqt: {suffix} {versement_type}")
                    remaining_depot -= global_calcul

                else:
                    paiement_details_dict['depot_et_avance'] = remaining_depot
                    paiement_details_dict['balance'] = global_calcul - remaining_depot if global_calcul > remaining_depot else remaining_depot - global_calcul
                    
                    if remaining_depot > 0:
                        versement_num = key.split('_')[1]
                        versement_type = key.split('_')[0]
                        suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                        paiement_details_dict['status_paiement'].append(f"Avns: {suffix} {versement_type}")
                    break
             
            if int(acquitt_p) >= int(montant_to_pay):
                paiement_details_dict['status'] = 'Acquitté'
         
            validated_data['mois'] = {'mois': request_mois}
             
            classe = db.query(Classe.nom_classe).filter(Classe.id == request.classe).scalar()
            niveau = db.query(Niveau.name).filter(Niveau.id == request.niveau_id).scalar()
            faculte = db.query(Faculte.nom).filter(Faculte.id == request.faculte_id).scalar() if request.faculte_id else None
            
 
            validated_data['paiement_details'] = {
                'paiement_details': {
                    'info_paiement': {
                        date_with_hours: {**paiement_details_dict, **request_mois}
                    },
                    'mois': request_mois,
                    'check_echeance': check_echeance,
                    'aide_financiere': type_bourse,
                    'accessoires': request_accessoires,
                    'details_etudiant': {
                        'identifiant': request.identifiant,
                        'nom': request.nom,
                        'prenom': request.prenom,
                        'aide_financiere': type_bourse,
                        'classe': classe,
                        'niveau': niveau,
                        'faculte': faculte,
                        'annee_academique': request.annee_academique
                    }
                }
            }
            
            # Créer ou récupérer le paiement
            payment = db.query(Paiement).filter(
                Paiement.etudiant_id == request.etudiant_id,
                Paiement.annee_academique == request.annee_academique
            ).first()
            print(validated_data)
            if not payment:
                payment = Paiement(**validated_data)
                db.add(payment)
                db.commit()
                db.refresh(payment)
        
        # Calculer l'index
        payment = db.query(Paiement).filter(
                Paiement.etudiant_id == request.etudiant_id,
                Paiement.annee_academique == request.annee_academique
            ).first()
        payment_data = json.loads(payment.paiement_details) if isinstance(payment.paiement_details, str) else payment.paiement_details
        # ind = len(payment_data.get('paiement_details', {}).get('info_paiement', {})) - 1
        info_paiement = payment_data.get('paiement_details', {}).get('info_paiement', {})

        if not info_paiement:
            raise HTTPException(
                status_code=400, 
                detail="info paiement vide ou invalide — aucun détail de paiement trouvé"
            )

        ind = len(info_paiement) - 1
        print(payment.id,ind)
        data_status={
            'mois':payment.mois,
            'annee_id':payment.annee_academique,
        }
        if payment.mois and payment.annee_academique:
            try:
                process_paiement_statut(db, payment.mois, payment.annee_academique, request.etudiant_id)
            except Exception as ps_err:
                logger.warning(f"process_paiement_statut non-bloquant (paiement déjà sauvegardé): {ps_err}")
        return PaymentSaveInfoResponse(
            route='print-recu',
            id=payment.id,
            keys=ind,
            openInNewTab=True
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur dans payment_save_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})
    
def process_paiement_statut(db: Session, mois, annee_academique_field, etudiant_id):
    """
    Traite et enregistre le statut de paiement d'un étudiant.
    
    Args:
        db: Session SQLAlchemy
        data: Données du paiement (doit avoir etudiant_id, annee_id, mois)
        annee_academique_field: Optionnel, si le champ s'appelle autrement
    
    Returns:
        PaiementStatut mis à jour ou créé
    """
    
    # 1. Récupère l'année académique
    # annee_value = getattr(data, annee_academique_field or "annee_id")
    annee = db.query(AnneeAcademique).filter(
        AnneeAcademique.annee_academique == annee_academique_field
    ).first()

    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")

    # 2. Récupère tous les mois de l'année
    tous_les_mois = get_mois_entre(annee.date_debut, annee.date_fin)

    # 3. Analyse les versements acquittés
    versements_acquittes = set()
    mois_data = mois.get("mois", mois)  # use inner dict if nested, else use as-is

    for key in mois_data.keys():
        parts = key.split("_")
        if len(parts) < 2:
            continue
        numero = int(parts[1])
        suffix = "er" if numero == 1 else "ème"
        label = f"{numero}{suffix} Versement"
        versements_acquittes.add(label)
    # for key in mois.keys():
      
    #     print("mois keys:",mois, list(mois.keys()))
    #     numero = int(key.split("_")[1])
    #     suffix = "er" if numero == 1 else "ème"
    #     label = f"{numero}{suffix} Versement"
    #     versements_acquittes.add(label)

    # 4. Calcule les mois accessibles selon les versements
    versement_mois = {
        "1er Versement": 3,
        "2ème Versement": 3,
        "3ème Versement": 2,
        "4ème Versement": 2,
    }

    total_mois_accessibles = sum(
        nb_mois
        for versement, nb_mois in versement_mois.items()
        if versement in versements_acquittes
    )

    mois_accessibles = tous_les_mois[:total_mois_accessibles]
    mois_bloques = tous_les_mois[total_mois_accessibles:]

    # 5. Enregistre ou met à jour dans PaiementStatut
    statut = db.query(PaiementStatut).filter(
        PaiementStatut.etudiant_id == etudiant_id,
        PaiementStatut.annee_id == annee.id
    ).first()

    if statut:
        anciens_mois = statut.mois_accessibles or []
        statut.mois_accessibles = list(dict.fromkeys(anciens_mois + mois_accessibles))
        statut.mois_bloques = [m for m in tous_les_mois if m not in statut.mois_accessibles]
        statut.updated_at = datetime.utcnow()
    else:
        statut = PaiementStatut(
            etudiant_id=etudiant_id,
            annee_id=annee.id,
            mois_accessibles=mois_accessibles,
            mois_bloques=mois_bloques,
        )
        db.add(statut)

    db.commit()
    db.refresh(statut)

def process_paiement_statut1(db: Session, mois, annee_academique_field, etudiant_id):
    """
    Traite et enregistre le statut de paiement d'un étudiant.
    
    Args:
        db: Session SQLAlchemy
        data: Données du paiement (doit avoir etudiant_id, annee_id, mois)
        annee_academique_field: Optionnel, si le champ s'appelle autrement
    
    Returns:
        PaiementStatut mis à jour ou créé
    """
    
    # 1. Récupère l'année académique
    # annee_value = getattr(data, annee_academique_field or "annee_id")
    annee = db.query(AnneeAcademique).filter(
        AnneeAcademique.annee_academique == annee_academique_field
    ).first()

    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")

    # 2. Récupère tous les mois de l'année
    tous_les_mois = get_mois_entre(annee.date_debut, annee.date_fin)

    # 3. Analyse les versements acquittés
    versements_acquittes = set()
    for key in mois.keys():
        numero = int(key.split("_")[1])
        suffix = "er" if numero == 1 else "ème"
        label = f"{numero}{suffix} Versement"
        versements_acquittes.add(label)

    # 4. Calcule les mois accessibles selon les versements
    versement_mois = {
        "1er Versement": 3,
        "2ème Versement": 3,
        "3ème Versement": 2,
        "4ème Versement": 2,
    }

    total_mois_accessibles = sum(
        nb_mois
        for versement, nb_mois in versement_mois.items()
        if versement in versements_acquittes
    )

    mois_accessibles = tous_les_mois[:total_mois_accessibles]
    mois_bloques = tous_les_mois[total_mois_accessibles:]

    # 5. Enregistre ou met à jour dans PaiementStatut
    statut = db.query(PaiementStatut).filter(
        PaiementStatut.etudiant_id == etudiant_id,
        PaiementStatut.annee_id == annee.id
    ).first()

    if statut:
        anciens_mois = statut.mois_accessibles or []
        statut.mois_accessibles = list(dict.fromkeys(anciens_mois + mois_accessibles))
        statut.mois_bloques = [m for m in tous_les_mois if m not in statut.mois_accessibles]
        statut.updated_at = datetime.utcnow()
    else:
        statut = PaiementStatut(
            etudiant_id=etudiant_id,
            annee_id=annee.id,
            mois_accessibles=mois_accessibles,
            mois_bloques=mois_bloques,
        )
        db.add(statut)

    db.commit()
    db.refresh(statut)
    
    # return statut

MOIS_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}

def get_mois_entre(date_debut: date, date_fin: date) -> list:
    """Retourne la liste des mois en français entre deux dates"""
    mois = []
    current = date_debut.replace(day=1)
    fin = date_fin.replace(day=1)
    while current <= fin:
        mois.append(MOIS_FR[current.month])
        current += relativedelta(months=1)
    return mois


class PaiementStatutRequest(BaseModel):
    etudiant_id: str
    annee_id: str
    mois: dict


@router_paie.post("/paiement-statut")
def enregistrer_paiement_statut(
    data: PaiementStatutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1. Récupère l'année académique
    annee = db.query(AnneeAcademique).filter(
        AnneeAcademique.annee_academique == data.annee_id
    ).first()

    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")

    # 2. Récupère tous les mois de l'année
    tous_les_mois = get_mois_entre(annee.date_debut, annee.date_fin)

    # 3. Analyse les versements acquittés
    # check_echeance = data.paiement_details.get("check_echeance", {})
    # info_paiement = data.paiement_details.get("info_paiement", {})

    versements_acquittes = set()
    for key in data.mois.keys():
        numero = int(key.split("_")[1])
        suffix = "er" if numero == 1 else "ème"
        label = f"{numero}{suffix} Versement"
        versements_acquittes.add(label)

    print(f"👉 Versements acquittés: {versements_acquittes}")

    # 4. Calcule les mois accessibles selon les versements
    # 1er versement → 3 mois, 2ème versement → 3 mois, 3ème → 2 mois, 4ème → 2 mois
    versement_mois = {
        "1er Versement": 3,
        "2ème Versement": 3,
        "3ème Versement": 2,
        "4ème Versement": 2,
    }

    total_mois_accessibles = 0
    for versement, nb_mois in versement_mois.items():
        if versement in versements_acquittes:
            total_mois_accessibles += nb_mois

    mois_accessibles = tous_les_mois[:total_mois_accessibles]
    mois_bloques = tous_les_mois[total_mois_accessibles:]


    # 5. Enregistre ou met à jour dans PaiementStatut
    statut = db.query(PaiementStatut).filter(
        PaiementStatut.etudiant_id == data.etudiant_id,
        PaiementStatut.annee_id == annee.id
    ).first()

    if statut:
        anciens_mois = statut.mois_accessibles or []
        statut.mois_accessibles = list(dict.fromkeys(anciens_mois + mois_accessibles))
        
        # Mois bloqués = tous les mois SAUF les accessibles
        statut.mois_bloques = [m for m in tous_les_mois if m not in statut.mois_accessibles]
        statut.updated_at = datetime.utcnow()
    else:
        statut = PaiementStatut(
            etudiant_id=data.etudiant_id,
            annee_id=annee.id,
            mois_accessibles=mois_accessibles,
            mois_bloques=mois_bloques,
        )
        db.add(statut)

    db.commit()
    db.refresh(statut)

    return {
        "success": "Statut de paiement enregistré",
        "mois_accessibles": mois_accessibles,
        "mois_bloques": mois_bloques,
        "versements_acquittes": list(versements_acquittes)
    }

class GetPaiementStatut(BaseModel):
    etudiant_id: str
    annee_academique: str

@router_paie.post("/get-paiement-statut")
def get_paiement_statut(
    data:GetPaiementStatut,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if len(data.annee_academique) >= 36:
        annee = db.query(AnneeAcademique).filter(
            AnneeAcademique.id == data.annee_academique
        ).first()
    else:
        annee = db.query(AnneeAcademique).filter(
            AnneeAcademique.annee_academique == data.annee_academique
        ).first()

    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")

    statut = db.query(PaiementStatut).filter(
        PaiementStatut.etudiant_id == data.etudiant_id,
        PaiementStatut.annee_id == annee.id
    ).first()

    if not statut:
        raise HTTPException(status_code=404, detail="Aucun statut de paiement trouvé")

    return {
        "etudiant_id": statut.etudiant_id,
        "annee_id": statut.annee_id,
        "mois_accessibles": statut.mois_accessibles,
        "mois_bloques": statut.mois_bloques,
        "created_at": statut.created_at,
        "updated_at": statut.updated_at,
    }