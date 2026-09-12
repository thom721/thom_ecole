"""Export en lecture seule pour elearning-iusth (voir plan d'intégration).

Fichier volontairement séparé des routes existantes (RProgramme.py,
RAcademic.py) : gardé par une clé API partagée (require_integration_key),
pas par l'auth JWT utilisateur — un consommateur externe, pas une action
humaine. N'écrit jamais dans la base, ne modifie aucune route existante.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased
from pydantic import BaseModel
from datetime import date

from app.database import get_db
from app.Models.MModels import AnneeAcademique, Cours, Faculte, Niveau, Professeur, User, Classe, Etudiant
from app.Models.MSystems import Personnel, Role, ModelHasRole
from app.Models.MRelations import Programme, ClasseEtudiant
from app.dependencies.integration_auth import require_integration_key
from app.config.Config import settings

router = APIRouter(prefix="/api/v1/integration", tags=["integration-export"], dependencies=[Depends(require_integration_key)])


class AnneeAcademiqueOut(BaseModel):
    id: str
    label: str
    date_debut: date
    date_fin: date
    status: bool


@router.get("/annees-academiques", response_model=list[AnneeAcademiqueOut])
def list_annees_academiques(db: Session = Depends(get_db)):
    annees = db.query(AnneeAcademique).order_by(AnneeAcademique.date_debut.desc()).all()
    return [
        AnneeAcademiqueOut(id=a.id, label=a.annee_academique, date_debut=a.date_debut, date_fin=a.date_fin, status=a.status)
        for a in annees
    ]


class ProgrammeExportOut(BaseModel):
    id: str
    cours_nom: str | None = None
    faculte_nom: str | None = None
    niveau_name: str | None = None
    classe_nom: str | None = None
    classe_id: str | None = None
    session: str | None = None
    heure: str | None = None
    jours: str | None = None
    coefficients: str | None = None
    note_de_passage: str | None = None
    professeur_nom: str | None = None
    professeur_prenom: str | None = None
    professeur_email: str | None = None
    professeur_login_email: str | None = None
    annee_academique_id: str
    annee_academique_label: str | None = None
    annee_date_debut: date | None = None
    annee_date_fin: date | None = None


def resolve_professeur_login_email(db: Session, professeur: Professeur | None) -> str | None:
    """Même logique que resolve_professeur_id (Dependencie.py:149-166),
    mais dans l'autre sens : retrouver l'email de connexion réel d'un
    Professeur donné, qu'il se soit connecté directement ou via un
    Personnel portant la casquette enseignante."""
    if professeur is None:
        return None
    direct_user = (
        db.query(User)
        .filter(User.userable_type == "App\\Models\\Professeur", User.userable_id == professeur.id)
        .first()
    )
    if direct_user:
        return direct_user.email
    if professeur.personnel_id:
        personnel_user = (
            db.query(User)
            .filter(User.userable_type == "App\\Models\\Personnel", User.userable_id == professeur.personnel_id)
            .first()
        )
        if personnel_user:
            return personnel_user.email
    return None


@router.get("/programmes", response_model=list[ProgrammeExportOut])
def list_programmes(
    annee_academique_id: str = Query(..., description="AnneeAcademique.id — obligatoire, voir plan (évite les lignes orphelines)"),
    db: Session = Depends(get_db),
):
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == annee_academique_id).first()
    if annee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Année académique introuvable")

    CoursAlias = aliased(Cours)
    FaculteAlias = aliased(Faculte)
    ProfesseurAlias = aliased(Professeur)
    NiveauAlias = aliased(Niveau)
    ClasseAlias = aliased(Classe)

    rows = (
        db.query(Programme, CoursAlias, FaculteAlias, NiveauAlias, ClasseAlias, ProfesseurAlias)
        .outerjoin(CoursAlias, Programme.Cours_id == CoursAlias.id)
        .outerjoin(FaculteAlias, Programme.Faculte_id == FaculteAlias.id)
        .outerjoin(NiveauAlias, Programme.niveau_id == NiveauAlias.id)
        .outerjoin(ClasseAlias, Programme.class_ == ClasseAlias.id)
        .outerjoin(ProfesseurAlias, Programme.professeur_id == ProfesseurAlias.id)
        .filter(Programme.annee_academique == annee_academique_id)
        .all()
    )

    result = []
    for programme, cours, faculte, niveau, classe, professeur in rows:
        result.append(ProgrammeExportOut(
            id=programme.id,
            cours_nom=cours.cours_nom if cours else None,
            faculte_nom=faculte.nom if faculte else None,
            niveau_name=niveau.name if niveau else None,
            classe_nom=classe.nom_classe if classe else None,
            classe_id=programme.class_,
            session=programme.session,
            heure=programme.heure,
            jours=programme.jours,
            coefficients=programme.coefficients,
            note_de_passage=programme.note_de_passage,
            professeur_nom=professeur.nom if professeur else None,
            professeur_prenom=professeur.prenom if professeur else None,
            professeur_email=professeur.email if professeur else None,
            professeur_login_email=resolve_professeur_login_email(db, professeur),
            annee_academique_id=annee.id,
            annee_academique_label=annee.annee_academique,
            annee_date_debut=annee.date_debut,
            annee_date_fin=annee.date_fin,
        ))
    return result


def get_programme_export(db: Session, programme_id: str) -> ProgrammeExportOut | None:
    """Même requête/mêmes champs que list_programmes, mais pour un seul
    programme — utilisé par Helper/elearning_webhook.py::notify_programme_changed
    pour pousser la fiche complète en temps réel (voir plan), sans dupliquer
    la résolution des jointures cours/faculté/niveau/classe/professeur."""
    CoursAlias = aliased(Cours)
    FaculteAlias = aliased(Faculte)
    ProfesseurAlias = aliased(Professeur)
    NiveauAlias = aliased(Niveau)
    ClasseAlias = aliased(Classe)

    row = (
        db.query(Programme, CoursAlias, FaculteAlias, NiveauAlias, ClasseAlias, ProfesseurAlias)
        .outerjoin(CoursAlias, Programme.Cours_id == CoursAlias.id)
        .outerjoin(FaculteAlias, Programme.Faculte_id == FaculteAlias.id)
        .outerjoin(NiveauAlias, Programme.niveau_id == NiveauAlias.id)
        .outerjoin(ClasseAlias, Programme.class_ == ClasseAlias.id)
        .outerjoin(ProfesseurAlias, Programme.professeur_id == ProfesseurAlias.id)
        .filter(Programme.id == programme_id)
        .first()
    )
    if row is None:
        return None

    programme, cours, faculte, niveau, classe, professeur = row
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == programme.annee_academique).first()

    return ProgrammeExportOut(
        id=programme.id,
        cours_nom=cours.cours_nom if cours else None,
        faculte_nom=faculte.nom if faculte else None,
        niveau_name=niveau.name if niveau else None,
        classe_nom=classe.nom_classe if classe else None,
        classe_id=programme.class_,
        session=programme.session,
        heure=programme.heure,
        jours=programme.jours,
        coefficients=programme.coefficients,
        note_de_passage=programme.note_de_passage,
        professeur_nom=professeur.nom if professeur else None,
        professeur_prenom=professeur.prenom if professeur else None,
        professeur_email=professeur.email if professeur else None,
        professeur_login_email=resolve_professeur_login_email(db, professeur),
        annee_academique_id=programme.annee_academique,
        annee_academique_label=annee.annee_academique if annee else None,
        annee_date_debut=annee.date_debut if annee else None,
        annee_date_fin=annee.date_fin if annee else None,
    )


class ClasseExportOut(BaseModel):
    id: str
    nom_classe: str
    niveau_name: str | None = None


@router.get("/classes", response_model=list[ClasseExportOut])
def list_classes(
    annee_academique_id: str = Query(..., description="AnneeAcademique.id"),
    db: Session = Depends(get_db),
):
    """Classes ayant au moins un étudiant actif pour cette année (voir
    plan Épic 19, intégration elearning-iusth) — pas toutes les classes
    de l'établissement, seulement celles réellement pertinentes."""
    rows = (
        db.query(Classe, Niveau)
        .join(ClasseEtudiant, ClasseEtudiant.classes_id == Classe.id)
        .outerjoin(Niveau, Classe.niveau_id == Niveau.id)
        .filter(ClasseEtudiant.annee_academique_id == annee_academique_id, ClasseEtudiant.status.is_(True))
        .distinct()
        .all()
    )
    return [ClasseExportOut(id=c.id, nom_classe=c.nom_classe, niveau_name=n.name if n else None) for c, n in rows]


