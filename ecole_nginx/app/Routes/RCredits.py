# app/Routes/RCredits.py — système à crédits (niveau "Universitaire"
# uniquement, voir app/Models/MCredits.py et app/Helper/credits.py).
#
# Fichier séparé de RCoursEtudiant.py (entièrement construit autour du blob
# JSON CoursEtudiant du système par année) : ce sous-système est
# relationnel avec de vraies FK, une stratégie de stockage différente qui
# ne doit pas se mélanger avec le flux existant.

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Literal

from app.database import get_db
from app.Models.MModels import User, Etudiant, Cours, AnneeAcademique
from app.Models.MRelations import Programme, EtudiantFaculte
from app.Models.MCredits import CoursPrerequis, CoursInscription
from app.Helper.credits import require_universitaire_actif, resume_progres_etudiant
from app.Helper.audit_log import log_action
from app.Helper.elearning_grades_client import fetch_devoirs_grades
from app.dependencies.Dependencie import (
    get_current_user, check_permission, require_role, user_has_permission, user_has_role, validate_exists,
)


def _est_lui_meme(current_user: User, etudiant_id: str) -> bool:
    """True si `current_user` EST l'étudiant `etudiant_id` (compte de
    connexion polymorphique User→Etudiant, voir Etudiant.user dans
    MModels.py) — permet le libre-service (inscription, consultation de ses
    propres notes/progrès) sans exiger les permissions réservées au
    personnel (Ajouter/Voir inscription cours)."""
    return current_user.userable_type == "App\\Models\\Etudiant" and current_user.userable_id == etudiant_id

router = APIRouter(prefix="/api/v1", tags=["Crédits Universitaires"])


# ============================================================================
# Prérequis
# ============================================================================

class CoursPrerequisOut(BaseModel):
    id: str
    cours_id: str
    prerequis_cours_id: str
    prerequis_cours_nom: Optional[str] = None

    class Config:
        from_attributes = True


class CoursPrerequisIn(BaseModel):
    prerequis_cours_id: str


def _get_cours_ou_404(cours_id: str, db: Session) -> Cours:
    cours = db.query(Cours).filter(Cours.id == cours_id).first()
    if not cours:
        raise HTTPException(status_code=422, detail="Cours introuvable")
    return cours


@router.get("/cours/{cours_id}/prerequis", response_model=list[CoursPrerequisOut])
def list_prerequis(cours_id: str, db: Session = Depends(get_db)):
    cours = _get_cours_ou_404(cours_id, db)
    require_universitaire_actif(db, niveau_id=cours.niveau_id)
    rows = db.query(CoursPrerequis).filter(CoursPrerequis.cours_id == cours_id).all()
    return [
        CoursPrerequisOut(
            id=r.id, cours_id=r.cours_id, prerequis_cours_id=r.prerequis_cours_id,
            prerequis_cours_nom=r.prerequis.cours_nom if r.prerequis else None,
        )
        for r in rows
    ]


@router.post("/cours/{cours_id}/prerequis", response_model=CoursPrerequisOut, status_code=status.HTTP_201_CREATED)
def add_prerequis(
    cours_id: str,
    payload: CoursPrerequisIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Modifier cours")),
):
    if cours_id == payload.prerequis_cours_id:
        raise HTTPException(status_code=422, detail="Un cours ne peut pas être son propre prérequis")

    cours = _get_cours_ou_404(cours_id, db)
    require_universitaire_actif(db, niveau_id=cours.niveau_id)
    validate_exists(Cours, Cours.id, db, payload.prerequis_cours_id)

    exists = db.query(CoursPrerequis).filter(
        CoursPrerequis.cours_id == cours_id,
        CoursPrerequis.prerequis_cours_id == payload.prerequis_cours_id,
    ).first()
    if exists:
        raise HTTPException(status_code=422, detail="Ce prérequis existe déjà")

    prerequis = CoursPrerequis(cours_id=cours_id, prerequis_cours_id=payload.prerequis_cours_id)
    db.add(prerequis)
    db.commit()
    db.refresh(prerequis)
    return CoursPrerequisOut(
        id=prerequis.id, cours_id=prerequis.cours_id, prerequis_cours_id=prerequis.prerequis_cours_id,
        prerequis_cours_nom=prerequis.prerequis.cours_nom if prerequis.prerequis else None,
    )


