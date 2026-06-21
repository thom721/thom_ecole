from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import re
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== SCHEMAS ====================

class GetPromusRequest(BaseModel):
    """Schema pour récupérer les étudiants promus"""
    data: Dict[str, str] = Field(..., description="Données de la requête")
    
    @field_validator('data')
    @classmethod
    def validate_data_fields(cls, v):
        """Valider les champs requis dans data"""
        required_fields = ['annee_academique_id', 'niveau_id', 'classes_id']
        
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Le champ '{field}' est obligatoire dans data")
        
        return v


class StorePromotionRequest(BaseModel):
    """Schema pour enregistrer la promotion d'étudiants"""
    annee_academique_id: str = Field(..., description="ID année académique actuelle")
    annee_academique_future: str = Field(..., description="ID année académique future")
    niveau_id: str = Field(..., description="ID niveau actuel")
    niveau_future: str = Field(..., description="ID niveau futur")
    classes_id: str = Field(..., description="ID classe actuelle")
    classe_future: str = Field(..., description="ID classe future")
    
    @field_validator('annee_academique_id', 'annee_academique_future')
    @classmethod
    def validate_annee_exists(cls, v, info):
        """Vérifier que l'année académique existe"""
        # La validation sera faite dans la route avec la DB
        return v
    
    @model_validator(mode='after')
    def validate_annee_sequence(self):
        """Vérifier que l'année future suit l'année actuelle"""
        # Cette validation sera faite dans la route avec accès à la DB
        return self


# ==================== FONCTIONS UTILITAIRES ====================

def get_max_coefficients_for_class(classe_id: str, db: Session) -> float:
    """
    Calculer les coefficients maximaux pondérés pour une classe
    
    Args:
        classe_id: ID de la classe
        db: Session de base de données
    
    Returns:
        Somme des coefficients pondérés maximaux
    """
    max_coeffs = {}
    
    # Récupérer tous les étudiants de la classe
    etudiants = db.query(CoursEtudiant).filter(
        CoursEtudiant.classe == classe_id
    ).all()
    
    for etudiant in etudiants:
        # Parser les données de l'étudiant
        if isinstance(etudiant.data_etudiant, str):
            notes = json.loads(etudiant.data_etudiant)
        else:
            notes = etudiant.data_etudiant
        
        if not notes or etudiant.identifiant not in notes:
            continue
        
        donnees = notes[etudiant.identifiant]
        
        # Parcourir les types (base et orale)
        for type_matiere in ['base', 'orale']:
            if type_matiere not in donnees:
                continue
            
            for matiere, detail in donnees[type_matiere].items():
                coef = float(detail.get('coefficients', 0))
                notes_list = detail.get('notes', {})
                
                # Nombre de notes
                nb_note = len(notes_list) if isinstance(notes_list, dict) else 0
                
                # Pondération par nombre de notes
                total_coef = coef * nb_note
                
                if matiere not in max_coeffs or total_coef > max_coeffs[matiere]:
                    max_coeffs[matiere] = total_coef
    
    # Retourner le total des coefficients pondérés
    return sum(max_coeffs.values())


def calculer_moyenne_generale(
    data_etudiant: Any, 
    identifiant: str, 
    max_coef: float
) -> tuple[str, float, float]:
    """
    Calculer la moyenne générale d'un étudiant
    
    Args:
        data_etudiant: Données de l'étudiant (JSON ou dict)
        identifiant: Identifiant de l'étudiant
        max_coef: Coefficient maximum pondéré
    
    Returns:
        Tuple (moyenne_formatée, total_notes, coefficient)
    """
    # Double parsing pour compatibilité Laravel
    if isinstance(data_etudiant, str):
        parse_data = json.loads(json.loads(data_etudiant))
    else:
        parse_data = data_etudiant
    
    data = parse_data.get(identifiant, {})
    
    total_notes = 0.0
    total_coefficients = 0.0
    
    # Parcourir base et orale
    for type_matiere in ['base', 'orale']:
        if type_matiere not in data:
            continue
        
        for matiere, details in data[type_matiere].items():
            notes = details.get('notes', {})
            coefficient = float(details.get('coefficients', 0))
            
            # Sommer les notes
            if isinstance(notes, dict):
                somme_notes = sum(float(note) for note in notes.values())
            elif isinstance(notes, list):
                somme_notes = sum(float(note) for note in notes)
            else:
                somme_notes = 0
            
            total_notes += somme_notes
            total_coefficients += coefficient * len(notes) if isinstance(notes, (dict, list)) else 0
    
    # Calculer la moyenne
    coeff = max_coef if max_coef > 0 else 1
    moyenne_generale = (total_notes / coeff) * 10
    
    return (f"{moyenne_generale:.2f}", total_notes, coeff)