class EtudiantExportOut(BaseModel):
    etudiant_id: str
    identifiant: str
    code: str | None = None
    nom: str
    prenom: str
    email: str | None = None
    etudiant_login_email: str | None = None


def resolve_student_login_email(db: Session, etudiant_id: str) -> str | None:
    """Même principe que resolve_professeur_login_email (professeurs) : retrouve
    l'email de connexion réel si cet étudiant a déjà été activé via
    PATCH /active-etudiant (RAcademic.py) — User.userable_type=
    'App\\Models\\Etudiant'. Distinct de Etudiant.email (la fiche
    administrative brute, presque toujours vide en pratique)."""
    student_user = (
        db.query(User)
        .filter(User.userable_type == "App\\Models\\Etudiant", User.userable_id == etudiant_id)
        .first()
    )
    return student_user.email if student_user else None


@router.get("/classes/{classe_id}/students", response_model=list[EtudiantExportOut])
def list_classe_students(
    classe_id: str,
    annee_academique_id: str = Query(..., description="AnneeAcademique.id"),
    db: Session = Depends(get_db),
):
    """Étudiants actifs d'une classe pour une année (voir plan Épic 19).
    `email` (fiche Etudiant brute) transmis tel quel même vide — quasi
    jamais renseigné côté ecole_nginx (vérifié : 0/1270 en base).
    `etudiant_login_email` résout le vrai email de connexion si l'étudiant
    a déjà été activé via le bouton existant de la page étudiant
    ecole_nginx (PATCH /active-etudiant) — préférable à `email` quand
    disponible, l'admin elearning-iusth peut toujours le corriger."""
    rows = (
        db.query(Etudiant)
        .join(ClasseEtudiant, ClasseEtudiant.etudiant_id == Etudiant.id)
        .filter(ClasseEtudiant.classes_id == classe_id, ClasseEtudiant.annee_academique_id == annee_academique_id,
                ClasseEtudiant.status.is_(True))
        .all()
    )
    return [
        EtudiantExportOut(etudiant_id=e.id, identifiant=e.identifiant, code=e.code, nom=e.nom, prenom=e.prenom,
                           email=e.email, etudiant_login_email=resolve_student_login_email(db, e.id))
        for e in rows
    ]


