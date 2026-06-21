from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import os 
import logging
import pandas as pd
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
import locale
from app.database import get_db
from app.Models.MModels import  AnneeAcademique,Niveau,Classe,User,Etudiant,Faculte
from app.Models.MRelations import ClasseEtudiant,CoursEtudiant
from app.Models.MSystems import Profile
from fastapi.responses import  StreamingResponse,FileResponse
from babel.dates import format_date
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.Helper.pdf_personaliser import PDFGenerator
router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()

# Modèles Pydantic pour la validation
class MassBulletinRequest(BaseModel):
    annee_academique: str = Field(..., description="Année académique")
    classe: str = Field(..., description="ID de la classe")
    mois: str = Field(..., description="Mois concerné")
    
    @validator('annee_academique')
    def annee_must_exist(cls, v, values):
        # Validation sera faite dans l'endpoint avec la DB
        if not v:
            raise ValueError("L'année académique est requise")
        return v
    
    @validator('classe')
    def classe_must_exist(cls, v):
        if not v:
            raise ValueError("La classe est requise")
        return v
    
    @validator('mois')
    def mois_required(cls, v):
        if not v:
            raise ValueError("Le mois est requis")
        return v


# Fonction auxiliaire pour calculer la moyenne générale
def calculer_moyenne_generale(
    data_etudiant: Any, 
    identifiant: str, 
    mois: str
) -> tuple[float, List[float], List[float]]:
    """
    Calcule la moyenne générale d'un étudiant
    
    Args:
        data_etudiant: Données de l'étudiant (JSON ou dict)
        identifiant: Identifiant de l'étudiant
        mois: Mois concerné ou 'all'
    
    Returns:
        Tuple contenant (moyenne, notes, coefficients)
    """
    # Parser les données
    if isinstance(data_etudiant, str):
        parse_data = json.loads(data_etudiant)
    else:
        parse_data = data_etudiant
    
    if identifiant not in parse_data:
        return (0.0, [], [])
    
    data = parse_data[identifiant]
    notes = []
    coefficient = []
    
    def traiter_section(section: Dict) -> None:
        """Traite une section (base ou orale)"""
        for matiere, details in section.items():
            coef = float(details['coefficients'])
            
            if mois == 'all':
                for note_mois,val in details['notes'].items(): 
                    notes.append(val)
                    coefficient.append(coef)
            elif mois in details['notes']:
                notes.append(details['notes'][mois])
                coefficient.append(coef)
    
    # Traiter les sections base et orale
    if 'base' in data:
        traiter_section(data['base'])
    if 'orale' in data:
        traiter_section(data['orale'])
     
    notes = [to_float(n) for n in notes]
    coefficient = [to_float(c) for c in coefficient] 
    total_coef = sum(coefficient)

     # moyenne = (sum(notes) / total_coef) * 10 if total_coef > 0 else 0

    # Calculer la moyenne
    if len(coefficient) > 0 and sum(coefficient) > 0:
        moyenne = (sum(notes) / sum(coefficient)) * 10
    else:
        moyenne = 1.0
    
    return (round(moyenne, 2), notes, coefficient)


