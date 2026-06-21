# ============================================================================
# CORRECTION POUR GÉRER data_month_field
# ============================================================================

# Fonction utilitaire pour normaliser data_month_field
def normalize_month_field(data_month_field):
    """
    Convertit data_month_field en dictionnaire avec clé 'mois'
    Gère les cas où c'est une liste, un dict, ou une chaîne JSON
    """
    # Cas 1: C'est None ou vide
    if not data_month_field:
        return {'mois': {}}
    
    # Cas 2: C'est une chaîne JSON
    if isinstance(data_month_field, str):
        try:
            data_month_field = json.loads(data_month_field)
        except json.JSONDecodeError:
            logger.warning(f"Impossible de parser data_month_field: {data_month_field}")
            return {'mois': {}}
    
    # Cas 3: C'est une liste (ancien format)
    if isinstance(data_month_field, list):
        logger.info("data_month_field est une liste, conversion en dict")
        return {'mois': {}}
    
    # Cas 4: C'est déjà un dictionnaire
    if isinstance(data_month_field, dict):
        # Vérifier si la clé 'mois' existe
        if 'mois' not in data_month_field:
            logger.warning("Clé 'mois' manquante dans data_month_field")
            return {'mois': data_month_field}  # Considérer tout comme 'mois'
        return data_month_field
    
    # Cas par défaut
    logger.warning(f"Type inattendu pour data_month_field: {type(data_month_field)}")
    return {'mois': {}}


# ============================================================================
# UTILISATION DANS VOTRE CODE
# ============================================================================

# Avant (qui causait l'erreur):
data_month_field = json.loads(data.mois) if isinstance(data.mois, str) else data.mois
new_data_for_month = {**data_month_field.get('mois', {}), **request_mois}  # ❌ ERREUR ICI

# Après (corrigé):
data_month_field_raw = json.loads(data.mois) if isinstance(data.mois, str) else data.mois
data_month_field = normalize_month_field(data_month_field_raw)
new_data_for_month = {**data_month_field.get('mois', {}), **request_mois}  # ✅ OK


# ============================================================================
# VERSION INLINE (sans fonction utilitaire)
# ============================================================================

# Parser les données
data_month_field_raw = json.loads(data.mois) if isinstance(data.mois, str) else data.mois

# Normaliser selon le type
if isinstance(data_month_field_raw, list):
    # Si c'est une liste, créer un nouveau dict
    data_month_field = {'mois': {}}
    logger.warning("data_month_field était une liste, convertie en dict vide")
elif isinstance(data_month_field_raw, dict):
    # Si c'est un dict, vérifier la structure
    if 'mois' in data_month_field_raw:
        data_month_field = data_month_field_raw
    else:
        # Considérer tout le dict comme 'mois'
        data_month_field = {'mois': data_month_field_raw}
else:
    # Cas par défaut
    data_month_field = {'mois': {}}
    logger.warning(f"Type inattendu pour data_month_field: {type(data_month_field_raw)}")

# Maintenant on peut fusionner en toute sécurité
new_data_for_month = {**data_month_field.get('mois', {}), **request_mois}


# ============================================================================
# VERSION COMPACTE AVEC GESTION D'ERREUR
# ============================================================================

try:
    data_month_field_raw = json.loads(data.mois) if isinstance(data.mois, str) else data.mois
    
    # Convertir en dict avec clé 'mois' si nécessaire
    if isinstance(data_month_field_raw, list):
        data_month_field = {'mois': {}}
    elif isinstance(data_month_field_raw, dict) and 'mois' not in data_month_field_raw:
        data_month_field = {'mois': data_month_field_raw}
    else:
        data_month_field = data_month_field_raw if isinstance(data_month_field_raw, dict) else {'mois': {}}
    
    # Fusionner
    new_data_for_month = {**data_month_field.get('mois', {}), **request_mois}
    
except Exception as e:
    logger.error(f"Erreur lors du traitement de data_month_field: {str(e)}")
    data_month_field = {'mois': {}}
    new_data_for_month = request_mois


# ============================================================================
# VERSION AVEC DEFAULTDICT (plus élégante)
# ============================================================================

from collections import defaultdict