def validate_annee_proche_fin(annee_id: str, db: Session, min_days: int = 30):
    """
    Vérifier que l'année académique est proche de sa fin
    
    Args:
        annee_id: ID de l'année académique
        db: Session de base de données
        min_days: Nombre de jours minimum avant la fin
    
    Raises:
        HTTPException: Si l'année n'est pas proche de sa fin
    """
    annee = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == annee_id
    ).first()
    
    if not annee or not annee.date_fin:
        return
    
    date_fin = datetime.strptime(str(annee.date_fin), "%Y-%m-%d")
    date_actuelle = datetime.now()
    
    jours_restants = (date_fin - date_actuelle).days
    
    if jours_restants > min_days:
        raise HTTPException(
            status_code=422,
            detail=f"L'année académique n'est pas encore proche de sa fin. Il reste {jours_restants} jours."
        )


def validate_annee_sequence(annee_actuelle_id: str, annee_future_id: str, db: Session):
    """
    Vérifier que l'année future suit immédiatement l'année actuelle
    
    Args:
        annee_actuelle_id: ID année actuelle
        annee_future_id: ID année future
        db: Session de base de données
    
    Raises:
        HTTPException: Si les années ne se suivent pas
    """
    annee_actuelle = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == annee_actuelle_id
    ).first()
    
    annee_future = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == annee_future_id
    ).first()
    
    if not annee_actuelle or not annee_future:
        return
    
    # Pattern: 2024/2025
    pattern = r'^(\d{4})/(\d{4})$'
    
    match_actuelle = re.match(pattern, annee_actuelle.annee_academique)
    match_future = re.match(pattern, annee_future.annee_academique)
    
    if not match_actuelle or not match_future:
        raise HTTPException(
            status_code=422,
            detail="Le format de l'année académique est invalide"
        )
    
    annee_fin_actuelle = int(match_actuelle.group(2))
    annee_debut_future = int(match_future.group(1))
    
    if annee_debut_future != annee_fin_actuelle:
        raise HTTPException(
            status_code=422,
            detail="L'année académique future doit immédiatement suivre l'année actuelle"
        )


def validate_classe_in_niveau(classe_id: str, niveau_id: str, db: Session):
    """
    Vérifier qu'une classe appartient à un niveau
    
    Args:
        classe_id: ID de la classe
        niveau_id: ID du niveau
        db: Session de base de données
    
    Raises:
        HTTPException: Si la classe n'appartient pas au niveau
    """
    classe = db.query(Classe).filter(Classe.id == classe_id).first()
    
    if not classe or classe.niveau_id != niveau_id:
        raise HTTPException(
            status_code=422,
            detail="La classe sélectionnée n'existe pas dans le niveau spécifié"
        )


# ==================== ROUTES ====================

