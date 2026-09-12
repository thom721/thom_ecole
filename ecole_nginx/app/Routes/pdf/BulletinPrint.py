from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import  StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import Session, joinedload
import locale
from babel.dates import format_date
from app.database import get_db
from app.Models.MModels import  AnneeAcademique,Niveau,Classe,User,Etudiant,Faculte,Cours
from app.Models.MRelations import ClasseEtudiant,CoursEtudiant
from app.Models.MSystems import Profile
from app.Helper.pdf_personaliser import PDFGenerator
from app.dependencies.Dependencie import check_permission
# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()

# Modèles Pydantic pour la validation
class BulletinRequest(BaseModel):
    bulletin: str = Field(..., description="ID du cours étudiant")
    mois: Optional[str] = None
    Trimestre: Optional[str] = None
    Controle: Optional[str] = None
    session: Optional[str] = None

    etudiant_id: Optional[str] = None
    annee_academique: Optional[str] = None
    get_notes: Optional[bool] = False


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
                for note_mois, val in details['notes'].items():
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
    # Calculer la moyenne
    if len(coefficient) > 0 and sum(coefficient) > 0:
        moyenne = (sum(notes) / sum(coefficient)) * 10
    else:
        moyenne = 1.0
    
    return (round(moyenne, 2), notes, coefficient)

def to_float(value, default=0.0):
    try:
        if value in ("", None, "[]"):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def calculer_moyenne_session(
    data_etudiant: Any,
    identifiant: str,
    session: str,
    db: Session,
) -> Dict[str, Any]:
    """Équivalent de calculer_moyenne_generale() pour la structure imbriquée
    par session/controle du niveau Universitaire (bloc), voir RNotes.py
    CAS 2 : data[identifiant][session][controle][type_matiere][cours].
    Structurellement différente de la structure 'mois' (pas de 'base'/
    'orale', clé 'cours' au lieu de 'notes' clées par mois) — calculer_
    moyenne_generale ne peut pas être réutilisée telle quelle.

    coefficients n'est garanti que sous le nœud 'intra' — 'finale' peut
    être créé nu ({'notes': {}}, voir RNotes.py ~l.384) sans son propre
    coefficient, donc toujours lu depuis 'intra' pour un cours donné.

    Intra et Final ne sont jamais fusionnés (confirmé via RPromus.py plus
    tôt dans cette session) — deux moyennes pondérées séparées, jamais une
    moyenne combinée."""
    if isinstance(data_etudiant, str):
        parse_data = json.loads(data_etudiant)
    else:
        parse_data = data_etudiant or {}

    session_data = parse_data.get(identifiant, {}).get(session, {}) if isinstance(parse_data, dict) else {}
    intra_node = session_data.get('intra', {}) if isinstance(session_data, dict) else {}
    finale_node = session_data.get('finale', {}) if isinstance(session_data, dict) else {}

    matieres = []
    notes_intra, coef_intra = [], []
    notes_finale, coef_finale = [], []

    # La clé "cours" du blob est soit un Cours.id (UUID, voir RNotes.py::
    # store_note CAS 2) soit déjà le nom du cours — les deux formes existent
    # en base selon le chemin d'écriture emprunté (voir NoteForm.vue). On
    # résout via Cours.cours_nom quand c'est un UUID connu, sinon on garde
    # la clé telle quelle (déjà un nom lisible).
    cours_nom_cache: Dict[str, str] = {}

    def resoudre_nom_cours(cours_key: str) -> str:
        if cours_key not in cours_nom_cache:
            cours_obj = db.query(Cours.cours_nom).filter(Cours.id == cours_key).first()
            cours_nom_cache[cours_key] = cours_obj[0] if cours_obj else cours_key
        return cours_nom_cache[cours_key]

    for type_matiere, cours_dict in intra_node.items():
        if not isinstance(cours_dict, dict):
            continue
        for cours, entree in cours_dict.items():
            if not isinstance(entree, dict):
                continue
            coef = to_float(entree.get('coefficients'))
            note_i = entree.get('notes', {}).get('intra')
            finale_entree = finale_node.get(type_matiere, {}).get(cours, {}) if isinstance(finale_node.get(type_matiere), dict) else {}
            note_f = finale_entree.get('notes', {}).get('finale') if isinstance(finale_entree, dict) else None

            matieres.append({
                'matiere': resoudre_nom_cours(cours),
                'coef': coef,
                'note_intra': to_float(note_i, None) if note_i is not None else None,
                'note_finale': to_float(note_f, None) if note_f is not None else None,
            })
            if note_i is not None:
                notes_intra.append(to_float(note_i))
                coef_intra.append(coef)
            if note_f is not None:
                notes_finale.append(to_float(note_f))
                coef_finale.append(coef)

    moyenne_intra = round(sum(n * c for n, c in zip(notes_intra, coef_intra)) / sum(coef_intra), 2) if sum(coef_intra) > 0 else None
    moyenne_finale = round(sum(n * c for n, c in zip(notes_finale, coef_finale)) / sum(coef_finale), 2) if sum(coef_finale) > 0 else None

    return {
        'matieres': matieres,
        'moyenne_intra': moyenne_intra,
        'moyenne_finale': moyenne_finale,
    }

