from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import  StreamingResponse
from sqlalchemy import select, and_, or_, func, case
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from app.Models.MFinancials import Paiement
from app.Models.MModels import Niveau,Etudiant,AnneeAcademique,Classe
from app.Models.MSystems import Profile
from app.Models.MRelations import ClasseEtudiant
from app.database import get_db
from datetime import datetime, date, time
import json
from collections import defaultdict
import logging
from app.Helper.pdf_personaliser import PDFGenerator


logger = logging.getLogger(__name__)

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class PrintPaymentReportRequest(BaseModel):
    """Requête pour le rapport de paiement"""
    classe: str = Field(None, description="Nom de la classe")
    date_debut: str = Field(..., description="Date de début",min_length=36)
    date_fin: Optional[str]=None
    versement: str = Field(..., description="Type de versement ou 'tous les versements'")
    
    @field_validator('classe', 'versement','date_debut')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()
    
    # @model_validator(mode='after')
    # def validate_date_range(self):
    #     if self.date_debut > self.date_fin:
    #         raise ValueError("La date de début doit être avant ou égale à la date de fin")
    #     return self

class PaymentReportItem(BaseModel):
    """Item de rapport de paiement"""
    identifiant: str
    cycle: str = "Non défini"
    nom: Optional[str] = "Non défini"
    prenom: Optional[str] = "Non défini"
    aide_financiere: str = "Non défini"
    classe_name: str = "Non défini"
    paiements: Dict[str, Any]
    check_echeances: Optional[Dict[str, float]] = {}

class PrintPaymentReportResponse(BaseModel):
    """Réponse du rapport de paiement"""
    data_payment: List[Dict[str, Any]]
    info: Optional[Dict[str, Any]]
    versement: str
    check_echeance_s: Optional[Dict[str, Any]]
    debut: str
    fin: str
    classe: str

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def extraire_donnees_par_intervalle_not_for_all(
    json_data: List[Dict],
    date_debut: str,
    date_fin: datetime,
    data_student: List,
    request_classe: str,
    request_versement: str
) -> List[Dict[str, Any]]:
    """
    Extrait les données pour un versement spécifique
    """
    resultat = {}
    check_echeance_final = {
        "Bourse":{},
"1/4 Bourse":{},
"Démie Bourse":{},
"Aucune":{},
    }
    
    for value in data_student:
        if value.nom_classe == request_classe:
            resultat[value.id] = {
                "entetesVersements":{},
                'identifiant': value.identifiant,
                'cycle': value.name or 'Non défini',
                'nom': value.nom or 'Non défini',
                'prenom': value.prenom or 'Non défini',
                'aide_financiere': value.aide_financiere or 'Non défini',
                'classe_name': value.nom_classe or 'Non défini',
                'paiements': {
                    'total': 0,
                    'avance': 0,
                    'balance': 0
                }
            }
            
            for paiement in json_data:
                paiements = paiement.get('paiement_details', {})
                data_student_info = paiements.get('details_etudiant', {})
                data_mois = paiements.get('mois', {})
                check_echeance = paiements.get('check_echeance', {})
                # print(f"check_echeance  11    {check_echeance}")
                info_paiement = paiements.get('info_paiement', {})
                
                for date_str, donnees in info_paiement.items():
                    try:
                        timestamp_cle = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
                    except ValueError:
                        continue
                    
                    if request_versement == 'tous les versements':
                        continue
                    # 1. On récupère proprement le nom de la classe cible
                    classe_info = data_student_info.get('classe')
                    aide_financiere = data_student_info.get('aide_financiere')
 
                    if isinstance(classe_info, list) and len(classe_info) > 0:
                        classe_cible = classe_info[0]
                    else:
                        classe_cible = classe_info
 
                    if classe_cible and classe_cible == resultat[value.id].get('classe_name'):
                        check_echeance_final[aide_financiere] = check_echeance

                    if request_classe != 'tous les versements':
                        etudiant_id = data_student_info.get('identifiant')
                        
                        if request_versement != 'tous les versements':
                            if (resultat[value.id]['identifiant'] == etudiant_id):
                                if donnees.get('status') != 'retourné':
                                    total_verse_temp = donnees.get('total_verse', 0)
                                    sorted_keys = sorted(check_echeance.keys(), key=versement_sort_key)
                        
                                    for key in sorted_keys:# check_echeance.items():
                                        values = check_echeance[key] 
                                        resultat[value.id]['entetesVersements'][key] = values
                                    
                                    # for key, values in check_echeance.items():
                                    #     resultat[value.id]['entetesVersements'][key] = values
                                        if check_echeance[key] <= total_verse_temp:
                                            resultat[value.id]['paiements'][key] = True
                                            
                                            if key == request_versement:
                                                resultat[value.id]['paiements']['total'] = values
                                            
                                            total_verse_temp -= values
                                        elif total_verse_temp < 0:
                                            resultat[value.id]['paiements'][key] = False
                                        else:
                                            resultat[value.id]['paiements'][key] = total_verse_temp
                                            
                                            if key == request_versement:
                                                resultat[value.id]['paiements']['avance'] = total_verse_temp
                                                resultat[value.id]['paiements']['balance'] = values - total_verse_temp
                                            
                                            total_verse_temp -= values
    
    for id_etudiant, etudiant in resultat.items():
        nom_c = etudiant.get('nom_classe')
        aide = etudiant.get('aide_financiere')
        if not etudiant['entetesVersements']: #not etudiant['paiements'] or len(etudiant['paiements']) <= 1:
             
            for key, values in check_echeance_final[aide].items():
            # if nom_c in check_echeance_final and aide in check_echeance_final[nom_c]:
                # for key, values in check_echeance_final[nom_c][aide].items():
                    if key not in etudiant['paiements']:
                        etudiant['paiements'][key] = False
                        etudiant['entetesVersements'][key] = values
    return list(resultat.values())

