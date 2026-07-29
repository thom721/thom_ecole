from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import re
import logging 
from app.database import get_db
from app.Models.MModels import Etudiant,User,Niveau,AnneeAcademique,Classe,Faculte
from app.Models.MRelations import ClasseEtudiant,EtudiantFaculte,Responsable,PieceSoumise,CoursEtudiant
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
from app.Helper.context import UserContext

logger = logging.getLogger(__name__)
 
router = APIRouter(prefix="/api/v1", tags=["Étudiants"])

# ==================== SCHEMAS ====================

class GetPromusRequest(BaseModel):
    """Schema pour récupérer les étudiants promus"""
    data: Dict[str, str] = Field(..., description="Données de la requête")
    print(data)
    @field_validator('data')
    @classmethod
    def validate_data_fields(cls, v):
        """Valider les champs requis dans data"""
        required_fields = ['annee_academique_id', 'niveau_id', 'classes_id']
        
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Le champ '{field}' est obligatoire dans data")
        
        return v

class PromotionData(BaseModel):
    annee_academique_id: str
    annee_academique_future: str # Assure-toi que ce champ est bien envoyé par le client
    niveau_id: str
    niveau_future: str
    classes_id: str
    classe_future: str


# 2. Le wrapper qui contient la clé 'data'
class GetPromusRequesttt(BaseModel):
    data: PromotionData
    @field_validator('data')
    @classmethod
    def validate_data_fields(cls, v):
        """Valider les champs requis dans data"""
        required_fields = ['annee_academique_id', 'niveau_id', 'classes_id']
        
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Le champ '{field}' est obligatoire dans data")
        
        return v


AIDE_FINANCIERE_VALEURS = {'Aucune', '1/4 Bourse', 'Démie Bourse', 'Bourse'}


class StorePromotionRequest(BaseModel):
    """Schema pour enregistrer la promotion d'étudiants"""
    annee_academique_id: str = Field(..., description="ID année académique actuelle")
    annee_academique_future: str = Field(..., description="ID année académique future")
    niveau_id: str = Field(..., description="ID niveau actuel")
    niveau_future: str = Field(..., description="ID niveau futur")
    classes_id: str = Field(..., description="ID classe actuelle")
    classe_future: str = Field(..., description="ID classe future")
    # Optionnel : {etudiant_id: nouvelle_valeur} — UNIQUEMENT les étudiants dont
    # l'aide financière change à la promotion (le client n'envoie que le
    # diff, pas la classe entière). Valeurs alignées sur Etudiant.aide_financiere
    # (voir Ajout_etudiant.vue/etudiant_detail_screen.dart pour les 4 valeurs).
    aide_financiere_updates: Optional[Dict[str, str]] = Field(
        None, description="etudiant_id -> nouvelle aide_financiere"
    )
    # Optionnel : étudiants à faire redoubler MANUELLEMENT malgré la
    # promotion automatique — pensé pour le préscolaire (jamais de moyenne à
    # calculer, "Succès" par défaut pour tous, voir _est_classe_prescolaire),
    # mais s'applique tel quel à n'importe quel étudiant du lot si besoin.
    forcer_redoublant: Optional[List[str]] = Field(
        None, description="Liste d'etudiant_id à faire redoubler malgré tout"
    )

    @field_validator('annee_academique_id', 'annee_academique_future')
    @classmethod
    def validate_annee_exists(cls, v, info):
        """Vérifier que l'année académique existe"""
        # La validation sera faite dans la route avec la DB
        return v

    @field_validator('aide_financiere_updates')
    @classmethod
    def validate_aide_financiere_values(cls, v):
        if v is None:
            return v
        invalides = set(v.values()) - AIDE_FINANCIERE_VALEURS
        if invalides:
            raise ValueError(
                f"Valeur(s) d'aide financière invalide(s) : {', '.join(sorted(invalides))}"
            )
        return v

    @model_validator(mode='after')
    def validate_annee_sequence(self):
        """Vérifier que l'année future suit l'année actuelle"""
        # Cette validation sera faite dans la route avec accès à la DB
        return self