@router.delete("/cours/{cours_id}/prerequis/{prerequis_cours_id}", status_code=status.HTTP_200_OK)
def delete_prerequis(
    cours_id: str,
    prerequis_cours_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Modifier cours")),
):
    cours = _get_cours_ou_404(cours_id, db)
    require_universitaire_actif(db, niveau_id=cours.niveau_id)

    prerequis = db.query(CoursPrerequis).filter(
        CoursPrerequis.cours_id == cours_id,
        CoursPrerequis.prerequis_cours_id == prerequis_cours_id,
    ).first()
    if not prerequis:
        raise HTTPException(status_code=404, detail="Prérequis non trouvé")
    db.delete(prerequis)
    db.commit()
    return {"success": "Prérequis retiré"}


# ============================================================================
# Inscriptions
# ============================================================================

class CoursInscriptionIn(BaseModel):
    etudiant_id: str
    cours_id: str
    annee_academique_id: str
    programme_id: Optional[str] = None
    override_prerequisite: bool = False
    override_max_tentatives: bool = False


class CoursInscriptionOut(BaseModel):
    id: str
    etudiant_id: str
    cours_id: str
    annee_academique_id: str
    programme_id: Optional[str] = None
    credits: float
    note_intra: Optional[float] = None
    note_finale: Optional[float] = None
    # Note combinée (note_intra pondérée par Cours.poids_intra_percent +
    # note_finale) — c'est elle qui pilote statut/credits_obtenus/GPA.
    note_globale: Optional[float] = None
    credits_obtenus: Optional[float] = None
    statut: str
    # Contribution des devoirs gérés côté elearning-iusth, en pourcentage,
    # séparée par phase comme le système bloc (voir Helper/
    # elearning_grades_client.py) — None si l'intégration n'est pas
    # active, si l'inscription n'a pas de programme_id, ou si l'étudiant
    # n'a pas d'email de corrélation.
    note_devoirs_intra: Optional[float] = None
    note_devoirs_finale: Optional[float] = None

    class Config:
        from_attributes = True


def _effective_credits(cours: Cours, programme: Optional[Programme]) -> float:
    if programme is not None and programme.credits is not None:
        return float(programme.credits)
    if cours.credits is not None:
        return float(cours.credits)
    raise HTTPException(status_code=422, detail=f"Aucun crédit défini pour le cours '{cours.cours_nom}'")