def safe_merge_months(data_mois, request_mois):
    """
    Fusionne les mois de manière sécurisée
    """
    try:
        # Parser si nécessaire
        if isinstance(data_mois, str):
            data_month_field = json.loads(data_mois)
        else:
            data_month_field = data_mois
        
        # Extraire le dict 'mois'
        if isinstance(data_month_field, dict) and 'mois' in data_month_field:
            existing_mois = data_month_field['mois']
        elif isinstance(data_month_field, dict):
            existing_mois = data_month_field
        else:
            existing_mois = {}
        
        # Fusionner
        return {**existing_mois, **request_mois}
    
    except Exception as e:
        logger.error(f"Erreur fusion mois: {str(e)}")
        return request_mois

# Utilisation:
new_data_for_month = safe_merge_months(data.mois, request_mois)


# ============================================================================
# EXEMPLE COMPLET DANS VOTRE CONTEXTE
# ============================================================================

@router.post("/payment-save-info", response_model=PaymentSaveInfoResponse)
async def payment_save_info(
    request: PaymentSaveInfoRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # ... votre code existant ...
        
        if data:
            # Parser les données existantes
            data_payment = json.loads(data.paiement_details) if isinstance(data.paiement_details, str) else data.paiement_details
            
            # ✅ CORRECTION ICI - Parser et normaliser data_month_field
            try:
                data_month_field_raw = json.loads(data.mois) if isinstance(data.mois, str) else data.mois
                
                # Gérer les différents types
                if isinstance(data_month_field_raw, list):
                    logger.warning(f"data_month_field est une liste: {data_month_field_raw}")
                    data_month_field = {'mois': {}}
                elif isinstance(data_month_field_raw, dict):
                    if 'mois' in data_month_field_raw:
                        data_month_field = data_month_field_raw
                    else:
                        logger.warning("Clé 'mois' manquante, utilisation du dict complet")
                        data_month_field = {'mois': data_month_field_raw}
                else:
                    logger.warning(f"Type inattendu: {type(data_month_field_raw)}")
                    data_month_field = {'mois': {}}
            
            except Exception as e:
                logger.error(f"Erreur parsing data_month_field: {str(e)}")
                data_month_field = {'mois': {}}
            
            # Maintenant on peut fusionner en toute sécurité
            new_data_for_month = {**data_month_field.get('mois', {}), **request_mois}
            
            # ... reste de votre code ...
            
            # Sauvegarder
            data.mois = json.dumps({'mois': new_data_for_month})
            db.commit()
        
        # ... reste de votre code ...
    
    except Exception as e:
        logger.error(f"Erreur dans payment_save_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


# ============================================================================
# DEBUG: AFFICHER LES TYPES ET VALEURS
# ============================================================================

# Pour déboguer, ajoutez ceci temporairement:
print(f"\n{'='*60}")
print(f"DEBUG data_month_field:")
print(f"Type: {type(data_month_field_raw)}")
print(f"Valeur: {data_month_field_raw}")
print(f"{'='*60}\n")

if isinstance(data_month_field_raw, list):
    print("⚠️  C'est une liste!")
    print(f"Contenu: {data_month_field_raw}")
elif isinstance(data_month_field_raw, dict):
    print("✅ C'est un dictionnaire")
    print(f"Clés: {data_month_field_raw.keys()}")
    print(f"'mois' présent: {'mois' in data_month_field_raw}")

























    from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from collections import OrderedDict
import json
import logging
import uuid as uuid_lib
import re

logger = logging.getLogger(__name__)

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class PaiementDetailsInput(BaseModel):
    """Détails du paiement en entrée"""
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
    """Requête pour sauvegarder un paiement"""
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
    paiement_details: PaiementDetailsInput
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
        # alpha_dash: lettres, chiffres, tirets et underscores
        if not all(c.isalnum() or c in ['-', '_'] for c in v):
            raise ValueError("L'identifiant doit contenir uniquement des lettres, chiffres, tirets et underscores")
        return v
    
    @model_validator(mode='after')
    def validate_depot_required(self):
        if not self.must_refresh_paiement and self.paiement_details.depot is None:
            raise ValueError("Vous devez ajouter le montant")
        return self

class PaymentSaveInfoResponse(BaseModel):
    """Réponse après sauvegarde du paiement"""
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

def normalize_month_field(data_month_field: Any) -> Dict[str, Dict]:
    """Normalise data_month_field pour gérer liste, dict ou string"""
    if not data_month_field:
        return {'mois': {}}
    
    if isinstance(data_month_field, str):
        try:
            data_month_field = json.loads(data_month_field)
        except json.JSONDecodeError:
            logger.warning(f"Impossible de parser data_month_field: {data_month_field}")
            return {'mois': {}}
    
    if isinstance(data_month_field, list):
        logger.info("data_month_field est une liste, conversion en dict")
        return {'mois': {}}
    
    if isinstance(data_month_field, dict):
        if 'mois' not in data_month_field:
            logger.warning("Clé 'mois' manquante dans data_month_field")
            return {'mois': data_month_field}
        return data_month_field
    
    logger.warning(f"Type inattendu pour data_month_field: {type(data_month_field)}")
    return {'mois': {}}

def set_perso_action(action: str):
    """Enregistre l'action personnalisée"""
    # Implémentez votre logique d'enregistrement d'action
    pass

def authorize_with_admin_token(user, permission: str, db: Session):
    """Vérifie les autorisations"""
    # Implémentez votre logique d'autorisation
    pass

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter()

@router.post("/payment-save-info", response_model=PaymentSaveInfoResponse)
async def payment_save_info(
    request: PaymentSaveInfoRequest,
    user = Depends(get_current_user),
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
    
    try:
        # Autorisation
        authorize_with_admin_token(user, "Ajouter paiement", db)
        
        # Générer la date et UUID
        date_with_hours = datetime.now().strftime('%d-%m-%Y %H:%M')
        last_paiement_key = str(uuid_lib.uuid4())
        current_date = datetime.now().date()
        
        # Récupérer l'année académique ID
        annee_id = db.query(AnneeAcademique.id).filter(
            AnneeAcademique.annee_academique == request.annee_academique
        ).scalar()
        
        if not annee_id:
            raise HTTPException(
                status_code=422,
                detail={"errors": "Année académique introuvable"}
            )
        
        # Vérifier si un paiement existe déjà
        data = db.query(Paiement).filter(
            Paiement.niveau_id == request.niveau_id,
            Paiement.etudiant_id == request.etudiant_id,
            Paiement.annee_academique == request.annee_academique
        ).first()
        
        # Vérifier les paiements antérieurs
        data_to_check = db.query(ClassesEtudiant).outerjoin(
            Paiement, ClassesEtudiant.etudiant_id == Paiement.etudiant_id
        ).filter(
            ClassesEtudiant.etudiant_id == request.etudiant_id,
            ClassesEtudiant.annee_academique_id != annee_id
        ).all()
        
        # Récupérer les paramètres de paiement
        data_pay = db.query(ParametrePaiement).filter(
            ParametrePaiement.niveau_id == request.niveau_id,
            ParametrePaiement.classe == request.classe,
            ParametrePaiement.anneeAcademique == annee_id
        ).first()
        
        if not data_pay:
            raise HTTPException(
                status_code=422,
                detail={"errors": "Paramètres de paiement non configurés"}
            )
        
        # Parser les versements
        montant_par_data = json.loads(data_pay.montant_par) if isinstance(data_pay.montant_par, str) else data_pay.montant_par
        versements = montant_par_data.get(data_pay.echeance, {})
        
        # Récupérer le type de bourse
        type_bourse = db.query(Etudiant.aide_financiere).filter(
            Etudiant.id == request.etudiant_id
        ).scalar() or 'Aucune'
        
        # Trier les versements par numéro
        def extract_number(key):
            match = re.search(r'_(\d+)_', key)
            return int(match.group(1)) if match else 0
        
        versements_sorted = OrderedDict(sorted(versements.items(), key=lambda x: extract_number(x[0])))
        
        # Calculer le montant à payer selon le type de bourse
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
            'identifiant': request.identifiant,
            'classe': request.classe,
            'echeance': request.echeance,
            'prenom': request.prenom,
            'nom': request.nom,
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
        
        # ============================================================
        # MISE À JOUR D'UN PAIEMENT EXISTANT
        # ============================================================
        
        if data:
            details = request.paiement_details.dict(exclude_none=True)
            
            # Parser les données existantes
            data_payment = json.loads(data.paiement_details) if isinstance(data.paiement_details, str) else data.paiement_details
            
            # Normaliser data_month_field
            data_month_field_raw = json.loads(data.mois) if isinstance(data.mois, str) else data.mois
            data_month_field = normalize_month_field(data_month_field_raw)
            
            # Récupérer le dernier type de bourse
            details_etudiant = data_payment.get('paiement_details', {}).get('details_etudiant', {})
            if isinstance(details_etudiant, str):
                details_etudiant = json.loads(details_etudiant)
            elif isinstance(details_etudiant, list) and details_etudiant:
                details_etudiant = details_etudiant[-1]
                if isinstance(details_etudiant, str):
                    details_etudiant = json.loads(details_etudiant)
            
            last_bourse_type_value = details_etudiant.get('aide_financiere', type_bourse) if isinstance(details_etudiant, dict) else type_bourse
            
            # Gestion de la modification de paiement
            if request.index_paiement and last_bourse_type_value == type_bourse:
                authorize_with_admin_token(user, "Modifier paiement", db)
                set_perso_action("update")
                
                paiement_details_dict['edit_by_id'] = user.id
                paiement_details_dict['edit_by'] = user.name
                paiement_details_dict['return_by_id'] = ''
                paiement_details_dict['return_by'] = ''
                
                # Note: supprimerDernierPaiement non implémenté ici pour simplifier
                # Vous devrez l'implémenter si nécessaire
            else:
                set_perso_action("create")
            
            # Parser les accessoires
            accessoires = json.loads(data_pay.accessoires) if isinstance(data_pay.accessoires, str) else data_pay.accessoires or []
            
            # Récupérer le dernier paiement non retourné
            info_paiement = data_payment.get('paiement_details', {}).get('info_paiement', {})
            last_info = None
            
            for date_key in reversed(list(info_paiement.keys())):
                entry = info_paiement[date_key]
                if entry.get('status', '') != 'retourné':
                    last_info = entry
                    break
            
            if last_info and isinstance(last_info, dict):
                new_payment = last_info.get('depot_et_avance', 0)
                total_verse = last_info.get('total_verse', 0)
            else:
                logger.warning("info_paiement vide ou invalide")
                new_payment = 0
                total_verse = 0
            
            paiement_details_dict['avance'] = f"{int(details.get('depot', 0))} + {int(new_payment)}"
            
            remaining_depot = int(details.get('depot', 0)) + int(new_payment)
            acquitte_paie = int(details.get('depot', 0)) + int(new_payment)
            
            # Traitement des accessoires
            total_accessoires = 0
            
            accessoires_list = data_payment.get('paiement_details', {}).get('accessoires', [])
            if isinstance(accessoires_list, list) and accessoires_list:
                end_accessoir = accessoires_list[-1]
            elif isinstance(accessoires_list, dict):
                end_accessoir = accessoires_list
            else:
                end_accessoir = {}
            
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
                        detail={"paiement_details.depot": "Le montant est insuffisant pour les accessoires choisis"}
                    )
            
            # Calculer les versements
            status = transform_payments(data_pay.montant_par, type_bourse)
            paiement_details_dict['total_verse'] = int(total_verse) + int(details.get('depot', 0))
            
            # Traitement normal des versements
            for key, value in versements_sorted.items():
                if key not in data_month_field.get('mois', {}):
                    value_ = int(value)
                    versement_parts = key.split('_')
                    get_versement_place = versement_parts[1]
                    
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
                        
                        versement_num = versement_parts[1]
                        versement_type = versement_parts[0]
                        suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                        
                        paiement_details_dict['status_paiement'].append(f"Acqt: {suffix} {versement_type}")
                        remaining_depot -= global_calcul
                    else:
                        paiement_details_dict['depot_et_avance'] = remaining_depot
                        paiement_details_dict['balance'] = abs(global_calcul - remaining_depot)
                        
                        if remaining_depot > 0:
                            versement_num = versement_parts[1]
                            versement_type = versement_parts[0]
                            suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                            paiement_details_dict['status_paiement'].append(f"Avns: {suffix} {versement_type}")
                        break
            
            # Mise à jour check_echeance
            if 'check_echeance' not in data_payment.get('paiement_details', {}):
                data_payment['paiement_details']['check_echeance'] = check_echeance
            
            new_data_for_month = {**data_month_field.get('mois', {}), **request_mois}
            
            # Récupérer les infos
            classe = db.query(Classe.nom_classe).filter(Classe.id == request.classe).scalar()
            niveau = db.query(Niveau.name).filter(Niveau.id == request.niveau_id).scalar()
            faculte = db.query(Faculte.nom).filter(Faculte.id == request.faculte_id).scalar() if request.faculte_id else None
            
            # Mettre à jour les données
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
            date_key = request.index_paiement if request.index_paiement else date_with_hours
            data_payment['paiement_details']['info_paiement'][date_key] = {
                **paiement_details_dict,
                **request_mois
            }
            
            # Sauvegarder
            data.paiement_details = json.dumps(data_payment)
            data.mois = json.dumps({'mois': new_data_for_month})
            data.last_paiement_key = last_paiement_key
            db.commit()
            db.refresh(data)
            payment = data
        
        # ============================================================
        # NOUVEAU PAIEMENT
        # ============================================================
        
        else:
            set_perso_action("create")
            
            accessoires = json.loads(data_pay.accessoires) if isinstance(data_pay.accessoires, str) else data_pay.accessoires or []
            details = request.paiement_details.dict(exclude_none=True)
            
            paiement_details_dict['devise'] = data_pay.devise
            status = transform_payments(data_pay.montant_par, type_bourse)
            
            remaining_depot = int(details.get('depot', 0))
            acquitt_p = int(details.get('depot', 0))
            
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
                        detail={"paiement_details.depot": "Le montant est insuffisant pour les accessoires choisis"}
                    )
            
            paiement_details_dict['total_verse'] = remaining_depot
            
            # Calculer les versements
            for key, value in versements_sorted.items():
                value_ = int(value)
                versement_parts = key.split('_')
                get_versement_place = versement_parts[1]
                
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
                    
                    versement_num = versement_parts[1]
                    versement_type = versement_parts[0]
                    suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                    
                    paiement_details_dict['status_paiement'].append(f"Acqt: {suffix} {versement_type}")
                    remaining_depot -= global_calcul
                else:
                    paiement_details_dict['depot_et_avance'] = remaining_depot
                    paiement_details_dict['balance'] = abs(global_calcul - remaining_depot)
                    
                    if remaining_depot > 0:
                        versement_num = versement_parts[1]
                        versement_type = versement_parts[0]
                        suffix = '1er' if versement_num == '1' else f"{versement_num}ème"
                        paiement_details_dict['status_paiement'].append(f"Avns: {suffix} {versement_type}")
                    break
            
            # Vérifier si acquitté
            if int(acquitt_p) >= int(montant_to_pay):
                paiement_details_dict['status'] = 'Acquitté'
            
            # Préparer les mois
            validated_data['mois'] = json.dumps({'mois': request_mois})
            
            # Récupérer les infos
            classe_list = db.query(Classe.nom_classe).filter(Classe.id == request.classe).all()
            classe = classe_list[0] if classe_list else None
            niveau = db.query(Niveau.name).filter(Niveau.id == request.niveau_id).scalar()
            faculte = db.query(Faculte.nom).filter(Faculte.id == request.faculte_id).scalar() if request.faculte_id else None
            
            # Construire paiement_details final
            validated_data['paiement_details'] = json.dumps({
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
            })
            
            # Créer le paiement
            payment = Paiement(**validated_data)
            db.add(payment)
            db.commit()
            db.refresh(payment)
        
        # Calculer l'index
        payment_data = json.loads(payment.paiement_details) if isinstance(payment.paiement_details, str) else payment.paiement_details
        ind = len(payment_data.get('paiement_details', {}).get('info_paiement', {})) - 1
        
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