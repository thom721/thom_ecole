from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import  StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, or_, func
from typing import Optional, List, Dict, Any
from decimal import Decimal
from fractions import Fraction
from pydantic import BaseModel, Field, field_validator,model_validator
from app.Models.MFinancials import Paiement,Loan,LoanRepayment,OrderItem,Vente,Depense,FraisInscription,OtherTransaction,AnnulationArriere
from app.Models.MModels import Niveau,Etudiant,User,AnneeAcademique
from app.Models.MSystems import Profile
from app.Models.MRelations import ClasseEtudiant
from app.database import get_db
from datetime import datetime, date, time
from enum import Enum
import json
import logging
from app.Helper.pdf_personaliser import PDFGenerator
from app.dependencies.Dependencie import check_permission

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS
# ============================================================================

class ReportType(str, Enum):
    GLOBAL = "Global"
    LIVRES = "Livres"
    TISSUS = "Tissus"
    FOURNITURES = "Fournitures"
    ARRIERE = "Arriéré"

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class PrintGlobalReportRequest(BaseModel):
    """Requête pour le rapport global"""
    date_debut: date = Field(..., description="Date de début")
    date_fin: date = Field(..., description="Date de fin")
    type: ReportType = Field(..., description="Type de rapport")
    
    @field_validator('date_debut', 'date_fin')
    @classmethod
    def validate_dates(cls, v):
        if not v:
            raise ValueError("La date est requise")
        return v
    
    @model_validator(mode='after')
    def validate_date_range(self):
        if self.date_debut > self.date_fin:
            raise ValueError("La date de début doit être avant ou égale à la date de fin")
        return self

class PaymentReportItem(BaseModel):
    """Item de paiement dans le rapport"""
    date_paiement: str
    identifiant: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    depot: Optional[float] = None
    total_verse: Optional[float] = None
    status_paiements: Optional[List[str]] = []
    status_avance: Optional[str] = ""
    
    class Config:
        from_attributes = True

class InscriptionStats(BaseModel):
    """Statistiques d'inscription par niveau"""
    total_inscrit: int
    frais_total: float

class SalesItem(BaseModel):
    """Item de vente"""
    qt_item: int
    order_total: float
    prix_item: float
    vente_name: str
    fname: str
    prenom: str

class SalesCategory(BaseModel):
    """Catégorie de ventes"""
    category: str
    quantite: float
    total: float
    items: List[Dict[str, Any]]

class DepenseItem(BaseModel):
    """Item de dépense"""
    description: str
    prix: float
    
    class Config:
        from_attributes = True