class StaffCredentialOut(BaseModel):
    source_type: str  # "professeur" | "personnel"
    source_id: str
    first_name: str
    last_name: str
    login_email: str
    password_hash: str
    role_names: list[str] = []


def _resolve_role_names(db: Session, user_id: str) -> list[str]:
    """Vrais rôles RBAC de ce compte (voir plan Épic 23) — même requête que
    user_has_role() (Dependencie.py:137-147), réutilisée telle quelle plutôt
    que dupliquée."""
    rows = (
        db.query(Role.name)
        .join(ModelHasRole, ModelHasRole.role_id == Role.id)
        .filter(ModelHasRole.model_id == user_id, ModelHasRole.model_type == "App\\Models\\User")
        .all()
    )
    return [r.name for r in rows]


@router.get("/staff-credentials", response_model=list[StaffCredentialOut])
def list_staff_credentials(db: Session = Depends(get_db)):
    """Export du hash de mot de passe (voir plan Épic 22, sync des
    identifiants professeur/personnel avec elearning-iusth) — gardé par
    require_integration_key (routeur) **et** par ce garde-fou
    supplémentaire explicite, car exposer un hash est plus sensible que
    le reste de cet export en lecture seule."""
    if not settings.INTEGRATION_ALLOW_CREDENTIAL_SYNC:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Synchronisation des identifiants désactivée (INTEGRATION_ALLOW_CREDENTIAL_SYNC)")

    result: list[StaffCredentialOut] = []

    prof_rows = (
        db.query(User, Professeur)
        .join(Professeur, and_(User.userable_type == "App\\Models\\Professeur", User.userable_id == Professeur.id))
        .all()
    )
    for user, prof in prof_rows:
        result.append(StaffCredentialOut(
            source_type="professeur", source_id=prof.id, first_name=prof.prenom or "", last_name=prof.nom or "",
            login_email=user.email, password_hash=user.password, role_names=_resolve_role_names(db, user.id),
        ))

    personnel_rows = (
        db.query(User, Personnel)
        .join(Personnel, and_(User.userable_type == "App\\Models\\Personnel", User.userable_id == Personnel.id))
        .all()
    )
    for user, personnel in personnel_rows:
        result.append(StaffCredentialOut(
            source_type="personnel", source_id=personnel.id, first_name=personnel.prenom or "", last_name=personnel.nom or "",
            login_email=user.email, password_hash=user.password, role_names=_resolve_role_names(db, user.id),
        ))

    return result