def versement_sort_key(s):
    # Extrait le premier chiffre pour trier numériquement
    import re
    match = re.search(r'(\d+)', s)
    return int(match.group(1)) if match else 0

def extraire_donnees_par_intervalle(
    json_data: List[Dict],
    date_debut: str,
    date_fin: datetime,
    data_student: List
) -> List[Dict[str, Any]]:
    """
    Extrait les données pour tous les versements
    """
    resultat = {}
    check_echeance_final = {
        "Bourse":{},
        "1/4 Bourse":{},
        "Démie Bourse":{},
        "Aucune":{},
            }
    
    for value in data_student:
        resultat[value.id] = {
            "entetesVersements":{},
            'identifiant': value.identifiant,
            'cycle': value.name or 'Non défini',
            'nom': value.nom or 'Non défini',
            'prenom': value.prenom or 'Non défini',
            'classe_name': value.nom_classe or 'Non défini',
            'aide_financiere': value.aide_financiere or 'Non défini',
            'paiements': {
                'balance': 0,
                'check_echeances': {}
            },
            'check_echeances': {}
        }
        
        for paiement in json_data:
            paiements = paiement.get('paiement_details', {})
            data_student_info = paiements.get('details_etudiant', {})
            data_mois = paiements.get('mois', {})
            check_echeance = paiements.get('check_echeance', {})

            # id = data_student_info.get('identifiant')
            # if id == "1-54000":
            #     print(f"\n\n\n\n{check_echeance}\n\n\n\n\n\n")
            # print(f"check_echeance  2    {check_echeance}      \n\n\n\n       {id}")
            # resultat[value.id]['paiements']['check_echeances'] = check_echeance

            # if value.nom_classe not in check_echeance_final:
            #     check_echeance_final[value.nom_classe] = {}
            #     [value.nom_classe][value.aide_financiere]
            # check_echeance_final = check_echeance
            
            info_paiement = paiements.get('info_paiement', {})
            
            for date_str, donnees in info_paiement.items():
                try:
                    timestamp_cle = datetime.strptime(date_str, '%d-%m-%Y %H:%M')
                except ValueError:
                    continue
                
                etudiant_id = data_student_info.get('identifiant')

                classe_info = data_student_info.get('classe')
                aide_financiere = data_student_info.get('aide_financiere')
                # print("\n\n\n\n")
                # print(f"donnees  {donnees}")
                # print("\n\n\n\n")
                if isinstance(classe_info, list) and len(classe_info) > 0:
                    classe_cible = classe_info[0]
                else:
                    classe_cible = classe_info

                if classe_cible and classe_cible == resultat[value.id].get('classe_name'):
                    check_echeance_final[aide_financiere] = check_echeance
                
                if resultat[value.id]['identifiant'] == etudiant_id:
                    if donnees.get('status') != 'retourné':
                        total_verse_temp = donnees.get('total_verse', 0)
                        # Trier les échéances par leur numéro
                        sorted_keys = sorted(check_echeance.keys(), key=versement_sort_key)
                        
                        for key in sorted_keys:# check_echeance.items():
                            values = check_echeance[key]


                            resultat[value.id]['entetesVersements'][key] = values
                            resultat[value.id]['paiements']['check_echeances'][key] = values
                            if check_echeance[key] <= total_verse_temp:
                                resultat[value.id]['paiements'][key] = True
                                resultat[value.id]['check_echeances'][key] = values
                                total_verse_temp -= values

                            elif total_verse_temp > 0:
                                # Paiement partiel (Avance)
                                resultat[value.id]['paiements'][key] = total_verse_temp
                                resultat[value.id]['paiements']['balance'] = values - total_verse_temp
                                total_verse_temp = 0 # Plus d'argent disponible après une avance
                            # elif total_verse_temp < 0:
                            #     resultat[value.id]['paiements'][key] = False
                            else:
                                resultat[value.id]['paiements'][key] = False
                                # resultat[value.id]['paiements'][key] = total_verse_temp
                                # resultat[value.id]['paiements']['balance'] = values - total_verse_temp
                                # total_verse_temp -= values
    
    # Ajouter les versements manquants comme False
    for id_etudiant, etudiant in resultat.items():
        nom_c = etudiant.get('nom_classe')
        aide = etudiant.get('aide_financiere')
        if not etudiant['entetesVersements']: #not etudiant['paiements'] or len(etudiant['paiements']) <= 1:
            # print(f"\n\n\n\n{etudiant}\n\n\n\n\n\n")
            for key, values in check_echeance_final[aide].items():
            # if nom_c in check_echeance_final and aide in check_echeance_final[nom_c]:
                # for key, values in check_echeance_final[nom_c][aide].items():
                    if key not in etudiant['paiements']:
                        etudiant['paiements'][key] = False
                        etudiant['entetesVersements'][key] = values
    
    return list(resultat.values())

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()