class LoanItem(BaseModel):
    """Item de prêt"""
    id: str
    amount: float
    remaining_balance: float
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class RepaymentItem(BaseModel):
    """Item de remboursement"""
    loan_user_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class GlobalReportResponse(BaseModel):
    """Réponse du rapport global"""
    payments: List[Dict[str, Any]]
    inscription: Dict[str, InscriptionStats]
    sales: Dict[str, SalesCategory]
    getNivel: List[Dict[str, Any]]
    depenses: List[DepenseItem]
    date1: str
    date2: str
    info: Optional[Dict[str, Any]]
    type: str
    loans: List[LoanItem]
    repayment: List[Dict[str, Any]]

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def transform_payments(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforme les paiements pour extraire les statuts"""
    datas = data if isinstance(data, dict) else json.loads(data) if isinstance(data, str) else {}
    status = {'status_paiements': []}
    
    if not isinstance(datas, dict) or not datas:
        return status
    
    for payment_key, value in datas.items():
        parts = payment_key.split('_')
        
        if len(parts) < 3:
            continue
        
        type_ = parts[0]
        
        try:
            versement_number = int(parts[1])
        except (ValueError, IndexError):
            continue
        
        if payment_key.startswith('Versement_') and versement_number in [1, 2, 3, 4]:
            suffix = 'er' if versement_number == 1 else 'ème'
            status['status_paiements'].append(f"{versement_number}{suffix} {type_}")
    
    return status

def get_last_payment(data: Dict[str, Any], current_date: str) -> Dict[str, str]:
    """Récupère le dernier paiement avec versement"""
    last_with_versement = None
    status = {'status_avance': ''}
    
    # Parcours à l'envers
    for date_key, info in reversed(list(data.items())):
        for key, value in info.items():
            if key.startswith('Versement_'):
                last_with_versement = {date_key: info}
                break
        if last_with_versement:
            break
    
    if last_with_versement:
        for date_key, payments in last_with_versement.items():
            for payment_key, value in payments.items():
                if payment_key.startswith('Versement_'):
                    parts = payment_key.split('_')
                    
                    if len(parts) < 2:
                        continue
                    
                    type_ = parts[0]
                    
                    try:
                        versement_number = int(parts[1]) + 1
                    except (ValueError, IndexError):
                        continue
                    
                    if versement_number in [1, 2, 3, 4]:
                        suffix = 'er' if versement_number == 1 else 'ème'
                        status['status_avance'] = f"{versement_number}{suffix} {type_}"
    
    return status

def extraire_donnees_par_intervalle_for_day(
    json_data: List[Dict],
    date_debut: datetime,
    date_fin: datetime
) -> List[Dict[str, Any]]:
    """Extrait les données de paiement pour l'intervalle donné"""
    resultat = []
    count = 0
    
    for value in json_data:
        paiements = value.get('paiement_details', {})
        data_student = paiements.get('details_etudiant', {})
        
        info_paiement = paiements.get('info_paiement', {})
        
        for date_str, donnees in info_paiement.items():
            try:
                # Parser la date au format 'd-m-Y H:i'
                date_cle = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
                
                # Vérifier si la date est dans l'intervalle
                if date_debut <= date_cle <= date_fin:
                    count += 1
                    
                    status = transform_payments(donnees)
                    avance_status = get_last_payment(info_paiement, date_str)
                    
                    # Fusionner toutes les données
                    result_item = {
                        **donnees,
                        **data_student,
                        **status,
                        **avance_status,
                        'date_paiement': date_cle.strftime('%Y-%m-%d %H:%M')
                    }
                    
                    resultat.append(result_item)
            
            except ValueError as e:
                logger.warning(f"Erreur parsing date {date_str}: {str(e)}")
                continue
    
    return resultat

def split_arrears_payments(
    rapport_personalise: List[Dict[str, Any]],
    db: Session
) -> tuple[List[Dict[str, Any]], SalesCategory]:
    """Sépare, parmi les paiements déjà extraits pour la période, ceux qui
    règlent une année académique différente de l'année active — un
    étudiant qui verse un montant pendant la période du rapport mais pour
    une année académique antérieure (arriéré), plutôt que pour l'année en
    cours. Chaque entrée de rapport_personalise porte déjà
    `annee_academique` (fusionné depuis paiement_details.details_etudiant).

    Retourne (paiements de l'année en cours uniquement, catégorie Arriéré)
    — les paiements en arriéré sont retirés de la liste principale pour
    éviter qu'ils soient comptés deux fois (une fois dans le total des
    paiements de l'année, une fois dans la section Arriéré).
    """
    annee_active = db.query(AnneeAcademique).filter(AnneeAcademique.status == 1).first()
    annee_active_nom = annee_active.annee_academique if annee_active else None

    if not annee_active_nom:
        return rapport_personalise, SalesCategory(category='Arriéré', quantite=0, total=0, items=[])

    current_year_payments = []
    arrears_items = []
    arrears_total = Decimal("0.0")

    for item in rapport_personalise:
        # Un versement retourné (Returns.py) reste dans info_paiement avec
        # status="retourné" plutôt que d'être supprimé — jamais compté dans
        # le total principal (voir global_report.html, is_returned), donc
        # pas non plus dans la section Arriéré.
        if item.get('status') == 'retourné':
            current_year_payments.append(item)
            continue

        annee_paiement = item.get('annee_academique')
        if annee_paiement and annee_paiement != annee_active_nom:
            montant = Decimal(str(item.get('depot') or 0))
            arrears_total += montant
            arrears_items.append({
                'qt_item': 1,
                'order_total': float(montant),
                'prix_item': float(montant),
                'vente_name': f"Solde {annee_paiement}",
                'fname': item.get('nom', ''),
                'prenom': item.get('prenom', ''),
            })
        else:
            current_year_payments.append(item)

    arrears_category = SalesCategory(
        category='Arriéré',
        quantite=len(arrears_items),
        total=float(arrears_total),
        items=arrears_items,
    )
    return current_year_payments, arrears_category

def get_register_for_period(
    niveaux: List,
    date_debut: datetime,
    date_fin: datetime,
    db: Session
) -> Dict[str, InscriptionStats]:
    """Récupère les statistiques d'inscription pour la période"""
    register = {}
    
    for niveau in niveaux:
        # Récupérer les inscriptions
        inscriptions = db.query(ClasseEtudiant).filter(
            ClasseEtudiant.niveau_id == niveau.id,
            ClasseEtudiant.created_at.between(date_debut, date_fin),
            ClasseEtudiant.user_id.isnot(None)
        ).all()
        
        total_inscrits = len(inscriptions)
        
        # Récupérer les IDs de niveau uniques
        niveau_ids = list(set([insc.niveau_id for insc in inscriptions]))
        
        # Récupérer les frais d'inscription
        frais = db.query(FraisInscription).filter(
            FraisInscription.niveau_id.in_(niveau_ids)
        ).all()
        
        frais_dict = {f.niveau_id: f.prix for f in frais}
        
        # Calculer le total des frais
        total_fee = sum(frais_dict.get(insc.niveau_id, 0) for insc in inscriptions)
        
        register[niveau.name] = InscriptionStats(
            total_inscrit=total_inscrits,
            frais_total=total_fee
        )
    
    return register

def _format_quantite_fraction(quantite: float) -> str:
    """Affiche une quantité fractionnaire (Tissus vendus au tiers/quart/demi
    "Aune", voir OrderItem.quantite — colonne texte en base, convertie en
    float dans get_sales_for_inter) sous forme de fraction lisible plutôt que
    de décimal brut : "1/2" pas "0.5", "1 1/2" pas "1.5". Dénominateur limité
    à 16 (couvre demis/quarts/huitièmes, largement suffisant pour du tissu au
    mètre) pour éviter une fraction absurde sur une valeur qui n'en est pas
    vraiment une (ex. un import erroné à 0.333333).
    """
    frac = Fraction(quantite).limit_denominator(16)
    whole, remainder = divmod(frac.numerator, frac.denominator)
    if remainder == 0:
        return str(whole)
    if whole == 0:
        return f"{remainder}/{frac.denominator}"
    return f"{whole} {remainder}/{frac.denominator}"


def get_sales_for_inter(
    date_debut: datetime,
    date_fin: datetime,
    db: Session
) -> Dict[str, SalesCategory]:
    """Récupère les ventes pour l'intervalle"""
    resultat = {}
    # 'Arriéré' n'est normalement pas une catégorie de produit vendu, mais
    # certains rapports existants ont pu enregistrer des arriérés comme
    # OrderItem (ancien flux, via Vente) avant l'ajout de
    # split_arrears_payments() (qui les tire de Paiement). On garde donc
    # cette catégorie ici pour ne rien perdre, et print_global_report()
    # fusionne les deux sources.
    categories = ['Livres', 'Tissus', 'Fournitures', 'Arriéré']
    
    for category in categories:
        # Query pour les ventes
        total_vente = db.query(
            OrderItem.quantite.label('qt_item'),
            OrderItem.total.label('order_total'),
            OrderItem.prix.label('prix_item'),
            OrderItem.nom.label('vente_name'),
            Vente,
            Etudiant.nom.label('fname'),
            Etudiant.prenom
        ).join(
            Vente, OrderItem.vente_id == Vente.id
        ).join(
            Etudiant, Vente.etudiant_id == Etudiant.id
        ).filter(
            OrderItem.category == category,
            OrderItem.status == '1',
            OrderItem.created_at.between(date_debut, date_fin)
        ).all()
        
        # Convertir en liste de dicts
        items = []
        quantite_total = 0
        montant_total = 0
        
        for item in total_vente:
            item_qt = float(item.qt_item) or 0
            quantite_total += item_qt
            montant_total += item.order_total or 0

            # Tissus vendus au "Aune" (quantité souvent fractionnaire, voir
            # _format_quantite_fraction) : la quantité est préfixée au nom
            # dans la colonne Description du rapport ("1/2 Aune Beige"),
            # sinon un seul article vendu 3 fois à 1/2 Aune apparaîtrait
            # comme 3 lignes identiques "Aune Beige" sans indiquer combien.
            vente_name = item.vente_name
            if category == 'Tissus':
                vente_name = f"{_format_quantite_fraction(item_qt)} {vente_name}"

            items.append({
                'qt_item': item.qt_item,
                'order_total': item.order_total,
                'prix_item': item.prix_item,
                'vente_name': vente_name,
                'fname': item.fname,
                'prenom': item.prenom
            })
        
        resultat[category] = SalesCategory(
            category=category,
            quantite=quantite_total,
            total=montant_total,
            items=items
        )
    
    return resultat

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()

@router.post("/print-global-repport", response_model=GlobalReportResponse)
def print_global_report(
    request: PrintGlobalReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Imprimer rapport")),
):
    """
    Génère un rapport global pour une période donnée
    
    Types de rapports disponibles:
    - Global: Tous les types
    - Livres: Ventes de livres uniquement
    - Tissus: Ventes de tissus uniquement
    - Fournitures: Ventes de fournitures uniquement
    - Arriéré: Arriérés uniquement
    """
    
    try:
        # Créer les datetime de début et fin de journée
        date_debut = datetime.combine(request.date_debut, time.min)
        date_fin = datetime.combine(request.date_fin, time.max)
        
        # Récupérer les paiements
        paiements_query = db.query(Paiement.paiement_details).filter(
            and_(
                Paiement.created_at <= date_fin,
                Paiement.updated_at >= date_debut
            )
        ).all()
        
        # Parser les paiement_details
        payment_list = []
        for p in paiements_query:
            if isinstance(p.paiement_details, str):
                payment_list.append(json.loads(p.paiement_details))
            else:
                payment_list.append(p.paiement_details)
        
        # Récupérer les niveaux
        niveaux = db.query(Niveau).filter(
            Niveau.status == 1
        ).order_by(Niveau.updated_at).all()
        
        # Extraire les données de paiement pour l'intervalle
        rapport_personalise = extraire_donnees_par_intervalle_for_day(
            payment_list,
            date_debut,
            date_fin
        )
        
        # Récupérer les statistiques d'inscription
        inscription = get_register_for_period(niveaux, date_debut, date_fin, db)

        # Séparer les paiements d'arriéré (année académique différente de
        # l'année active) du reste — voir split_arrears_payments().
        rapport_personalise, arrears_category = split_arrears_payments(rapport_personalise, db)

        # Récupérer les ventes
        sales = get_sales_for_inter(date_debut, date_fin, db)

        # Fusionner les deux sources d'arriéré : anciens rapports enregistrés
        # comme OrderItem/Vente (sales['Arriéré'], flux historique) + ceux
        # tirés des paiements de l'année précédente (arrears_category,
        # nouveau flux) — on additionne plutôt que d'écraser, pour ne perdre
        # aucune donnée existante.
        vente_arriere = sales.get('Arriéré') or SalesCategory(category='Arriéré', quantite=0, total=0, items=[])
        sales['Arriéré'] = SalesCategory(
            category='Arriéré',
            quantite=vente_arriere.quantite + arrears_category.quantite,
            total=vente_arriere.total + arrears_category.total,
            items=vente_arriere.items + arrears_category.items,
        )

        # Dérogations d'arriéré accordées pendant la période (voir
        # RAnnulationArriere.py) — distinct de sales['Arriéré'] : aucun
        # argent n'a été encaissé ici, c'est une dette annulée sur ordre
        # d'un responsable. Affiché séparément, jamais additionné au total.
        derogations_query = (
            db.query(AnnulationArriere)
            .options(joinedload(AnnulationArriere.etudiant))
            .filter(AnnulationArriere.created_at.between(date_debut, date_fin))
            .all()
        )
        derogations = []
        total_derogations = Decimal("0.0")
        for d in derogations_query:
            total_derogations += d.montant_annule
            derogations.append({
                'fname': d.etudiant.nom if d.etudiant else '',
                'prenom': d.etudiant.prenom if d.etudiant else '',
                'annee_academique': d.annee_academique,
                'montant_annule': float(d.montant_annule),
                'ordonne_par': d.ordonne_par,
                'ordonne_par_fonction': d.ordonne_par_fonction,
                'executant_nom': d.executant_nom,
                'executant_role': d.executant_role,
                'raison': d.raison,
                'statut': d.statut,
            })

        # Récupérer les dépenses
        depenses = db.query(Depense).filter(
            Depense.created_at.between(date_debut, date_fin)
        ).all()
        
        # Récupérer les prêts
        loans_query = db.query(Loan).filter(
            Loan.created_at.between(date_debut, date_fin)
        ).all()
        
        loans = []
        for loan in loans_query:
            loans.append(LoanItem(
                id=loan.id,
                amount=loan.amount,
                remaining_balance=loan.remaining_balance,
                user_name=loan.user.name if loan.user else None
            ))
        
        # Récupérer les remboursements
        repayments = db.query(LoanRepayment).filter(
            LoanRepayment.created_at.between(date_debut, date_fin)
        ).all()
       
        repay_list = []
        for repay in repayments:
            repay_list.append({
                'paid_amount':repay.paid_amount,
                'loan_user_name': repay.loan.user.name if repay.loan and repay.loan.user else None
            })

        # --- Dans ta route de rapport ---

        # 1. Récupérer les remboursements de prêts
        # repayments = db.query(LoanRepayment).options(
        #     joinedload(LoanRepayment.loan).joinedload(Loan.user)
        # ).filter(LoanRepayment.created_at.between(date_debut, date_fin)).all()

        # 2. Récupérer les "Autres Transactions" (Nouveau)
        autres = db.query(OtherTransaction).options(
            joinedload(OtherTransaction.user),
            joinedload(OtherTransaction.etudiant)
        ).filter(OtherTransaction.created_at.between(date_debut, date_fin)).all()

        # --- Construction de la réponse ---
        # repay_list = []
        # total_repay = Decimal("0.0")
        # for r in repayments:
        #     total_repay += r.paid_amount
        #     repay_list.append({
        #         'paid_amount': float(r.paid_amount), # Convertir pour le JSON
        #         'loan_user_name': r.loan.user.name if r.loan and r.loan.user else "N/A"
        #     })

        autres_list = []
        total_autres = Decimal("0.0")
        for a in autres:
            total_autres += a.montant
            nom_complet = ''
            if a.etudiant:
                nom_complet = f"{a.etudiant.nom} {a.etudiant.prenom}"
            autres_list.append({
                'description': a.description,
                'montant': float(a.montant),
                'description_supplementaire':a.description_supplementaire,
                'user_name': a.user.name if a.user else "N/A",
                'nom_complet': nom_complet
            })
        print(autres_list)
        # if trans.etudiant:
        #         nom_complet = f"{trans.etudiant.nom} {trans.etudiant.prenom}"
        #     else:
        #         nom_complet = "N/A (Identifiant non reconnu)"
        # print(repay_list)
        # Récupérer le profil
        profile = db.query(Profile).first()
  
  
        niveaux_list = [
            {'id': n.id, 'name': n.name}
            for n in niveaux
        ] 
     
     #    return GlobalReportResponse(
        data = {
            "payments":rapport_personalise,
            "inscription":inscription,
            "sales":sales,
            "getNivel":niveaux_list,
            "depenses":[DepenseItem.model_validate(d) for d in depenses],
            "date1":request.date_debut.strftime('%d-%m-%Y'),
            "date2":request.date_fin.strftime('%d-%m-%Y'),
            "info":profile,
            "type":request.type.value,
            "loans":loans,
            "repayment":repay_list,
            "total_autres": float(total_autres),
            "autres_transactions": autres_list,
            "derogations": derogations,
            "total_derogations": float(total_derogations),
            "date": datetime.now().strftime("%d/%m/%Y")
        }
     #    )
    
        # pdf_buffer = 
        # from fastapi.concurrency import run_in_threadpool

        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
            "global_report.html",  # Votre template Jinja2
            data,
            "global_report.pdf"
        )
        # )
        # pdf_buffer = await run_in_threadpool(
        #     pdf_gen.generate_pdf_for_api,
        #     "global_repport.html",
        #     data,
        #     "global_repport.pdf"
        # )
        # return data
          # Retourner le PDF
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=global_report.pdf"
               }
          )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Erreur dans print_global_report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur s'est produite lors de l'affichage du rapport"
        )
    
# from fastapi.concurrency import run_in_threadpool

# pdf_buffer = await run_in_threadpool(
#     pdf_gen.generate_pdf_for_api,
#     template_file="register_repport.html",
#     data=data,
#     output_filename="register_repport.pdf"
# )



# ============================================================================
# VERSION AVEC QUERY PARAMETERS (alternative)
# ============================================================================

# @router.get("/print-global-report-get", response_model=GlobalReportResponse)
# async def print_global_report_get(
#     date_debut: date = Query(..., description="Date de début (YYYY-MM-DD)"),
#     date_fin: date = Query(..., description="Date de fin (YYYY-MM-DD)"),
#     type: ReportType = Query(..., description="Type de rapport"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Version GET du rapport global
    
#     Exemple: /print-global-report-get?date_debut=2025-01-01&date_fin=2025-01-31&type=Global
#     """
    
#     # Valider les dates
#     if date_debut > date_fin:
#         raise HTTPException(
#             status_code=422,
#             detail="La date de début doit être avant ou égale à la date de fin"
#         )
    
#     # Créer la requête et appeler la fonction principale
#     request = PrintGlobalReportRequest(
#         date_debut=date_debut,
#         date_fin=date_fin,
#         type=type
#     )
    
#     return await print_global_report(request, db)