@router.post("/promotion/promus")
async def get_promus(
    request: GetPromusRequest,
    db: Session = Depends(get_db)
):
    """
    Récupérer la liste des étudiants promus et en échec
    
    Retourne la liste des étudiants avec leur moyenne, note totale et statut
    """
    try:
        data = request.data
        
        # Validation de l'existence des entités
        annee = db.query(AnneeAcademique).filter(
            AnneeAcademique.id == data['annee_academique_id']
        ).first()
        
        if not annee:
            raise HTTPException(status_code=404, detail="Année académique introuvable")
        
        # Vérifier que le niveau existe
        niveau = db.query(Niveau).filter(Niveau.id == data['niveau_id']).first()
        if not niveau:
            raise HTTPException(status_code=404, detail="Niveau introuvable")
        
        # Vérifier que la classe existe
        classe = db.query(Classe).filter(Classe.id == data['classes_id']).first()
        if not classe:
            raise HTTPException(status_code=404, detail="Classe introuvable")
        
        annee_academique = annee.annee_academique
        
        # Récupérer la liste des étudiants
        student_list = db.query(
            ClassesEtudiant,
            Etudiant.id.label('etudiant_id'),
            Etudiant.nom,
            Etudiant.prenom,
            Etudiant.identifiant,
            Classe.nom_classe,
            ClassesEtudiant.classes_id,
            CoursEtudiant.data_etudiant
        ).join(
            Etudiant, Etudiant.id == ClassesEtudiant.etudiant_id
        ).join(
            Classe, Classe.id == ClassesEtudiant.classes_id
        ).join(
            CoursEtudiant, CoursEtudiant.etudiant_id == ClassesEtudiant.etudiant_id
        ).filter(
            ClassesEtudiant.classes_id == data['classes_id'],
            ClassesEtudiant.niveau_id == data['niveau_id'],
            ClassesEtudiant.annee_academique_id == data['annee_academique_id'],
            CoursEtudiant.annee_academique == annee_academique,
            ClassesEtudiant.status == 1
        ).all()
        
        data_promus = []
        max_coeffs_cache = {}
        
        for row in student_list:
            if row.data_etudiant == '"[]"':
                continue
            
            # Ignorer les classes Kindergarten
            if "Kind " in row.nom_classe:
                continue
            
            # Récupérer ou calculer le coefficient max pour cette classe
            classe_id = row.classes_id
            
            if classe_id not in max_coeffs_cache:
                max_coeffs_cache[classe_id] = get_max_coefficients_for_class(classe_id, db)
            
            max_coef = max_coeffs_cache[classe_id]
            
            # Calculer la moyenne
            results = calculer_moyenne_generale(
                row.data_etudiant,
                row.identifiant,
                max_coef
            )
            
            # Déterminer la moyenne minimale selon la classe
            m_general = 6.50 if row.nom_classe.startswith("CP") else 6.0
            
            # Ajouter aux résultats
            moyenne_float = float(results[0])
            data_promus.append({
                'id': row.etudiant_id,
                'nom': row.nom,
                'prenom': row.prenom,
                'note': results[1],
                'max': results[2],
                'moyenne': results[0],
                'status': "Succès" if moyenne_float >= m_general else "Échec"
            })
        
        return {"result": data_promus}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur dans get_promus: {str(e)}", exc_info=True)
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/promotion/store")
async def store_promotion(
    request: StorePromotionRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Enregistrer la promotion des étudiants vers l'année académique suivante
    
    Les étudiants ayant réussi sont promus dans la classe future.
    Les étudiants en échec redoublent dans la même classe.
    """
    try:
        # Validation 1: Année académique proche de sa fin (10 jours)
        validate_annee_proche_fin(request.annee_academique_id, db, min_days=10)
        
        # Validation 2: Années doivent exister
        annee_actuelle = db.query(AnneeAcademique).filter(
            AnneeAcademique.id == request.annee_academique_id
        ).first()
        
        annee_future = db.query(AnneeAcademique).filter(
            AnneeAcademique.id == request.annee_academique_future
        ).first()
        
        if not annee_actuelle or not annee_future:
            raise HTTPException(
                status_code=404,
                detail="Année académique introuvable"
            )
        
        # Validation 3: Années doivent se suivre
        validate_annee_sequence(
            request.annee_academique_id,
            request.annee_academique_future,
            db
        )
        
        # Validation 4: Classes doivent appartenir aux niveaux
        validate_classe_in_niveau(request.classes_id, request.niveau_id, db)
        validate_classe_in_niveau(request.classe_future, request.niveau_future, db)
        
        # Autorisation admin
        # AuthorizationHelper.authorize_with_admin_token(req, "Modifier etudiant")
        
        # Récupérer la liste des étudiants
        student_list = db.query(
            ClassesEtudiant,
            Etudiant.id.label('etudiant_id'),
            Classe.nom_classe,
            ClassesEtudiant.classes_id,
            CoursEtudiant.data_etudiant,
            Etudiant.identifiant
        ).join(
            Etudiant, Etudiant.id == ClassesEtudiant.etudiant_id
        ).join(
            Classe, Classe.id == ClassesEtudiant.classes_id
        ).join(
            CoursEtudiant, CoursEtudiant.etudiant_id == ClassesEtudiant.etudiant_id
        ).filter(
            ClassesEtudiant.classes_id == request.classes_id,
            ClassesEtudiant.niveau_id == request.niveau_id,
            ClassesEtudiant.annee_academique_id == request.annee_academique_id,
            ClassesEtudiant.status == 1
        ).all()
        
        max_coeffs_cache = {}
        promus_count = 0
        redoublants_count = 0
        
        for row in student_list:
            # Ignorer Kindergarten
            if "Kind " in row.nom_classe:
                continue
            
            # Récupérer coefficient max
            classe_id = row.classes_id
            if classe_id not in max_coeffs_cache:
                max_coeffs_cache[classe_id] = get_max_coefficients_for_class(classe_id, db)
            
            max_coef = max_coeffs_cache[classe_id]
            
            # Calculer moyenne
            results = calculer_moyenne_generale(
                row.data_etudiant,
                row.identifiant,
                max_coef
            )
            
            # Déterminer seuil de réussite
            m_general = 6.50 if row.nom_classe.startswith("CP") else 6.0
            moyenne_float = float(results[0])
            
            # Promouvoir ou faire redoubler
            if moyenne_float >= m_general:
                # Étudiant promu → classe future
                update_or_create_classes_etudiant(
                    db,
                    etudiant_id=row.etudiant_id,
                    annee_academique_id=request.annee_academique_future,
                    classes_id=request.classe_future,
                    niveau_id=request.niveau_future
                )
                promus_count += 1
            else:
                # Étudiant redoublant → même classe
                update_or_create_classes_etudiant(
                    db,
                    etudiant_id=row.etudiant_id,
                    annee_academique_id=request.annee_academique_future,
                    classes_id=request.classes_id,
                    niveau_id=request.niveau_id
                )
                redoublants_count += 1
        
        db.commit()
        
        return {
            "success": "Opération réussie",
            "statistics": {
                "total": promus_count + redoublants_count,
                "promus": promus_count,
                "redoublants": redoublants_count
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur dans store_promotion: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))


# ==================== FONCTION HELPER ====================

def update_or_create_classes_etudiant(
    db: Session,
    etudiant_id: str,
    annee_academique_id: str,
    classes_id: str,
    niveau_id: str
):
    """
    Créer ou mettre à jour un enregistrement classes_etudiants
    Équivalent de updateOrCreate de Laravel
    """
    # Chercher l'enregistrement existant
    existing = db.query(ClassesEtudiant).filter(
        ClassesEtudiant.etudiant_id == etudiant_id,
        ClassesEtudiant.annee_academique_id == annee_academique_id
    ).first()
    
    if existing:
        # Mettre à jour
        existing.classes_id = classes_id
        existing.niveau_id = niveau_id
        existing.status = 1
    else:
        # Créer
        new_record = ClassesEtudiant(
            etudiant_id=etudiant_id,
            annee_academique_id=annee_academique_id,
            classes_id=classes_id,
            niveau_id=niveau_id,
            status=1
        )
        db.add(new_record)


# ==================== DÉPENDANCES ====================

def get_db():
    """Dépendance pour obtenir la session de base de données"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user():
    """Récupérer l'utilisateur courant"""
    # TODO: Implémenter selon votre système d'auth
    return 1