@router.post("/print-rapport-paiement")#, response_model=PrintPaymentReportResponse
def print_payment_report(
    request: PrintPaymentReportRequest,
    db: Session = Depends(get_db)
):
    """
    Génère un rapport de paiement pour une classe et une période données
    
    - **classe**: Nom de la classe
    - **date_debut**: Date de début de la période
    - **date_fin**: Date de fin de la période
    - **versement**: Type de versement spécifique ou "tous les versements"
    """
    
    try:
        # Créer les datetime de début et fin de journée
        date_debut = request.date_debut #datetime.combine(request.date_debut, time.min)
        date_fin = request.date_fin#datetime.combine(request.date_fin, time.max)
        # Récupérer l'année académique active
        annee = db.query(AnneeAcademique).filter(
            AnneeAcademique.id == date_debut
        ).first()
        
        if not annee:
            raise HTTPException(
                status_code=404,
                detail="Aucune année académique active trouvée"
            )
        
        # Récupérer tous les paiements de l'année académique
        paiements_query = db.query(Paiement.paiement_details).filter(
            Paiement.annee_academique == annee.annee_academique
        ).all()
        
        # Parser les paiement_details
        payment_list = []
        for p in paiements_query:
            if isinstance(p.paiement_details, str):
                payment_list.append(json.loads(p.paiement_details))
            else:
                payment_list.append(p.paiement_details)
        
        # Récupérer les données des étudiants avec jointures
        # Utilisation de db.execute pour une query raw-like
        from sqlalchemy import text
        
        # data_student_query = db.execute(
        #     text("""
        #         SELECT 
        #             etudiants.id,
        #             etudiants.identifiant,
        #             classes.nom_classe,
        #             niveaux.name,
        #             etudiants.nom,
        #             etudiants.prenom,
        #             etudiants.aide_financiere
        #         FROM etudiants
        #         LEFT JOIN classes_etudiants ON classes_etudiants.etudiant_id = etudiants.id
        #         LEFT JOIN annee_academiques ON classes_etudiants.annee_academique_id = annee_academiques.id
        #         LEFT JOIN classes ON classes_etudiants.classes_id = classes.id
        #         LEFT JOIN niveaux ON classes_etudiants.niveau_id = niveaux.id
        #         WHERE classes_etudiants.annee_academique_id = :annee_id
        #         AND classes_etudiants.status = 1
        #         ORDER BY etudiants.nom, niveaux.updated_at
        #     """),
        #     {"annee_id": annee.id}
        # )
        
        # data_student = data_student_query.fetchall()

        # Préparation de la base de la requête
        query_str = """
            SELECT 
                etudiants.id,
                etudiants.identifiant,
                classes.nom_classe,
                niveaux.name,
                etudiants.nom,
                etudiants.prenom,
                etudiants.aide_financiere
            FROM etudiants
            LEFT JOIN classes_etudiants ON classes_etudiants.etudiant_id = etudiants.id
            LEFT JOIN annee_academiques ON classes_etudiants.annee_academique_id = annee_academiques.id
            LEFT JOIN classes ON classes_etudiants.classes_id = classes.id
            LEFT JOIN niveaux ON classes_etudiants.niveau_id = niveaux.id
            WHERE classes_etudiants.annee_academique_id = :annee_id
            AND classes_etudiants.status = 1
        """

        # Paramètres de la requête
        params = {"annee_id": annee.id}

        # AJOUT DU FILTRE CONDITIONNEL
        if request.classe.lower() != "all":
            query_str += " AND classes.nom_classe = :nom_classe"
            params["nom_classe"] = request.classe

        # Ajout du tri à la fin
        query_str += " ORDER BY etudiants.nom, niveaux.updated_at"

        # Exécution
        data_student_query = db.execute(text(query_str), params)
        data_student = data_student_query.fetchall()
        
        # Convertir en objets simples pour faciliter le traitement
        class StudentData:
            def __init__(self, row):
                self.id = row.id
                self.identifiant = row.identifiant 
                self.nom_classe = row.nom_classe
                self.name = row.name
                self.nom = row.nom
                self.prenom = row.prenom
                self.aide_financiere = row.aide_financiere
        
        students = [StudentData(row) for row in data_student]
        
        # Extraire les données selon le type de versement
        if request.versement != 'tous les versements':
            data_payment = extraire_donnees_par_intervalle_not_for_all(
                payment_list,
                date_debut,
                date_fin,
                students,
                request.classe,
                request.versement
            )
        else:
            data_payment = extraire_donnees_par_intervalle(
                payment_list,
                date_debut,
                date_fin,
                students
            )
        
        # Récupérer le dernier check_echeance
        check_echeance_s = {}
        if payment_list:
            for paiement in payment_list:
                paiements = paiement.get('paiement_details', {})
                check_echeance = paiements.get('check_echeance', {})
                if check_echeance:
                    check_echeance_s = check_echeance
        
        # Récupérer le profil
        profile = db.query(Profile).first()
        # profile_dict = None
        # if profile:
        #     profile_dict = {
        #         'nom': profile.nom,
        #         'email': getattr(profile, 'email', None),
        #         'adresse': getattr(profile, 'adresse', None)
        #     }

        

        # Imaginons que 'data_payment' est votre liste d'étudiants brute
        # grouped_payments = defaultdict(list)

        # for student in data_payment:
        #     classe = student.get('classe_name', 'Sans Classe')
        #     grouped_payments[classe].append(student)

        grouped_results = defaultdict(list)
        for student in data_payment:
            grouped_results[student['classe_name']].append(student)

        # Convertir en dictionnaire classique pour Jinja2 (optionnel mais recommandé)
        # grouped_payments = dict(grouped_payments)
        # return "grouped_payments"
        data ={
            "data_payment":data_payment,
            "groupedPayments":grouped_results,
            "info":profile,
            "versement":request.versement,
            "check_echeance_s":check_echeance_s,
            "debut":request.date_debut,#.strftime('%Y-%m-%d'),
            "fin":None, #request.date_fin.strftime('%Y-%m-%d'),
            "classe":request.classe,
            "entetesVersements":check_echeance_s,
            "date": datetime.now().strftime("%d/%m/%Y"),
        }

            
        # return data
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
            "payment_repport.html",  # Votre template Jinja2
            data,
            "payment_repport.pdf"
        )
    #     pdf_buffer = pdf_gen.generate_pdf_for_api(
    #     template_file="payment_repport.html",  # Votre template Jinja2
    #     data=data,
    #     output_filename="payment_repport.pdf"
    # )
        # return data
          # Retourner le PDF
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=payment_repport.pdf"
               }
          )
        
        # return PrintPaymentReportResponse(
        #     data_payment=data_payment,
        #     info=profile_dict,
        #     versement=request.versement,
        #     check_echeance_s=check_echeance_s,
        #     debut=request.date_debut.strftime('%Y-%m-%d'),
        #     fin=request.date_fin.strftime('%Y-%m-%d'),
        #     classe=request.classe
        # )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur dans print_payment_report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur s'est produite lors de l'affichage du rapport"
        )


