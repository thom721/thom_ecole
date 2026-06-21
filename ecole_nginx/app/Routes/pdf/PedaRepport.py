from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
import locale
from app.database import get_db
from app.Models.MModels import  AnneeAcademique,Niveau,Classe,User,Etudiant,Faculte
from app.Models.MRelations import ClasseEtudiant,CoursEtudiant
from app.Models.MSystems import Profile
from fastapi.responses import  StreamingResponse
# Configuration du logging
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
    niveau_id: str = Field(..., description="Niveau concerné")
    
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
                for note_mois in details['notes']:
                    notes.append(note_mois)
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
    student_list: List[Any]
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
          #   print(value)
          #   print(value._mapping.keys())
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


@router.post("/peda-repport")
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
        
        logger.info(f"Année académique: {request.annee_academique}, Classe: {request.classe}")
        
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
        if request.classe and request.classe != "Toutes les classes":
            query = query.filter(ClasseEtudiant.classes_id == request.classe)


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
                # Configurer la locale en français
                try:
                    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
                except:
                    pass
                
                start = datetime.strptime(str(date.date_debut), '%Y-%m-%d')
                end = datetime.strptime(str(date.date_fin), '%Y-%m-%d')
                
                current = start
                while current <= end:
                    month_name = current.strftime('%B').capitalize()
                    mois_print.append(month_name)
                    current += relativedelta(months=1)
            
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
            data_bulletin
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
                # 'data_etudiant': item.data_etudiant,

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
        # return result
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        template_file="pedagogic_repport.html",  # Votre template Jinja2
        data=result,
        output_filename="pedagogic_repport.pdf"
    )
        # return data
          # Retourner le PDF
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=pedagogic_repport.pdf"
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

# Fonction pour obtenir la session DB (à a 

# 2025/2026, Classe: 70a93c37-75e6-4fb7-868d-08e3dbe3cf99