@router.post("/credits/inscriptions", response_model=CoursInscriptionOut, status_code=status.HTTP_201_CREATED)
def creer_inscription(
    payload: CoursInscriptionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Libre-service : un étudiant peut s'inscrire lui-même (soumis aux mêmes
    # règles — niveau actif, pas déjà inscrit, prérequis, limite de reprises
    # — rien n'est assoupli sur le fond, juste sur qui peut déclencher
    # l'inscription). Le personnel garde besoin de la permission dédiée pour
    # inscrire N'IMPORTE QUEL étudiant.
    if not _est_lui_meme(current_user, payload.etudiant_id) and not user_has_permission(current_user, "Ajouter inscription cours", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorisé à inscrire cet étudiant")

    etudiant = db.query(Etudiant).filter(Etudiant.id == payload.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=422, detail="Etudiant introuvable")
    cours = db.query(Cours).filter(Cours.id == payload.cours_id).first()
    if not cours:
        raise HTTPException(status_code=422, detail="Cours introuvable")
    if not db.query(AnneeAcademique).filter(AnneeAcademique.id == payload.annee_academique_id).first():
        raise HTTPException(status_code=422, detail="Année académique introuvable")

    # Le picker d'étudiant (POST /live-student) cherche dans toute l'école,
    # pas seulement Universitaire (voir plan Épic 24) — on vérifie donc ici
    # que l'étudiant appartient bien au niveau du cours visé, pour ne
    # jamais inscrire un étudiant K-12/Technique à un cours universitaire
    # par erreur de sélection.
    if not db.query(EtudiantFaculte).filter(
        EtudiantFaculte.etudiant_id == payload.etudiant_id,
        EtudiantFaculte.niveau_id == cours.niveau_id,
    ).first():
        raise HTTPException(status_code=422, detail="Cet étudiant n'appartient pas au niveau de ce cours")

    programme = None
    if payload.programme_id:
        programme = db.query(Programme).filter(Programme.id == payload.programme_id).first()
        if not programme:
            raise HTTPException(status_code=422, detail="Programme introuvable")

    require_universitaire_actif(db, niveau_id=cours.niveau_id)

    exists = db.query(CoursInscription).filter(
        CoursInscription.etudiant_id == payload.etudiant_id,
        CoursInscription.cours_id == payload.cours_id,
        CoursInscription.annee_academique_id == payload.annee_academique_id,
    ).first()
    if exists:
        raise HTTPException(status_code=422, detail="Cet étudiant est déjà inscrit à ce cours pour cette année")

    # Blocage automatique au-delà du nombre de reprises autorisées
    # (Cours.reprises_max, structurel — pas une config par offre) : compte
    # les tentatives déjà échouées sur CE cours, toutes années confondues.
    if cours.reprises_max is not None:
        echecs = db.query(CoursInscription).filter(
            CoursInscription.etudiant_id == payload.etudiant_id,
            CoursInscription.cours_id == payload.cours_id,
            CoursInscription.statut == "echoue",
        ).count()
        if echecs >= cours.reprises_max:
            if payload.override_max_tentatives:
                if not user_has_role(current_user, ["admin", "Responsable pédagogique"], db):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Seul un administrateur ou responsable pédagogique peut ignorer la limite de reprises",
                    )
                log_action(
                    db, current_user.id, "override_max_tentatives", "Cours", cours.id,
                    new_values={"etudiant_id": payload.etudiant_id, "echecs": echecs, "reprises_max": cours.reprises_max},
                    reason="Limite de reprises ignorée à l'inscription",
                )
            else:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Le nombre maximum de reprises ({cours.reprises_max}) pour le cours "
                        f"'{cours.cours_nom}' est atteint pour cet étudiant."
                    ),
                )

    if payload.override_prerequisite:
        if not user_has_role(current_user, ["admin", "Responsable pédagogique"], db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seul un administrateur ou responsable pédagogique peut ignorer les prérequis",
            )
    else:
        prerequis_rows = db.query(CoursPrerequis).filter(CoursPrerequis.cours_id == payload.cours_id).all()
        noms_manquants = []
        for pr in prerequis_rows:
            # 'en_cours' accepté (pas seulement 'valide') : inscription
            # simultanée autorisée pendant qu'un prérequis est en cours —
            # aucune conséquence rétroactive si ce prérequis échoue ensuite
            # (simplification assumée, pas de désinscription automatique).
            validee = db.query(CoursInscription).filter(
                CoursInscription.etudiant_id == payload.etudiant_id,
                CoursInscription.cours_id == pr.prerequis_cours_id,
                CoursInscription.statut.in_(("valide", "en_cours")),
            ).first()
            if not validee:
                noms_manquants.append(pr.prerequis.cours_nom if pr.prerequis else pr.prerequis_cours_id)
        if noms_manquants:
            raise HTTPException(
                status_code=422,
                detail={"errors": {"prerequis": [
                    f"Le cours '{cours.cours_nom}' nécessite d'avoir validé au préalable : {', '.join(noms_manquants)}"
                ]}},
            )

    inscription = CoursInscription(
        etudiant_id=payload.etudiant_id,
        cours_id=payload.cours_id,
        programme_id=payload.programme_id,
        annee_academique_id=payload.annee_academique_id,
        niveau_id=cours.niveau_id,
        credits=_effective_credits(cours, programme),
        statut="en_cours",
    )
    db.add(inscription)
    db.commit()
    db.refresh(inscription)

    if payload.override_prerequisite:
        log_action(
            db, current_user.id, "override_prerequisite", "CoursInscription", inscription.id,
            new_values={"cours_id": payload.cours_id, "etudiant_id": payload.etudiant_id},
            reason="Prérequis ignoré à l'inscription",
        )

    return inscription


class NoteCreditsIn(BaseModel):
    phase: Literal['intra', 'finale']
    note: float