# ============================================================================
# VERSION AVEC SQLAlchemy ORM (alternative à la query raw)
# ============================================================================

# @router.post("/print-payment-report-orm", response_model=PrintPaymentReportResponse)
# async def print_payment_report_orm(
#     request: PrintPaymentReportRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#     Version avec SQLAlchemy ORM pur (sans SQL raw)
#     """
    
#     try:
#         # Récupérer l'année académique active
#         annee = db.query(AnneeAcademique).filter(
#             AnneeAcademique.status == 1
#         ).first()
        
#         if not annee:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Aucune année académique active trouvée"
#             )
        
#         # Créer les datetime
#         date_debut = datetime.combine(request.date_debut, time.min)
#         date_fin = datetime.combine(request.date_fin, time.max)
        
#         # Récupérer les paiements
#         paiements_query = db.query(Paiement.paiement_details).filter(
#             Paiement.annee_academique == annee.annee_academique
#         ).all()
        
#         payment_list = []
#         for p in paiements_query:
#             if isinstance(p.paiement_details, str):
#                 payment_list.append(json.loads(p.paiement_details))
#             else:
#                 payment_list.append(p.paiement_details)
        
#         # Récupérer les étudiants avec ORM
#         students_query = db.query(
#             Etudiant.id,
#             Etudiant.identifiant,
#             Niveau.niveau_detude,
#             Classe.nom_classe,
#             Niveau.name,
#             Etudiant.nom,
#             Etudiant.prenom,
#             Etudiant.aide_financiere
#         ).select_from(Etudiant)\
#         .outerjoin(ClasseEtudiant, ClasseEtudiant.etudiant_id == Etudiant.id)\
#         .outerjoin(AnneeAcademique, ClasseEtudiant.annee_academique_id == AnneeAcademique.id)\
#         .outerjoin(Classe, ClasseEtudiant.classes_id == Classe.id)\
#         .outerjoin(Niveau, ClasseEtudiant.niveau_id == Niveau.id)\
#         .filter(
#             ClasseEtudiant.annee_academique_id == annee.id,
#             ClasseEtudiant.status == 1
#         ).order_by(Etudiant.nom, Niveau.updated_at).all()
        
