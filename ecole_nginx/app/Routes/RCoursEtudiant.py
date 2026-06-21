from fastapi import APIRouter, Depends, HTTPException, Query,status
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import desc, asc, or_, func,select,  distinct, and_
import math
from babel.dates import format_date
from pydantic import BaseModel
from typing import Optional, List, Dict, Any,Union
from app.Schemas.cours_etudiant import CoursEtudiantResponse,PaginatedCoursEtudiantResponse,AddNoteRequest,EtudiantNoteData,CoursNoteData,ExamEcheanceData,AddNoteResponse,ErrorResponse,EditNoteResponse,EtudiantNoteResult,EditNoteRequest
from app.database import get_db
from app.Models.MModels import Etudiant,Niveau,Classe,Faculte,Professeur,User,Cours,AnneeAcademique
from app.Models.MFinancials import ParametrePaiement,ParamExam
from app.Models.MRelations import ClasseEtudiant,CoursEtudiant,Programme,EtudiantFaculte
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role
from app.Helper.calcule import *
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json
import logging
import locale

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Cours Etudiants"])

# GET avec pagination optionnelle et recherche
@router.get("/coursEtudiant", response_model=Union[List[CoursEtudiantResponse], PaginatedCoursEtudiantResponse])
def get_cours_etudiants(
    page: Optional[int] = Query(None, ge=1, description="Page number (optionnel)"),
    per_page: int = Query(16, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Recherche sur identifiant, nom, prénom, classe"),
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    # Utiliser les relations SQLAlchemy avec aliases pour éviter les conflits
    FaculteAlias = aliased(Faculte)
    EtudiantAlias = aliased(Etudiant)
    ClasseAlias = aliased(Classe)
    NiveauAlias = aliased(Niveau)
    ParamExamAlias = aliased(ParamExam)   
    query = (
        db.query(
            CoursEtudiant.id,
            CoursEtudiant.identifiant,
            CoursEtudiant.annee_academique,
            CoursEtudiant.classe.label("classe_id"),  # ID de la classe
            CoursEtudiant.created_at,
            CoursEtudiant.updated_at,
            
            # Relations avec alias
            EtudiantAlias.nom.label("fname"),
            EtudiantAlias.prenom.label("lname"),
            ClasseAlias.nom_classe,
            NiveauAlias.name,
            FaculteAlias.nom.label("fac_name"),
            ParamExamAlias.evaluation_par
        )
        .outerjoin(EtudiantAlias, CoursEtudiant.etudiant_id == EtudiantAlias.id)
        .outerjoin(FaculteAlias, CoursEtudiant.faculte == FaculteAlias.id)
        .outerjoin(ClasseAlias, CoursEtudiant.classe == ClasseAlias.id)
        .outerjoin(NiveauAlias, CoursEtudiant.niveau == NiveauAlias.id)
        .outerjoin(
            ParamExamAlias,
            CoursEtudiant.niveau == ParamExamAlias.niveau_id
            # Note: La condition sur annee_academique est commentée dans ton Laravel
            # and_(CoursEtudiant.annee_academique == ParamExamAlias.anneeAcademique)
        )
        .distinct()  # Comme ton Laravel
        .order_by(desc(CoursEtudiant.updated_at))
    )
    
    # Recherche textuelle (comme ton Laravel)
    if search:
        # search = f"%{search}%"
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                CoursEtudiant.identifiant.ilike(search_pattern),
                EtudiantAlias.nom.ilike(search_pattern),
                EtudiantAlias.prenom.ilike(search_pattern),
                CoursEtudiant.classe.ilike(search_pattern),
                ClasseAlias.nom_classe.ilike(search_pattern)
            )
        )
    
    # Si pas de pagination
    if page is None:
        results = query.all()
        
        data = []
        for row in results:
            data.append(CoursEtudiantResponse(
                id=row.id,
                identifiant=row.identifiant,
                fname=row.fname,  # nom de l'étudiant
                lname=row.lname,  # prénom de l'étudiant
                annee_academique=row.annee_academique,
                name=row.name,  # nom du niveau
                classe=row.nom_classe,  # ID de la classe
                nom_classe=row.nom_classe,  # nom de la classe
                evaluation_par=row.evaluation_par,
                fac_name=row.fac_name,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
        
        return data  # Retourne directement la liste
    
    # Avec pagination
    total = query.count()
    skip = (page - 1) * per_page
    
    results = query.offset(skip).limit(per_page).all()
    
    # Transformer les résultats
    data = []
    for row in results:
        data.append(CoursEtudiantResponse(
            id=row.id,
            identifiant=row.identifiant,
            fname=row.fname,
            lname=row.lname,
            annee_academique=row.annee_academique,
            name=row.name,
            classe=row.classe_id,
            nom_classe=row.nom_classe,
            evaluation_par=row.evaluation_par,
            fac_name=row.fac_name,
            created_at=row.created_at,
            updated_at=row.updated_at
        ))
    
    # Calculer la dernière page
    last_page = math.ceil(total / per_page) if total else 1
    
    # Construire les query params
    query_params = {}
    if search:
        query_params["search"] = search
    
    return PaginatedCoursEtudiantResponse(
        data=data,
        meta={
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if data else 0,
            "to": skip + len(data) if data else 0,
            "query_params": query_params
        }
    )

# GET par ID


@router.post("/coursEtudiant/{student}", response_model=CoursEtudiantResponse)
def get_cours_etudiant(cours_etudiant_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    # Utiliser les mêmes relations
    FaculteAlias = aliased(Faculte)
    EtudiantAlias = aliased(Etudiant)
    ClasseAlias = aliased(Classe)
    NiveauAlias = aliased(Niveau)
    ParamExamAlias = aliased(ParametrePaiement)
    
    result = (
        db.query(
            CoursEtudiant.id,
            CoursEtudiant.identifiant,
            CoursEtudiant.annee_academique,
            CoursEtudiant.classe.label("classe_id"),
            CoursEtudiant.created_at,
            CoursEtudiant.updated_at,
            CoursEtudiant.data_etudiant,  # Inclure le JSON si besoin
            
            EtudiantAlias.nom.label("fname"),
            EtudiantAlias.prenom.label("lname"),
            ClasseAlias.nom_classe,
            NiveauAlias.name,
            FaculteAlias.nom.label("fac_name"),
            ParamExamAlias.evaluation_par
        )
        .outerjoin(EtudiantAlias, CoursEtudiant.etudiant_id == EtudiantAlias.id)
        .outerjoin(FaculteAlias, CoursEtudiant.faculte == FaculteAlias.id)
        .outerjoin(ClasseAlias, CoursEtudiant.classe == ClasseAlias.id)
        .outerjoin(NiveauAlias, CoursEtudiant.niveau == NiveauAlias.id)
        .outerjoin(
            ParamExamAlias,
            CoursEtudiant.niveau == ParamExamAlias.niveau_id
        )
        .filter(CoursEtudiant.id == cours_etudiant_id)
        .first()
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Cours étudiant non trouvé")
    
    return CoursEtudiantResponse(
        id=result.id,
        identifiant=result.identifiant,
        fname=result.fname,
        lname=result.lname,
        annee_academique=result.annee_academique,
        name=result.name,
        classe=result.classe_id,
        nom_classe=result.nom_classe,
        evaluation_par=result.evaluation_par,
        fac_name=result.fac_name,
        created_at=result.created_at,
        updated_at=result.updated_at
        # data_etudiant=result.data_etudiant  # Décommente si tu veux inclure le JSON
    )


def generate_months_between_dates(start_date: date, end_date: date) -> Dict[str, int]:
    """Génère un dictionnaire des mois entre deux dates"""
    months = {}
    
    # Configurer la locale en français
    # try:
    #     locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    # except:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')
        # locale.setlocale(locale.LC_TIME, 'French')
    except:
        pass
    
    # from babel.dates import format_date
    current = start_date
 
    while current <= end_date:
        month_name = format_date(
            current,
            format="MMMM",
            locale="fr"
        ).capitalize()
        month_name = current.strftime('%B').capitalize()
        months[month_name] = 0
        current += relativedelta(months=1)
    # while current <= end_date:
    
    return months

@router.post("/cours-etudiant-add-note", response_model=AddNoteResponse)
async def add_note(
    request: AddNoteRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ajouter des notes pour les étudiants
    """
    if not user_has_permission(user, "Ajouter note", db):
        raise HTTPException(
            status_code=422,
            detail="Non autorisé !"
        )
    try:
        # Vérifier la permission
        if not user_has_permission(user, "Ajouter note",db):
            raise HTTPException(
                status_code=422,
                detail="Vous n'êtes pas autorisé à effectuer cette action"
            )
        
        # Vérifier que les IDs existent
        niveau_exists = db.query(select(Niveau.id).where(Niveau.id == request.niveau).exists()).scalar()
        if not niveau_exists:
            raise HTTPException(status_code=422, detail={"errors": "Le niveau spécifié n'existe pas"})
        
        cours_exists = db.query(select(Cours.id).where(Cours.id == request.cours).exists()).scalar()
        if not cours_exists:
            raise HTTPException(status_code=422, detail={"errors": "Le cours spécifié n'existe pas"})
        
        classe_exists = db.query(select(Classe.id).where(Classe.id == request.class_).exists()).scalar()
        if not classe_exists:
            raise HTTPException(status_code=422, detail={"errors": "La classe spécifiée n'existe pas"})
        
        annee_exists = db.query(select(AnneeAcademique.id).where(AnneeAcademique.id == request.annee_academique).exists()).scalar()
        if not annee_exists:
            raise HTTPException(status_code=422, detail={"errors": "L'année académique spécifiée n'existe pas"})
        
        # Récupérer le niveau
        niveau = db.query(Niveau).filter(Niveau.id == request.niveau).first()
        
        # Validation conditionnelle selon le type de niveau
        if niveau.name == "Universitaire":
            if not request.session:
                raise HTTPException(status_code=422, detail={"errors": "La session est requise pour le niveau universitaire"})
            if not request.faculte:
                raise HTTPException(status_code=422, detail={"errors": "La faculté est requise pour le niveau universitaire"})
            
            # Vérifier que la faculté existe
            faculte_exists = db.query(select(Faculte.id).where(Faculte.id == request.faculte).exists()).scalar()
            if not faculte_exists:
                raise HTTPException(status_code=422, detail={"errors": "La faculté spécifiée n'existe pas"})
        
        if niveau.name == "Technique":
            if not request.faculte:
                raise HTTPException(status_code=422, detail={"errors": "Une Option est requise pour le niveau technique"})
            
            faculte_exists = db.query(select(Faculte.id).where(Faculte.id == request.faculte).exists()).scalar()
            if not faculte_exists:
                raise HTTPException(status_code=422, detail={"errors": "L'option' spécifiée n'existe pas"})
        
        # Récupérer les paramètres d'examen
        exam_echeance = None
        if niveau.name != "Universitaire":
            exam_echeance_query = (
                select(
                    Niveau.name,
                    ParamExam.evaluation_par
                )
                .join(AnneeAcademique, AnneeAcademique.id == ParamExam.annee_academique_id)
                .join(Niveau, Niveau.id == ParamExam.niveau_id)
                .where(ParamExam.annee_academique_id == request.annee_academique)
                .where(ParamExam.niveau_id == request.niveau)
            )
            result = db.execute(exam_echeance_query).first()
            
            if not result:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": "Les paramètres des évaluations ne sont pas encore configurés"}
                )
            
            exam_echeance = ExamEcheanceData(
                name=result.name,
                evaluation_par=result.evaluation_par
            )
        
        # Récupérer les dates de l'année académique
        annee_data = db.query(
            AnneeAcademique.date_debut,
            AnneeAcademique.date_fin,
            AnneeAcademique.annee_academique
        ).filter(AnneeAcademique.id == request.annee_academique).first()
        
        # Générer les mois si l'évaluation est par mois
        month = None
        if exam_echeance and exam_echeance.evaluation_par.lower() == "mois":
            month = generate_months_between_dates(annee_data.date_debut, annee_data.date_fin)
        
        # Construire la requête pour les étudiants
        result = []
        
        if niveau.name in ["Universitaire", "Technique"]:
            query = (
                select(
                    Etudiant.id,
                    Etudiant.nom,
                    Etudiant.prenom,
                    Etudiant.identifiant,
                    AnneeAcademique.annee_academique,
                    Niveau.id.label('niveauId'),
                    Classe.nom_classe,
                    Faculte.nom.label('facName'),
                    Faculte.id.label('facId'),
                    Niveau.name,
                    EtudiantFaculte.annee_academique_id,
                    EtudiantFaculte.classes_id,
                    EtudiantFaculte.niveau_id
                )
                .select_from(EtudiantFaculte)
                .join(Etudiant, Etudiant.id == EtudiantFaculte.etudiant_id)
                .join(AnneeAcademique, AnneeAcademique.id == EtudiantFaculte.annee_academique_id)
                .join(Niveau, Niveau.id == EtudiantFaculte.niveau_id)
                .join(Classe, Classe.id == EtudiantFaculte.classes_id)
                .join(Faculte, Faculte.id == EtudiantFaculte.faculte_id)
                .join(Programme, Programme.class_ == EtudiantFaculte.classes_id)
                .where(Programme.annee_academique == request.annee_academique)
                .where(Programme.class_ == request.class_)
                .where(Programme.niveau_id == request.niveau)
                .where(EtudiantFaculte.faculte_id == request.faculte)
                .where(EtudiantFaculte.annee_academique_id == request.annee_academique)
                .where(EtudiantFaculte.classes_id == request.class_)
                .where(EtudiantFaculte.niveau_id == request.niveau)
            )
            
            # Filtrer par professeur si l'utilisateur n'est pas admin ou responsable pédagogique
            if not user_has_role(user, ["admin", "Responsable pédagogique"], db):
                query = query.where(Programme.class_ == request.class_).where(
                    Programme.professeur_id == user.userable_id
                )
            
            results = db.execute(query.distinct().order_by(Etudiant.nom)).fetchall()
            
        else:
            query = (
                select(
                    Etudiant.id,
                    Etudiant.nom,
                    Etudiant.prenom,
                    Etudiant.identifiant,
                    AnneeAcademique.annee_academique,
                    Niveau.id.label('niveauId'),
                    Classe.nom_classe,
                    Niveau.name,
                    ClasseEtudiant.annee_academique_id,
                    ClasseEtudiant.classes_id,
                    ClasseEtudiant.niveau_id
                )
                .select_from(ClasseEtudiant)
                .join(Etudiant, Etudiant.id == ClasseEtudiant.etudiant_id)
                .join(AnneeAcademique, AnneeAcademique.id == ClasseEtudiant.annee_academique_id)
                .join(Niveau, Niveau.id == ClasseEtudiant.niveau_id)
                .join(Classe, Classe.id == ClasseEtudiant.classes_id)
                .join(Programme, Programme.class_ == ClasseEtudiant.classes_id)
                .where(Programme.annee_academique == request.annee_academique)
                .where(Programme.class_ == request.class_)
                .where(Programme.niveau_id == request.niveau)
                .where(ClasseEtudiant.annee_academique_id == request.annee_academique)
                .where(ClasseEtudiant.classes_id == request.class_)
                .where(ClasseEtudiant.niveau_id == request.niveau)
                .where(ClasseEtudiant.status == 1)
            )
            
            if not user_has_role(user, ["admin", "Responsable pédagogique"], db):
                query = query.where(Programme.class_ == request.class_).where(
                    Programme.professeur_id == user.userable_id
                )
            
            results = db.execute(query.distinct().order_by(Etudiant.nom)).fetchall()
        
        # Convertir les résultats
        result = [
            EtudiantNoteData(
                id=row.id,
                nom=row.nom,
                prenom=row.prenom,
                identifiant=row.identifiant,
                annee_academique=row.annee_academique,
                niveauId=row.niveauId,
                nom_classe=row.nom_classe,
                name=row.name,
                annee_academique_id=row.annee_academique_id,
                classes_id=row.classes_id,
                niveau_id=row.niveau_id,
                facName=getattr(row, 'facName', None),
                facId=getattr(row, 'facId', None)
            )
            for row in results
        ]
        
        # Récupérer les informations du cours
        query_cours = (
            select(
                Cours.cours_nom,
                Programme.session,
                Programme.note_de_passage,
                Classe.nom_classe,
                Cours.note_de_passage.label('cours_note_passage'),
                Programme.coefficients,
                Cours.type_matiere,
                Programme.professeur_id
            )
            .select_from(Cours)
            .join(Programme, Programme.Cours_id == Cours.id)
            .join(Classe, Programme.class_ == Classe.id)
            .where(Programme.Cours_id == request.cours)
            .where(Programme.class_ == request.class_)
            .where(Cours.id == request.cours)
            .where(Programme.annee_academique == request.annee_academique)
        )
        
        if niveau.name == "Universitaire":
            query_cours = query_cours.where(Programme.Faculte_id.isnot(None)).where(
                Programme.session == request.session
            )
        
        cours_result = db.execute(query_cours).first()
        
        if not cours_result:
            raise HTTPException(
                status_code=422,
                detail={
                    "errors": {
                        "warning": f"Le cours choisi ne fait pas partie du programme. {request.session or ''}"
                    }
                }
            )
        
        cours = CoursNoteData(
            cours_nom=cours_result.cours_nom,
            session=getattr(cours_result, 'session', None),
            note_de_passage=cours_result.note_de_passage,
            nom_classe=cours_result.nom_classe,
            coefficients=cours_result.coefficients,
            type_matiere=cours_result.type_matiere,
            professeur_id=cours_result.professeur_id
        )

        if len(result) > 0 and cours:
            pass
        else:
            raise HTTPException(
                status_code=422,
                detail="Aucune donnée trouvée pour les paramètres fournis ou vous n'êtes pas autorisé."
            )
        
        # Récupérer la liste de tous les cours
        query_list_cours = (
            select(
                Cours.id,
                Cours.cours_nom,
                Classe.nom_classe,
                Programme.note_de_passage,
                Programme.coefficients,
                Programme.note_de_passage.label('programme_note_passage'),
                Cours.type_matiere,
                Programme.professeur_id
            )
            .select_from(Cours)
            .join(Programme, Programme.Cours_id == Cours.id)
            .join(Classe, Programme.class_ == Classe.id)
            .where(Programme.niveau_id == request.niveau)
            .where(Programme.class_ == request.class_)
            .where(Programme.annee_academique == request.annee_academique)
        )
        
        if niveau.name == "Universitaire":
            query_list_cours = query_list_cours.where(Programme.faculte_id.isnot(None)).where(
                Programme.session == request.session
            )
        
        list_cours_results = db.execute(query_list_cours).fetchall()
        list_cours = [
            {
                "id": row.id,
                "cours_nom": row.cours_nom,
                "nom_classe": row.nom_classe,
                "note_de_passage": row.note_de_passage,
                "coefficients": row.coefficients,
                "type_matiere": row.type_matiere,
                "professeur_id": row.professeur_id
            }
            for row in list_cours_results
        ]
        
        # Mettre à jour ou créer les enregistrements cours_etudiants
        for item in result:
            logger.info(f"Traitement étudiant: {item.id}, niveau: {item.niveauId}")
            
            cours_etudiant = db.query(CoursEtudiant).filter(
                CoursEtudiant.etudiant_id == item.id,
                CoursEtudiant.annee_academique == item.annee_academique
            ).first()
            
            if cours_etudiant:
                logger.info(f"Mise à jour cours_etudiant pour: {item.id}")
                cours_etudiant.niveau = item.niveauId
                cours_etudiant.classe = item.classes_id
            else:
                logger.info(f"Création cours_etudiant pour: {item.id}")
                new_cours_etudiant = CoursEtudiant(
                    etudiant_id=item.id,
                    identifiant=item.identifiant,
                    niveau=item.niveauId,
                    annee_academique=item.annee_academique,
                    classe=item.classes_id,
                    faculte=item.facId or "",
                    data_etudiant=json.dumps([])
                )
                db.add(new_cours_etudiant)
        
        db.commit()
        
        # Vérifier si des données ont été trouvées
        if len(result) > 0 and cours:
            return AddNoteResponse(
                datas={
                    "result": [r.dict() for r in result],
                    "cours": cours.dict(),
                    "session": request.session,
                    "examEcheance": exam_echeance.dict() if exam_echeance else None,
                    "month": month,
                    "list_cours": list_cours,
                    "annee": annee_data.annee_academique
                }
            )
        else:
            raise HTTPException(
                status_code=422,
                detail={
                    "errors": {
                        "warning": "Aucune donnée trouvée pour les paramètres fournis ou vous n'êtes pas autorisé."
                    }
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur dans add_note: {str(e)}")
        raise HTTPException(status_code=500, detail={"errors": str(e)})
# POST créer

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def parse_etudiant_data(data_etudiant: Any) -> Dict[str, Any]:
    """Parse les données JSON de l'étudiant de manière sécurisée"""
    try:
        if isinstance(data_etudiant, str):
            if not data_etudiant or data_etudiant.strip() == "":
                return {}
            return json.loads(data_etudiant)
        elif isinstance(data_etudiant, dict):
            return data_etudiant
        elif data_etudiant is None:
            return {}
        else:
            logger.warning(f"Type de données inattendu: {type(data_etudiant)}")
            return {}
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Erreur de parsing JSON: {str(e)}")
        return {}

def get_note_from_data(
    data: Dict[str, Any],
    identifiant: str,
    cours_type: str,
    cours: str,
    evaluation_examen: Optional[str]
) -> float:
    """Récupère la note depuis la structure de données imbriquée"""
    try:
        # Vérifier la structure complète
        if (
            identifiant in data and
            isinstance(data[identifiant], dict) and
            cours_type in data[identifiant] and
            isinstance(data[identifiant][cours_type], dict) and
            cours in data[identifiant][cours_type] and
            isinstance(data[identifiant][cours_type][cours], dict) and
            'notes' in data[identifiant][cours_type][cours] and
            isinstance(data[identifiant][cours_type][cours]['notes'], dict)
        ):
            # Si evaluation_examen est None, retourner 0
            if evaluation_examen is None:
                return 0.0
            
            # Récupérer la note
            if evaluation_examen in data[identifiant][cours_type][cours]['notes']:
                note_value = data[identifiant][cours_type][cours]['notes'][evaluation_examen]
                
                # Convertir en float
                if isinstance(note_value, (int, float)):
                    return float(note_value)
                elif isinstance(note_value, str):
                    try:
                        return float(note_value)
                    except ValueError:
                        logger.warning(f"Valeur de note invalide: {note_value}")
                        return 0.0
        
        return 0.0
        
    except (KeyError, TypeError, ValueError) as e:
        logger.warning(f"Erreur récupération note: {str(e)}")
        return 0.0



@router.post("/cours-etudiant-edit-note", response_model=EditNoteResponse)
async def edit_note(
    request: EditNoteRequest,
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    """
    Éditer les notes des étudiants
    
    Récupère les notes actuelles des étudiants pour un cours et une évaluation spécifiques.
    
    Args:
        request: Données de la requête contenant le cours, l'année, le type de matière et les étudiants
        
    Returns:
        Liste des étudiants avec leurs notes actuelles
        
    Raises:
        HTTPException: Si une erreur se produit lors du traitement
    """
    errors: List[str] = []
    warnings: List[str] = []
    data_etudiants: List[EtudiantNoteResult] = []
    
    # Normaliser les données
    cours_type = request.type_matiere.lower()
    evaluation_examen = request.examen
    cours = request.cours
    
    logger.info(f"Traitement de {len(request.notes)} notes pour le cours {cours}")
    
    try:
        # Traiter chaque étudiant
        for index, item in enumerate(request.notes):
            try:
                logger.debug(f"Traitement étudiant {index + 1}/{len(request.notes)}: {item.id}")
                
                # Vérifier que les données requises sont présentes
                if not item.id or not item.identifiant:
                    error_msg = f"Données manquantes pour l'étudiant à l'index {index}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                # Récupérer l'étudiant
                etudiant = db.query(CoursEtudiant).filter(
                    CoursEtudiant.etudiant_id == item.id,
                    CoursEtudiant.annee_academique == request.annee_academique
                ).first()
                
                if not etudiant:
                    error_msg = f"Étudiant avec ID {item.id} non trouvé pour l'année {request.annee_academique}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                # Parser les données de l'étudiant
                data = parse_etudiant_data(etudiant.data_etudiant)
                
                # Récupérer la note
                note = get_note_from_data(
                    data=data,
                    identifiant=item.identifiant,
                    cours_type=cours_type,
                    cours=cours,
                    evaluation_examen=evaluation_examen
                )
                
                # Log si la note est 0
                if note == 0.0:
                    warning_msg = f"Note non trouvée pour {item.identifiant} - cours: {cours}, évaluation: {evaluation_examen}"
                    warnings.append(warning_msg)
                    logger.debug(warning_msg)
                
                # Ajouter aux résultats
                data_etudiants.append(
                    EtudiantNoteResult(
                        etudiant_id=item.id,
                        note=note
                    )
                )
                
                logger.debug(f"Note trouvée pour {item.identifiant}: {note}")
                
            except Exception as e:
                error_msg = f"Erreur traitement étudiant {item.id}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg, exc_info=True)
                continue
        
        # Calculer les statistiques
        total_processed = len(request.notes)
        total_success = len(data_etudiants)
        total_errors = len(errors)
        
        logger.info(
            f"Traitement terminé - "
            f"Total: {total_processed}, "
            f"Succès: {total_success}, "
            f"Erreurs: {total_errors}"
        )
        
        # Retourner les résultats
        return EditNoteResponse(
            success=data_etudiants,
            warnings=warnings if warnings else [],
            total_processed=total_processed,
            total_success=total_success,
            total_errors=total_errors
        )
        
    except Exception as e:
        logger.error(f"Erreur critique dans edit_note: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "errors": errors if errors else ["Erreur interne du serveur"],
                "errors_": str(e),
                "details": {
                    "cours": cours,
                    "annee_academique": request.annee_academique,
                    "type_matiere": cours_type,
                    "examen": evaluation_examen
                }
            }
        )



# DELETE
@router.delete("/coursEtudiant/{cours_etudiant_id}", status_code=204)
def delete_cours_etudiant(cours_etudiant_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    cours_etudiant = db.query(CoursEtudiant).filter(
        CoursEtudiant.id == cours_etudiant_id
    ).first()
    
    if not cours_etudiant:
        raise HTTPException(status_code=404, detail="Cours étudiant non trouvé")
    
    db.delete(cours_etudiant)
    db.commit()
    
    return None

class CoursEtudiantNote(BaseModel):
    etudiant_id:str
    annee_academique: str
    mois: Optional[str] = None
    Trimestre: Optional[str] = None
    Controle: Optional[str] = None
    session: Optional[str] = None

@router.post("/student-notes")
async def get_student_note(request: CoursEtudiantNote, db: Session = Depends(get_db)): 
    try:
        bulletin_exists = db.query(CoursEtudiant).filter(
            CoursEtudiant.etudiant_id == request.etudiant_id,
            CoursEtudiant.annee_academique == request.annee_academique
        ).first()
        
        if not bulletin_exists:
            raise HTTPException(
                status_code=400,
                detail="Le bulletin spécifié n'existe pas"
            )
        
        bulletin_id = request.etudiant_id
        mois = request.mois
        trimestre = request.Trimestre
        controle = request.Controle
        session = request.session
        
        request_data = ''
        all_headers = []
        
        # Récupérer l'année académique active
        date = db.query(AnneeAcademique).filter(
            AnneeAcademique.status == 1
        ).with_entities(
            AnneeAcademique.id,
            AnneeAcademique.date_debut,
            AnneeAcademique.date_fin,
            AnneeAcademique.annee_academique
        ).first()
        
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
                
                if mois not in mois_print and mois != 'all':
                    raise HTTPException(
                        status_code=400,
                        detail=f"Données manquantesddd. {mois}"
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
        
        # Première requête - Récupérer les données du bulletin
        data_bulletin = db.query(
            CoursEtudiant,
            Niveau.name,
            Etudiant.nom.label('fname'),
            Etudiant.prenom.label('lname'),
            Faculte.nom.label('fac_name'),
            Classe.nom_classe,
            AnneeAcademique.annee_academique,
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
            ClasseEtudiant, ClasseEtudiant.classes_id == CoursEtudiant.classe
        ).outerjoin(
            Etudiant, Etudiant.id == CoursEtudiant.etudiant_id
        ).join(  
                AnneeAcademique,
                AnneeAcademique.id == ClasseEtudiant.annee_academique_id
            ).filter(
            CoursEtudiant.etudiant_id == request.etudiant_id,
            CoursEtudiant.annee_academique == request.annee_academique
        ).first()
        
        if not data_bulletin:
            raise HTTPException(
                status_code=404,
                detail="Bulletin non trouvé"
            )
        
       
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

        
        # Calculer les moyennes et le classement
        data = moyenne_and_place(
            data_bulletin.classe_id,
            request_data,
            data_bulletin_student,
            False
        )
        
        toutes_matieres = {}

        # # Ajouter toutes les matières de base et orale
        # toutes_matieres.update(donnees["base"])    # Ajoute toutes les matières de base
        # toutes_matieres.update(donnees["orale"]) 



        donnees = from_str(data_bulletin[9]).get(data_bulletin[8],"")
        toutes_matieres = {**donnees["base"], **donnees["orale"]}
        result = {
            'data_student': {
                # 'cours_etudiant': data_bulletin[0],
                'niveau_name': data_bulletin[1],
                'fname': data_bulletin[2],
                'lname': data_bulletin[3],
                'fac_name': data_bulletin[4],
                'nom_classe': data_bulletin[5],
                'annee_academique': data_bulletin[6],
                'identifiant': data_bulletin[8],
                'data_etudiant':toutes_matieres,
                # 'data_etudiant':from_str(data_bulletin[9]).get(data_bulletin[8],"").items(),
                'name':data_bulletin[12]
            },
            'bulletin_id':bulletin_exists.id,
            'mois': request_data,
            'student_value': len(data.get('result', [])),
            'allHeaders': all_headers,
            'moyenne_classe': data.get('moyenne_classe', 1),
            'result': next(
                (e for e in data.get('result', []) if e["etudiant_id"] == request.etudiant_id), 
                None
            )#data.get('result', []).find()
        }

        return result

        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage du bulletin: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur s'est produite lors de l'affichage du bulletin"
        )
    
def from_str(data_etudiant):
    if isinstance(data_etudiant, str):
        parse_data = json.loads(data_etudiant)
    else:
        parse_data = data_etudiant
    return parse_data