@router.put("/credits/inscriptions/{inscription_id}/note", response_model=CoursInscriptionOut)
def saisir_note_credits(
    inscription_id: str,
    payload: NoteCreditsIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin', 'Responsable pédagogique', 'teacher'])),
):
    """Intra et Final sont deux notes distinctes (voir plan Épic 24, même
    principe que RNotes.py::store_note CAS 2 côté système bloc) : Final
    exige qu'Intra existe déjà, et seule la saisie de Final déclenche la
    décision valide/échoué (note_globale, pondérée par
    Cours.poids_intra_percent — il n'existe aucun précédent de combinaison
    automatique Intra/Final dans le système bloc, cette formule est
    propre au système à crédits)."""
    if not user_has_permission(current_user, "Ajouter note", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorisé à saisir une note")

    inscription = db.query(CoursInscription).filter(CoursInscription.id == inscription_id).first()
    if not inscription:
        raise HTTPException(status_code=404, detail="Inscription non trouvée")
    require_universitaire_actif(db, niveau_id=inscription.niveau_id)

    cours = db.query(Cours).filter(Cours.id == inscription.cours_id).first()

    if payload.phase == 'intra':
        inscription.note_intra = payload.note
    else:
        if inscription.note_intra is None:
            raise HTTPException(status_code=422, detail="Vous devez d'abord enregistrer la note Intra.")
        inscription.note_finale = payload.note
        poids_intra = float(cours.poids_intra_percent) / 100 if cours and cours.poids_intra_percent is not None else 0.5
        note_globale = float(inscription.note_intra) * poids_intra + payload.note * (1 - poids_intra)
        inscription.note_globale = note_globale

        seuil = float(cours.note_de_passage) if cours and cours.note_de_passage else 0.0
        if note_globale >= seuil:
            inscription.statut = "valide"
            inscription.credits_obtenus = float(inscription.credits)
        else:
            inscription.statut = "echoue"
            inscription.credits_obtenus = 0

    db.commit()
    db.refresh(inscription)
    return inscription


@router.get("/credits/inscriptions", response_model=list[CoursInscriptionOut])
def list_inscriptions(
    etudiant_id: str = Query(...),
    annee_academique_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Libre-service : un étudiant peut consulter ses propres inscriptions
    # sans la permission réservée au personnel.
    if not _est_lui_meme(current_user, etudiant_id) and not user_has_permission(current_user, "Voir inscription cours", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorisé à consulter ces inscriptions")
    require_universitaire_actif(db)
    query = db.query(CoursInscription).filter(CoursInscription.etudiant_id == etudiant_id)
    if annee_academique_id:
        query = query.filter(CoursInscription.annee_academique_id == annee_academique_id)
    inscriptions = query.order_by(CoursInscription.created_at.asc()).all()

    # Contribution des devoirs gérés côté elearning-iusth (voir plan Épic
    # 24) — un seul appel par programme_id distinct, jamais un par ligne.
    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    devoirs_cache: dict[str, dict[str, float]] = {}

    def devoirs_for(programme_id: Optional[str]) -> dict:
        if not programme_id or not etudiant or not etudiant.email:
            return {}
        if programme_id not in devoirs_cache:
            devoirs_cache[programme_id] = fetch_devoirs_grades(programme_id)
        return devoirs_cache[programme_id].get(etudiant.email, {})

    return [
        CoursInscriptionOut(
            id=i.id, etudiant_id=i.etudiant_id, cours_id=i.cours_id,
            annee_academique_id=i.annee_academique_id, programme_id=i.programme_id,
            credits=i.credits, note_intra=i.note_intra, note_finale=i.note_finale,
            note_globale=i.note_globale, credits_obtenus=i.credits_obtenus,
            statut=i.statut,
            note_devoirs_intra=devoirs_for(i.programme_id).get("note_devoirs_intra"),
            note_devoirs_finale=devoirs_for(i.programme_id).get("note_devoirs_finale"),
        )
        for i in inscriptions
    ]


@router.get("/credits/etudiants/{etudiant_id}/progres")
def progres_etudiant(
    etudiant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Libre-service, même logique que list_inscriptions ci-dessus.
    if not _est_lui_meme(current_user, etudiant_id) and not user_has_permission(current_user, "Voir inscription cours", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorisé à consulter cette progression")
    require_universitaire_actif(db)
    validate_exists(Etudiant, Etudiant.id, db, etudiant_id)
    return resume_progres_etudiant(db, etudiant_id)