# ==================== FONCTIONS UTILITAIRES ====================

def _est_classe_prescolaire(nom_classe: str) -> bool:
    """Convention locale de nommage (constatée en base, ex. "1ère Année Kind
    A") — pas le nom du niveau ("Prescolaire"/"Maternelle", jamais fiable :
    aucun champ ne distingue les niveaux évalués des non-évalués sur
    `Niveau`, et même la constante de seed ne s'accorde pas avec la vraie
    valeur en base). Ces classes n'ont jamais de notes : voir get_promus/
    store_promotion pour la promotion automatique qui en découle.
    """
    return "Kind " in nom_classe


def _sans_donnees_de_cours(data_etudiant: Any) -> bool:
    """True si data_etudiant (JSON brut de CoursEtudiant.data_etudiant) ne
    contient aucune donnée de cours exploitable — stocké tantôt comme dict
    (cas normal), tantôt comme liste JSON vide "[]" pour un étudiant sans
    aucun cours/note enregistré. Remplace un ancien test fragile sur la
    chaîne exacte '"[]"' (ratait toute autre variante de sérialisation
    d'une liste/valeur vide) par un vrai parsing + vérification de type.
    """
    try:
        parsed = json.loads(data_etudiant) if isinstance(data_etudiant, str) else data_etudiant
    except (TypeError, ValueError):
        return True
    return not isinstance(parsed, dict) or not parsed


def calculer_moyenne_generale(
    data_etudiant: Any,
    identifiant: str
) -> tuple[str, float, float]:
    """
    Calculer la moyenne générale d'un étudiant.

    Dénominateur propre à l'étudiant (somme de ses coefficients × nombre de
    notes réellement présentes), identique à la formule du bulletin
    (`pdf/BulletinPrint.py::calculer_moyenne_generale`, mois="all") — jusqu'à
    ce correctif, Promus utilisait à la place un dénominateur fixe par
    classe (le max observé chez n'importe quel élève de la classe), ce qui
    désynchronisait les deux moyennes dès qu'un mois était retiré à un
    étudiant précis (ex. via "Supprimer notes" pour une absence justifiée) :
    son numérateur baissait mais pas le dénominateur commun, le pénalisant
    par rapport à la moyenne recalculée affichée sur son bulletin.

    Args:
        data_etudiant: Données de l'étudiant (JSON ou dict)
        identifiant: Identifiant de l'étudiant

    Returns:
        Tuple (moyenne_formatée, total_notes, coefficient)
    """
    # Double parsing pour compatibilité Laravel
    if isinstance(data_etudiant, str):
        parse_data = json.loads(data_etudiant)#json.loads()
    else:
        parse_data = data_etudiant
    
    # data_etudiant est parfois stocké comme liste JSON vide ("[]") plutôt que
    # dict pour un étudiant sans aucune note/cours enregistré — un .get()
    # direct plantait alors avec "'list' object has no attribute 'get'"
    # (get_promus le contournait déjà via un skip fragile sur la chaîne
    # exacte '"[]"', mais store_promotion n'avait aucune protection). Traité
    # comme "aucune donnée" plutôt que planter : moyenne 0 → Échec/redoublant,
    # jamais une promotion silencieuse sur une absence de données.
    data = parse_data.get(identifiant, {}) if isinstance(parse_data, dict) else {}
    
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
    coeff = total_coefficients if total_coefficients > 0 else 1
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