def moyenne_and_place(
    classes_id: int, 
    mois: str, 
    student_list: List[Any],full_info=False
) -> Dict[str, Any]:
    """
    Calcule les moyennes et le classement des étudiants
    
    Args:
        classes_id: ID de la classe
        mois: Mois concerné
        student_list: Liste des étudiants
    
    Returns:
        Dictionnaire avec les résultats et la moyenne de classe
    """
    try:
        data_promus = []
        moyennes_classe = []
        for value in student_list: 
            if value.data_etudiant != '"[]"':
                
                results = calculer_moyenne_generale(
                    value.data_etudiant, 
                    value.identifiant, 
                    mois
                )
                
                moyenne = results[0]
                moyennes_classe.append(moyenne)
                
                data_promus.append({
                    'etudiant_id': value.etudiant_id,
                    'identifiant': value.identifiant,
                    'nom': value.fname,
                    'prenom': value.lname,
                    'nisu':value.nisu if full_info else None,
                    'sexe':value.sexe if full_info else None,
                    'lieu_de_naissance':value.lieu_de_naissance if full_info else None,
                    'date_de_naissance':_naissance(value.date_de_naissance) if full_info else None,
                    'moyenne': moyenne
                })
            else:
                logger.info(f"Étudiant sans notes: {value.fname} {value.lname}")
        
        # Calculer la moyenne de classe
        if len(moyennes_classe) > 0:
            moyenne_classe = sum(moyennes_classe) / len(moyennes_classe)
        else:
            moyenne_classe = 0.0
        
        # Trier par moyenne décroissante
        data_promus.sort(key=lambda x: x['moyenne'], reverse=True)
        
        # Attribuer les rangs
        rang = 0
        derniere_moyenne = None
        
        for student in data_promus:
            if derniere_moyenne is None or student['moyenne'] != derniere_moyenne:
                rang += 1
                derniere_moyenne = student['moyenne']
            
            student['rang'] = rang
        
        return {
            'result': data_promus,
            'moyenne_classe': round(moyenne_classe, 2)
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Erreur dans moyenne_and_place: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/imprime-mas-bulletin")
def impression_mas_bulletin(request: MassBulletinRequest, db: Session = Depends(get_db)):
    """
    Endpoint pour l'impression en masse des bulletins d'une classe
    
    Args:
        request: Données de la requête validées
        db: Session de base de données
    
    Returns:
        Données des bulletins de tous les étudiants de la classe
    """
    try:
        # Validation de l'année académique
        annee_exists = db.query(AnneeAcademique).filter(
            AnneeAcademique.annee_academique == request.annee_academique
        ).first()
        
        if not annee_exists:
            return {"errors": "L'année académique spécifiée n'existe pas"}
        
        # Validation de la classe
        classe_exists = db.query(Classe).filter(
            Classe.id == request.classe
        ).first()
        
        if not classe_exists:
            return {"errors": "La classe spécifiée n'existe pas"}
        
        
        # Récupérer l'année académique avec ses dates
        date = db.query(AnneeAcademique).filter(
            AnneeAcademique.annee_academique == request.annee_academique
        ).with_entities(
            AnneeAcademique.id,
            AnneeAcademique.date_debut,
            AnneeAcademique.date_fin,
            AnneeAcademique.annee_academique
        ).first()
        
        data_bulletin = (
               db.query(
                    CoursEtudiant.id.label("coursEID"),
                    CoursEtudiant.etudiant_id.label("etudiant_id"),
                    CoursEtudiant.identifiant.label("identifiant"),
                    CoursEtudiant.annee_academique.label("annee_academique_ce"),
                    CoursEtudiant.niveau.label("niveau_id"),
                    CoursEtudiant.classe.label("classe_id"),
                    CoursEtudiant.data_etudiant.label("data_etudiant"),

                    Niveau.name.label("niveau"),
                    Etudiant.nom.label("fname"),
                    Etudiant.prenom.label("lname"),
                    Faculte.nom.label("fac_name"),
                    Classe.nom_classe.label("nom_classe"),
                    ClasseEtudiant.annee_academique_id.label("annee_id"),
                    AnneeAcademique.annee_academique.label("annee_academique")
               )
               .join(
                    ClasseEtudiant,
                    and_(
                         ClasseEtudiant.classes_id == CoursEtudiant.classe,
                         ClasseEtudiant.etudiant_id == CoursEtudiant.etudiant_id,
                         ClasseEtudiant.annee_academique_id == date.id,
                         ClasseEtudiant.status == 1
                    )
               ) .join(  
                AnneeAcademique,
                AnneeAcademique.id == ClasseEtudiant.annee_academique_id
            )
               .outerjoin(Faculte, Faculte.id == CoursEtudiant.faculte)
               .outerjoin(Niveau, Niveau.id == CoursEtudiant.niveau)
               .outerjoin(Classe, Classe.id == CoursEtudiant.classe)
               .outerjoin(Etudiant, Etudiant.id == CoursEtudiant.etudiant_id)
               .filter(
                    ClasseEtudiant.classes_id == request.classe,
                    CoursEtudiant.annee_academique == request.annee_academique
               )
               .all()
               )



        all_headers = ''
        
        # Vérifier si des données ont été trouvées
        if len(data_bulletin) < 1:
            logger.info("Data error - Aucun bulletin trouvé")
            return {"errors": "Data error"}
        
        # Traitement du mois
        if request.mois:
            if not request.mois:
                return {"error": "Données manquantes."}
            
            mois_print = []
            
            if date: 
                try:
                    # locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
                    locale.setlocale(locale.LC_TIME, 'French_France.1252')

                except:
                    pass
                
                start = datetime.strptime(str(date.date_debut), '%Y-%m-%d')
                end = datetime.strptime(str(date.date_fin), '%Y-%m-%d')
                
                current = start
                while current <= end:
                    month_name = format_date(
                        current,
                        format="MMMM",
                        locale="fr"
                    ).capitalize()

                    mois_print.append(month_name)
                    current += relativedelta(months=1)

                # while current <= end:
                #     month_name = current.strftime('%B').capitalize()
                #     mois_print.append(month_name)
                #     current += relativedelta(months=1)
                # while current <= end:
                #     # On génère le nom du mois
                #     month_raw = current.strftime('%B').capitalize()
                    
                #     # Sécurité : Si on est sur Windows, on décode proprement pour éviter les Dã©
                #     try:
                #         # On tente de redécoder si le système a utilisé un mauvais encodage
                #         month_name = month_raw.encode('latin1').decode('utf-8')
                #     except (UnicodeEncodeError, UnicodeDecodeError):
                #         # Si ça échoue, c'est que c'est déjà du bon UTF-8
                #         month_name = month_raw

                #     mois_print.append(month_name)
                #     current += relativedelta(months=1)
            
            # Vérifier si le mois est valide
            if request.mois not in mois_print and request.mois != 'Annuel':
                return {"error": "Données manquantes."}
            
            request_data = request.mois
            all_headers = mois_print
        
        # Déterminer le mois pour le calcul
        data_month = request_data if (request.mois != 'all' and request.mois != 'Annuel') else 'all'
        
        # Calculer les moyennes et classements
        data = moyenne_and_place(
            request.classe, 
            data_month,
            data_bulletin,False
        )
        
        # Récupérer le profil
        profile = db.query(Profile).first()
        
        # Préparer la réponse
        result = {
            'data_students': [
                {
                    'cours_etudiant': item.coursEID,
                    'etudiant_id': item.etudiant_id,
                    'identifiant': item.identifiant,
                    'data_etudiant': item.data_etudiant,

                    'name': item.niveau,
                    'niveau_name': item.niveau,
                    'fname': item.fname,
                    'lname': item.lname,
                    'fac_name': item.fac_name,
                    'nom_classe': item.nom_classe,
                    'annee_academique': item.annee_academique,
                    'classe': item.classe_id
                }
                for item in data_bulletin
            ],

            'info': profile,
            'mois': request.mois,
            'allHeaders': all_headers,
            'moyenne_classe': data.get('moyenne_classe', 1),
            'result': data.get('result', []),
            'data': data
        }
 
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "multiple_bulletin_print.html",  # Votre template Jinja2
        result,
        "multiple_bulletin_print.pdf"
    )
        
    #            pdf_buffer = pdf_gen.generate_pdf_for_api_html(
    #     template_file="multiple_bulletin_print.html",  # Votre template Jinja2
    #     data=result,
    #     output_filename="multiple_bulletin_print.pdf"
    # )
        # return data
          # Retourner le PDF 
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=multiple_bulletin_print.pdf; charset=utf-8"
               }
          )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Erreur lors de l'impression des bulletins: {str(e)}", exc_info=True)
        return {"errors": str(e), "err": request_data if 'request_data' in locals() else None}