def moyenne_and_place(
    classes_id: int, 
    mois: str, 
    student_list: List[Any],
    db: Session
) -> Dict[str, Any]:
    """
    Calcule les moyennes et le classement des étudiants
    
    Args:
        classes_id: ID de la classe
        mois: Mois concerné
        student_list: Liste des étudiants
        db: Session de base de données
    
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


@router.post("/imprime-bulletin")
def impression_bulletin(
    request: BulletinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Imprimer bulletin")),
):
    """
    Endpoint pour l'impression du bulletin
    
    Args:
        request: Données de la requête validées
        db: Session de base de données
    
    Returns:
        Données du bulletin formatées
    """
    try:
        # etudiant_id
        # annee_academique
        # get_notes
        if request.get_notes:
           bulletin_exists = db.query(CoursEtudiant).filter(
            CoursEtudiant.etudiant_id == request.etudiant_id,
            CoursEtudiant.annee_academique == request.annee_academique
        ).first()
        else:
            # Validation du bulletin
            bulletin_exists = db.query(CoursEtudiant).filter(
            CoursEtudiant.id == request.bulletin
        ).first()
        
        if not bulletin_exists:
            raise HTTPException(
                status_code=400,
                detail="Les informations spécifiées n'existe pas"
            )
        
        bulletin_id = request.bulletin
        mois = request.mois
        trimestre = request.Trimestre
        controle = request.Controle
        session = request.session
        
        request_data = ''
        all_headers = []
        
        # Année académique DU BULLETIN imprimé — PAS l'année active. Un
        # bulletin d'une année passée (ex: notes ajoutées après coup pour
        # 2019-2022) doit chercher ses camarades de classe dans SA PROPRE
        # année (voir data_bulletin_student plus bas) ; avec l'année active
        # à la place (comme avant), cette jointure ne trouve jamais personne
        # pour une année révolue, "result" reste vide, et le bulletin sort
        # sans moyenne de classe ni classement (voir MasBulletinPrint.py,
        # qui utilise déjà request.annee_academique — même correction ici).
        date = db.query(AnneeAcademique).filter(
            AnneeAcademique.annee_academique == bulletin_exists.annee_academique
        ).with_entities(
            AnneeAcademique.id,
            AnneeAcademique.date_debut,
            AnneeAcademique.date_fin,
            AnneeAcademique.annee_academique
        ).first()

        if not date:
            raise HTTPException(
                status_code=404,
                detail=f"Année académique introuvable pour ce bulletin ({bulletin_exists.annee_academique})."
            )
        
        if not session:
            if mois:
                if not bulletin_id or not mois:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Données manquantes. {bulletin_id} {mois}"
                    )
                
                mois_print = []
                
                if date:
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
                
                if mois not in mois_print and mois != 'all':
                    raise HTTPException(
                        status_code=400,
                        detail=f"Données manquantes. {bulletin_id} 33{mois}"
                    )
                
                request_data = mois
                all_headers = mois_print
                
            elif trimestre:
                trimestre_print = ['Trimestre I', 'Trimestre II', 'Trimestre III']
                if trimestre not in trimestre_print and trimestre != 'all':
                    raise HTTPException(
                        status_code=400,
                        detail=f"Données manquantes. {bulletin_id} 22 {trimestre}"
                    )
                request_data = trimestre
                all_headers = trimestre_print
                
            elif controle:
                controle_print = ['Contr. I', 'Contr. II', 'Contr. III', 'Contr. IV']
                if controle not in controle_print and controle != 'all':
                    raise HTTPException(
                        status_code=400,
                        detail=f"Données manquantes. {bulletin_id} 11 {controle}"
                    )
                request_data = controle
                all_headers = controle_print
                
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Données manquantes. {bulletin_id} 00{mois}"
                )
        else:
            # Niveau Universitaire, système bloc (Intra/Final) — voir
            # calculer_moyenne_session ci-dessus. request.mois est réutilisé
            # comme sélecteur de phase : 'intra', 'finale', ou 'all' (les
            # deux, affichées côte à côte, jamais fusionnées).
            if mois not in ('intra', 'finale', 'all'):
                raise HTTPException(
                    status_code=400,
                    detail="Le paramètre 'mois' doit valoir 'intra', 'finale' ou 'all' pour ce niveau."
                )
            request_data = mois
            all_headers = ['Intra', 'Finale']

        # Première requête - Récupérer les données du bulletin
        data_bulletin = db.query(
            CoursEtudiant,
            Niveau.name,
            Etudiant.nom.label('fname'),
            Etudiant.prenom.label('lname'),
            Faculte.nom.label('fac_name'),
            Classe.nom_classe,
            CoursEtudiant.annee_academique,
            CoursEtudiant.data_etudiant,
            CoursEtudiant.identifiant,
            CoursEtudiant.data_etudiant,
            CoursEtudiant.etudiant_id,
            CoursEtudiant.classe.label('classe_id'),
            Niveau.name,
        ).outerjoin(
            Faculte, Faculte.id == CoursEtudiant.faculte
        ).outerjoin(
            Niveau, Niveau.id == CoursEtudiant.niveau
        ).outerjoin(
            Classe, Classe.id == CoursEtudiant.classe
        ).outerjoin(
            Etudiant, Etudiant.id == CoursEtudiant.etudiant_id
        ).filter(
            CoursEtudiant.id == request.bulletin
        ).first()
        
        if not data_bulletin:
            raise HTTPException(
                status_code=404,
                detail="Bulletin non trouvé"
            )
        # .join(  
        #         AnneeAcademique,
        #         AnneeAcademique.id == ClasseEtudiant.annee_academique_id
        #     )
         # .outerjoin(
        #     ClasseEtudiant, ClasseEtudiant.classes_id == CoursEtudiant.classe
        # )
        data_bulletin_student = (
            db.query(
                CoursEtudiant,  # modèle principal
                Niveau.name.label("niveau"),
                Etudiant.nom.label("fname"),
                Etudiant.prenom.label("lname"),
                Faculte.nom.label("fac_name"),
                Classe.nom_classe.label("nom_classe"),
                AnneeAcademique.annee_academique.label("annee_academique"),
                CoursEtudiant.data_etudiant.label("data_etudiant"),
                CoursEtudiant.identifiant.label("identifiant"),
                CoursEtudiant.etudiant_id.label("etudiant_id"),
            )
            .join(
                ClasseEtudiant,
                and_(
                    ClasseEtudiant.classes_id == CoursEtudiant.classe,
                    ClasseEtudiant.etudiant_id == CoursEtudiant.etudiant_id,
                    ClasseEtudiant.annee_academique_id == date.id,
                    ClasseEtudiant.status == 1,
                )
            )
            .join(  
                AnneeAcademique,
                AnneeAcademique.id == ClasseEtudiant.annee_academique_id
            )
            .outerjoin(Faculte, Faculte.id == CoursEtudiant.faculte)
            .outerjoin(Niveau, Niveau.id == CoursEtudiant.niveau)
            .outerjoin(Classe, Classe.id == CoursEtudiant.classe)
            .outerjoin(Etudiant, Etudiant.id == CoursEtudiant.etudiant_id)
            .filter(
                ClasseEtudiant.classes_id == data_bulletin.classe_id,
                CoursEtudiant.annee_academique == date.annee_academique
            )
            .all()
        )

        
        # Calculer les moyennes et le classement — sans objet pour le
        # niveau bloc/session : data_bulletin_student joint ClasseEtudiant,
        # où les étudiants Universitaire/Technique ne sont jamais inscrits
        # (ils utilisent EtudiantFaculte, voir Etudiants.py) — la requête
        # renverrait toujours une liste vide, donc pas de classement de
        # classe pour ce niveau (voir calculer_moyenne_session à la place).
        session_result = None
        if session:
            session_result = calculer_moyenne_session(
                data_bulletin[9], data_bulletin[8], session, db,
            )
            data = {'result': [], 'moyenne_classe': 0}
        else:
            data = moyenne_and_place(
                data_bulletin.classe_id,
                request_data,
                data_bulletin_student,
                db
            )
        print(data_bulletin,data_bulletin.annee_academique)
        # Récupérer le profil
        profile = db.query(Profile).first()

        # Préparer la réponse
        result = {
            'data_student': {
                'cours_etudiant': data_bulletin[0],
                'niveau_name': data_bulletin[1],
                # 'name': data_bulletin[1],
                'fname': data_bulletin[2],
                'lname': data_bulletin[3],
                'fac_name': data_bulletin[4],
                'nom_classe': data_bulletin[5],
                'annee_academique': data_bulletin[6],
                'identifiant': data_bulletin[8],
                'data_etudiant':data_bulletin[9],
                'name':data_bulletin[12]
            },
            'info': profile,
            'mois': request_data,
            'session': session,
            'session_matieres': session_result['matieres'] if session_result else [],
            'moyenne_intra': session_result['moyenne_intra'] if session_result else None,
            'moyenne_finale': session_result['moyenne_finale'] if session_result else None,
            'allHeaders': all_headers,
            'moyenne_classe': data.get('moyenne_classe', 1),
            'result': data.get('result', [])
        }
        
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "one_bulletin.html",  # Votre template Jinja2
        result,
        "one_bulletin.pdf"
    )
        
    #     pdf_buffer = pdf_gen.generate_pdf_for_api(
    #     template_file="one_bulletin.html",  # Votre template Jinja2
    #     data=result,
    #     output_filename="one_bulletin.pdf"
    # )
        
        # return data
          # Retourner le PDF
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=one_bulletin.pdf"
               }
          )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage du bulletin: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur s'est produite lors de l'affichage du bulletin"
        )


# Fonction pour obtenir la session DB (à adapter selon votre configuration)
 