@router.post("/get-promus")
async def get_promus(
    request: GetPromusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
            ClasseEtudiant,
            Etudiant.id.label('etudiant_id'),
            Etudiant.nom,
            Etudiant.prenom,
            Etudiant.identifiant,
            Etudiant.aide_financiere,
            Classe.nom_classe,
            ClasseEtudiant.classes_id,
            CoursEtudiant.data_etudiant
        ).join(
            Etudiant, Etudiant.id == ClasseEtudiant.etudiant_id
        ).join(
            Classe, Classe.id == ClasseEtudiant.classes_id
        ).outerjoin(
            # LEFT JOIN, pas INNER : un étudiant du préscolaire n'a
            # généralement AUCUNE ligne CoursEtudiant (pas de cours/notes à
            # ce niveau) — un join intérieur les excluait tous SAUF le ou les
            # rares élèves qui en avaient une par accident (symptôme
            # rapporté : "3ème Année Kind B" en a 33 en base, mais le tableau
            # Promus n'en affichait qu'1 seul). Le filtre sur
            # `annee_academique` doit rester dans la clause ON du join et
            # PAS dans le WHERE/filter() ci-dessous : un filtre WHERE sur une
            # colonne d'un LEFT JOIN redevient un INNER JOIN de fait (NULL
            # ne satisfait jamais une égalité), annulant l'effet recherché.
            CoursEtudiant,
            and_(
                CoursEtudiant.etudiant_id == ClasseEtudiant.etudiant_id,
                CoursEtudiant.annee_academique == annee_academique,
            )
        ).filter(
            ClasseEtudiant.classes_id == data['classes_id'],
            ClasseEtudiant.niveau_id == data['niveau_id'],
            ClasseEtudiant.annee_academique_id == data['annee_academique_id'],
            ClasseEtudiant.status == 1
        ).all()
        
        data_promus = []

        for row in student_list:
            # Préscolaire ("Kind " dans le nom de classe, convention locale —
            # voir _est_classe_prescolaire) : pas de notes/moyenne, jamais
            # évaluable. Auparavant complètement ignoré (`continue`), ce qui
            # laissait ces élèves bloqués indéfiniment dans la même classe —
            # ils sont maintenant inclus, "Succès" par défaut (promotion
            # automatique), sans moyenne à calculer.
            if _est_classe_prescolaire(row.nom_classe):
                data_promus.append({
                    'id': row.etudiant_id,
                    'nom': row.nom,
                    'prenom': row.prenom,
                    'note': 0,
                    'max': 0,
                    'moyenne': '-',
                    'status': "Succès",
                    'sans_evaluation': True,
                    'aide_financiere': row.aide_financiere or 'Aucune'
                })
                continue

            if _sans_donnees_de_cours(row.data_etudiant):
                continue

            # Calculer la moyenne
            results = calculer_moyenne_generale(
                row.data_etudiant,
                row.identifiant
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
                'status': "Succès" if moyenne_float >= m_general else "Échec",
                'sans_evaluation': False,
                'aide_financiere': row.aide_financiere or 'Aucune'
            })
        
        return {"result": data_promus}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur dans get_promus: {str(e)}", exc_info=True)
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/etudiant-promus-to")
async def store_promotion(
    request: StorePromotionRequest,
    req: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        
        # Récupérer la liste des étudiants — LEFT JOIN (voir get_promus pour
        # le détail) : sans ça, un étudiant du préscolaire sans aucune ligne
        # CoursEtudiant serait exclu ici aussi, et resterait bloqué dans sa
        # classe malgré la promotion automatique ajoutée pour ce cas.
        #
        # Limité à l'année SOURCE (comme get_promus) : un étudiant déjà
        # scolarisé depuis plusieurs années a des lignes CoursEtudiant pour
        # CHAQUE année passée — sans cette limite, il apparaissait plusieurs
        # fois dans la boucle ci-dessous, et chaque passage tentait de créer
        # la même ligne d'affectation future → doublon rejeté par la base
        # ("Duplicate entry ... unique_classe_etudiant", cas réel rencontré).
        student_list = db.query(
            ClasseEtudiant,
            Etudiant.id.label('etudiant_id'),
            Classe.nom_classe,
            ClasseEtudiant.classes_id,
            CoursEtudiant.data_etudiant,
            Etudiant.identifiant
        ).join(
            Etudiant, Etudiant.id == ClasseEtudiant.etudiant_id
        ).join(
            Classe, Classe.id == ClasseEtudiant.classes_id
        ).outerjoin(
            CoursEtudiant,
            and_(
                CoursEtudiant.etudiant_id == ClasseEtudiant.etudiant_id,
                CoursEtudiant.annee_academique == annee_actuelle.annee_academique,
            )
        ).filter(
            ClasseEtudiant.classes_id == request.classes_id,
            ClasseEtudiant.niveau_id == request.niveau_id,
            ClasseEtudiant.annee_academique_id == request.annee_academique_id,
            ClasseEtudiant.status == 1
        ).all()
        
        promus_count = 0
        redoublants_count = 0
        forced_redoublants = set(request.forcer_redoublant or [])
        # Filet de sécurité : un même étudiant ne doit jamais être traité
        # deux fois dans cette boucle (peu importe la cause exacte — jointure
        # qui se dédouble, doublon de données...), sinon deux tentatives de
        # créer la même ligne d'affectation future se percutent (la session
        # ne revoit pas la première tant que la transaction n'est pas
        # validée, voir SessionLocal(autoflush=False) dans database.py).
        deja_traites = set()

        for row in student_list:
            if row.etudiant_id in deja_traites:
                continue
            deja_traites.add(row.etudiant_id)

            if _est_classe_prescolaire(row.nom_classe):
                # Jamais de moyenne : promotion automatique, sauf si l'admin
                # a explicitement demandé de faire redoubler cet enfant
                # (forcer_redoublant — voir StorePromotionRequest).
                promu = row.etudiant_id not in forced_redoublants
            else:
                # Même exclusion que get_promus (étudiant sans aucune donnée
                # de cours) : laissé tel quel plutôt que basculé
                # silencieusement en "redoublant" — un étudiant qui
                # n'apparaissait pas dans le tableau de revue affiché à
                # l'admin ne doit pas être déplacé par la promotion sans que
                # personne ne l'ait vu.
                if _sans_donnees_de_cours(row.data_etudiant):
                    continue

                # Calculer moyenne
                results = calculer_moyenne_generale(
                    row.data_etudiant,
                    row.identifiant
                )

                # Déterminer seuil de réussite
                m_general = 6.50 if row.nom_classe.startswith("CP") else 6.0
                moyenne_float = float(results[0])
                promu = moyenne_float >= m_general and row.etudiant_id not in forced_redoublants

            if promu:
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

        # Aide financière (bourse) réévaluée à la promotion : appliquée dans
        # la même transaction que le déplacement de classe, sur la table
        # etudiants (Etudiant.aide_financiere) — seuls les étudiants présents
        # dans le diff envoyé par le client sont touchés, tous les autres
        # gardent leur valeur actuelle inchangée.
        aide_financiere_count = 0
        if request.aide_financiere_updates:
            # Etudiant.register_observers() (main.py) journalise automatiquement
            # toute mise à jour de ce modèle (GlobalModelObserver, voir
            # Observers/global_observer.py) et exige un user_id de contexte —
            # jamais défini jusqu'ici dans cette route (aucune autre mutation
            # d'Etudiant n'y existait avant l'aide financière), d'où "User non
            # authentifié lors du log" au premier essai réel. Même motif que
            # Etudiants.py::store_etudiant.
            UserContext.set_user_id(current_user.id)
            for etudiant_id, nouvelle_valeur in request.aide_financiere_updates.items():
                etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
                if etudiant and etudiant.aide_financiere != nouvelle_valeur:
                    etudiant.aide_financiere = nouvelle_valeur
                    db.add(etudiant)
                    aide_financiere_count += 1

        db.commit()

        return {
            "success": "Opération réussie",
            "statistics": {
                "aide_financiere_modifiee": aide_financiere_count,
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
    existing = db.query(ClasseEtudiant).filter(
        ClasseEtudiant.etudiant_id == etudiant_id,
        ClasseEtudiant.annee_academique_id == annee_academique_id
    ).first()
    
    if existing:
        # Mettre à jour
        existing.classes_id = classes_id
        existing.niveau_id = niveau_id
        existing.status = 1
    else:
        # Créer
        new_record = ClasseEtudiant(
            etudiant_id=etudiant_id,
            annee_academique_id=annee_academique_id,
            classes_id=classes_id,
            niveau_id=niveau_id,
            status=1
        )
        db.add(new_record)


 