def to_float(value, default=0.0):
    try:
        if value in ("", None, "[]"):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default
    


class DecisionRequest(BaseModel):
    annee_ac: str = Field(..., description="Année académique")
    classe: str = Field(..., description="ID de la classe")
    is_excel:bool
def _naissance(date_de_naissance) -> str:
    if date_de_naissance:
        if isinstance(date_de_naissance, str):
            dt = datetime.fromisoformat(date_de_naissance)
        else:
            dt = date_de_naissance
        return dt.strftime("%d %b %Y")
    return ""
@router.post("/print-repport-decision")
def impression_mas_bulletin(request: DecisionRequest, db: Session = Depends(get_db)):
    annee_exists = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == request.annee_ac
    ).first()
    
    if not annee_exists:
        return {"errors": "L'année académique spécifiée n'existe pas"}
    
    # Validation de la classe
    classe_exists = db.query(Classe).filter(
        Classe.id == request.classe
    ).first()
    
    if not classe_exists:
        return {"errors": "La classe spécifiée n'existe pas"}

    date = db.query(AnneeAcademique).filter(
            AnneeAcademique.id == request.annee_ac
        ).with_entities(
            AnneeAcademique.id,
            AnneeAcademique.date_debut,
            AnneeAcademique.date_fin,
            AnneeAcademique.annee_academique
        ).first()
    
    data_bulletin = (
        db.query(
            CoursEtudiant.id.label("coursEID"),
            CoursEtudiant.etudiant_id.label("etudiant_id"),
            CoursEtudiant.identifiant.label("identifiant"),
            CoursEtudiant.annee_academique.label("annee_academique_ce"),
            CoursEtudiant.niveau.label("niveau_id"),
            CoursEtudiant.classe.label("classe_id"),
            CoursEtudiant.data_etudiant.label("data_etudiant"),

            Niveau.name.label("niveau"),
            Etudiant.nom.label("fname"),
            Etudiant.prenom.label("lname"),
            Etudiant.sexe.label("sexe"),
            Etudiant.nisu.label("nisu"),
            Etudiant.date_de_naissance.label("date_de_naissance"),
            Etudiant.lieu_de_naissance.label("lieu_de_naissance"),
            Faculte.nom.label("fac_name"),
            Classe.nom_classe.label("nom_classe"),
            ClasseEtudiant.annee_academique_id.label("annee_id"),
            AnneeAcademique.annee_academique.label("annee_academique")
        )
        .join(
            ClasseEtudiant,
            and_(
                ClasseEtudiant.classes_id == CoursEtudiant.classe,
                ClasseEtudiant.etudiant_id == CoursEtudiant.etudiant_id,
                ClasseEtudiant.annee_academique_id == date.id,
                ClasseEtudiant.status == 1
            )
        ) .join(  
        AnneeAcademique,
        AnneeAcademique.id == ClasseEtudiant.annee_academique_id
    )
        .outerjoin(Faculte, Faculte.id == CoursEtudiant.faculte)
        .outerjoin(Niveau, Niveau.id == CoursEtudiant.niveau)
        .outerjoin(Classe, Classe.id == CoursEtudiant.classe)
        .outerjoin(Etudiant, Etudiant.id == CoursEtudiant.etudiant_id)
        .filter(
            ClasseEtudiant.classes_id == request.classe,
            CoursEtudiant.annee_academique == date.annee_academique
        )
        .all()
        )
    if len(data_bulletin) < 1:
        logger.info("Data error - Aucun bulletin trouvé")
        return {"errors": "Aucun bulletin trouvé"}
    
    data = moyenne_and_place(
        request.classe,
        'all',
        data_bulletin, True
    )
        
        # Récupérer le profil
    profile = db.query(Profile).first()

    result = {
        'classe':classe_exists.nom_classe,
        'annee_academique': date.annee_academique, 
        'moyenne_classe': data.get('moyenne_classe', 1),
        # 'result': sorted(data.get('result', [])),
        'result': sorted(data.get('result', []), key=lambda x: x.get('nom', '').upper()),
    }
    if request.is_excel:
        datas = sorted(data.get('result', []), key=lambda x: x.get('nom', '').upper())
        df = pd.DataFrame(datas)
    
        df['Date et Lieu de naissance'] = df['date_de_naissance'] + " à " + df['lieu_de_naissance']
        df['Mention'] = df['moyenne'].apply(lambda x: 'Admis(e)' if x >= 5.0 else 'Echoué(e)')

        cols_to_export = ['nom', 'prenom', 'sexe', 'Date et Lieu de naissance', 'nisu', 'moyenne', 'rang', 'Mention']
        df_final = df[cols_to_export]
        df_final.columns = ['Nom', 'Prénom', 'Sexe', 'Date et Lieu de naissance', 'NISU', 'Moyenne', 'Rang', 'Mention']

        df_final.to_excel("Palmares_2AF_Fidèle.xlsx", index=False)

        cache_dir = os.getenv('LOCALAPPDATA', os.getcwd()) 
        temp_file = os.path.join(cache_dir, "temp_export.xlsx")
        df_final.to_excel(temp_file, index=False)
        print(f"✅ Excel enregistré ici : {temp_file}")
    
        return FileResponse(
            path=temp_file, 
            filename="Palmares_2AF_2025.xlsx", # Nom que l'utilisateur verra
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ) 
    else:
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "list_decision.html",
        result,
        "Palmares_Fidèle.pdf"
        )
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=Palmares_Fidèle.pdf"
            }
        ) 
        