#         # Convertir en objets
#         class StudentData:
#             def __init__(self, row):
#                 self.id = row.id
#                 self.identifiant = row.identifiant
#                 self.niveau_detude = row.niveau_detude
#                 self.nom_classe = row.nom_classe
#                 self.name = row.name
#                 self.nom = row.nom
#                 self.prenom = row.prenom
#                 self.aide_financiere = row.aide_financiere
        
#         students = [StudentData(row) for row in students_query]
        
#         # Extraire les données
#         if request.versement != 'tous les versements':
#             data_payment = extraire_donnees_par_intervalle_not_for_all(
#                 payment_list,
#                 date_debut,
#                 date_fin,
#                 students,
#                 request.classe,
#                 request.versement
#             )
#         else:
#             data_payment = extraire_donnees_par_intervalle(
#                 payment_list,
#                 date_debut,
#                 date_fin,
#                 students
#             )
        
#         # Récupérer le dernier check_echeance
#         check_echeance_s = {}
#         if payment_list:
#             for paiement in reversed(payment_list):
#                 paiements = paiement.get('paiement_details', {})
#                 check_echeance = paiements.get('check_echeance', {})
#                 if check_echeance:
#                     check_echeance_s = check_echeance
#                     break
        
#         # Récupérer le profil
#         profile = db.query(Profile).first()
#         profile_dict = None
#         if profile:
#             profile_dict = {
#                 'nom': profile.nom,
#                 'email': getattr(profile, 'email', None),
#                 'adresse': getattr(profile, 'adresse', None)
#             }
        
#         return PrintPaymentReportResponse(
#             data_payment=data_payment,
#             info=profile_dict,
#             versement=request.versement,
#             check_echeance_s=check_echeance_s,
#             debut=request.date_debut.strftime('%Y-%m-%d'),
#             fin=request.date_fin.strftime('%Y-%m-%d'),
#             classe=request.classe
#         )
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Erreur dans print_payment_report_orm: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail="Une erreur s'est produite lors de l'affichage du rapport"
#         )


# ============================================================================
# MODÈLES SQLAlchemy ADDITIONNELS
# ============================================================================

# class ClasseEtudiant(Base):
#     __tablename__ = "classes_etudiants"
    
#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     etudiant_id = Column(String(36), ForeignKey("etudiants.id"))
#     classes_id = Column(String(36), ForeignKey("classes.id"))
#     niveau_id = Column(String(36), ForeignKey("niveaux.id"))
#     annee_academique_id = Column(String(36), ForeignKey("annee_academiques.id"))
#     status = Column(Integer, default=1)
#     created_at = Column(DateTime, nullable=True)
#     updated_at = Column(DateTime, nullable=True)
    
#     etudiant = relationship("Etudiant", back_populates="classe_etudiants")
#     classe = relationship("Classe")
#     niveau = relationship("Niveau")
#     annee_academique = relationship("AnneeAcademique")