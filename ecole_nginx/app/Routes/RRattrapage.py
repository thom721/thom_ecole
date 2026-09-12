# app/Routes/RRattrapage.py — session de rattrapage pour le système par
# année (voir app/Models/MRelations.py::RattrapageSession et
# RPromus.py::store_promotion, champ rattrapage_etudiants).
#
# Réutilise calculer_moyenne_generale/update_or_create_classes_etudiant de
# RPromus.py plutôt que de les dupliquer.

import copy
import json
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MModels import User, Etudiant, AnneeAcademique, Classe
from app.Models.MRelations import RattrapageSession, CoursEtudiant
from app.Helper.elearning_webhook import notify_enrollment_changed
from app.dependencies.Dependencie import check_permission, require_role, user_has_permission
from app.Routes.RPromus import calculer_moyenne_generale, update_or_create_classes_etudiant

router = APIRouter(prefix="/api/v1", tags=["Rattrapage"])

PEDAGOGIC_ROLES = ['admin', 'Responsable pédagogique', 'teacher']


class RattrapageSessionOut(BaseModel):
    id: str
    etudiant_id: str
    annee_academique_id: str
    classes_id: str
    niveau_id: str
    matieres_a_repasser: list
    notes_rattrapage: Optional[dict] = None
    moyenne_recalculee: Optional[float] = None
    statut: str
    decision_finale: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/rattrapage", response_model=list[RattrapageSessionOut])
def list_rattrapage(
    annee_academique_id: Optional[str] = Query(None),
    classes_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PEDAGOGIC_ROLES)),
):
    query = db.query(RattrapageSession)
    if annee_academique_id:
        query = query.filter(RattrapageSession.annee_academique_id == annee_academique_id)
    if classes_id:
        query = query.filter(RattrapageSession.classes_id == classes_id)
    return query.order_by(RattrapageSession.created_at.asc()).all()


def _substituer_notes_rattrapage(data_etudiant: Any, identifiant: str, notes_rattrapage: dict) -> dict:
    """Copie data_etudiant en remplaçant, pour chaque matière présente dans
    notes_rattrapage, l'ensemble de ses notes par la seule note de
    rattrapage (le rattrapage remplace le résultat de l'année pour cette
    matière, il ne s'ajoute pas à elle) — puis renvoie une structure prête
    à repasser à calculer_moyenne_generale."""
    parsed = json.loads(data_etudiant) if isinstance(data_etudiant, str) else data_etudiant
    parsed = copy.deepcopy(parsed) if isinstance(parsed, dict) else {}

    etudiant_data = parsed.get(identifiant, {})
    for type_matiere in ['base', 'orale']:
        if type_matiere not in etudiant_data:
            continue
        for matiere, details in etudiant_data[type_matiere].items():
            if matiere in notes_rattrapage:
                details['notes'] = {'rattrapage': notes_rattrapage[matiere]}

    parsed[identifiant] = etudiant_data
    return parsed


@router.post("/rattrapage/{rattrapage_session_id}/notes", response_model=RattrapageSessionOut)
def saisir_notes_rattrapage(
    rattrapage_session_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PEDAGOGIC_ROLES)),
):
    if not user_has_permission(current_user, "Ajouter note", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non autorisé à saisir une note")

    notes = payload.get("notes")
    if not isinstance(notes, dict) or not notes:
        raise HTTPException(status_code=422, detail="'notes' ({matiere: note}) est requis")

    session = db.query(RattrapageSession).filter(RattrapageSession.id == rattrapage_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session de rattrapage non trouvée")
    if session.statut != "en_attente":
        raise HTTPException(status_code=422, detail="Cette session de rattrapage est déjà terminée")

    etudiant = db.query(Etudiant).filter(Etudiant.id == session.etudiant_id).first()
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == session.annee_academique_id).first()
    if not etudiant or not annee:
        raise HTTPException(status_code=422, detail="Étudiant ou année académique introuvable")

    cours_etudiant = db.query(CoursEtudiant).filter(
        CoursEtudiant.etudiant_id == session.etudiant_id,
        CoursEtudiant.annee_academique == annee.annee_academique,
    ).first()
    if not cours_etudiant:
        raise HTTPException(status_code=422, detail="Aucune donnée de cours trouvée pour cet étudiant/année")

    notes_cumulees = dict(session.notes_rattrapage or {})
    notes_cumulees.update(notes)

    data_substituee = _substituer_notes_rattrapage(cours_etudiant.data_etudiant, etudiant.identifiant, notes_cumulees)
    resultats = calculer_moyenne_generale(data_substituee, etudiant.identifiant)

    session.notes_rattrapage = notes_cumulees
    session.moyenne_recalculee = float(resultats[0])
    db.commit()
    db.refresh(session)
    return session


class RattrapageDecisionIn(BaseModel):
    annee_academique_future_id: str
    classe_future_id: str
    niveau_future_id: str


@router.post("/rattrapage/{rattrapage_session_id}/decision", response_model=RattrapageSessionOut)
def decision_rattrapage(
    rattrapage_session_id: str,
    payload: RattrapageDecisionIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Modifier etudiant")),
):
    session = db.query(RattrapageSession).filter(RattrapageSession.id == rattrapage_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session de rattrapage non trouvée")
    if session.statut != "en_attente":
        raise HTTPException(status_code=422, detail="Cette session de rattrapage est déjà terminée")
    if session.moyenne_recalculee is None:
        raise HTTPException(status_code=422, detail="Aucune note de rattrapage saisie pour cette session")

    classe = db.query(Classe).filter(Classe.id == session.classes_id).first()
    if not classe:
        raise HTTPException(status_code=422, detail="Classe introuvable")

    # Même seuil que RPromus.py::store_promotion (6.50 pour les classes
    # "CP", 6.0 sinon) — pas de nouvelle règle de passage configurable
    # introduite ici (hors périmètre, voir le plan).
    seuil = 6.50 if classe.nom_classe.startswith("CP") else 6.0
    succes = float(session.moyenne_recalculee) >= seuil

    if succes:
        classes_id_cible = payload.classe_future_id
        niveau_id_cible = payload.niveau_future_id
    else:
        # Échec au rattrapage → redoublement, même classe/niveau que
        # l'année évaluée (identique à la branche redoublement de
        # store_promotion), sous la nouvelle année académique.
        classes_id_cible = session.classes_id
        niveau_id_cible = session.niveau_id

    update_or_create_classes_etudiant(
        db,
        etudiant_id=session.etudiant_id,
        annee_academique_id=payload.annee_academique_future_id,
        classes_id=classes_id_cible,
        niveau_id=niveau_id_cible,
    )

    session.statut = "termine_succes" if succes else "termine_echec"
    session.decision_finale = "Succès" if succes else "Échec"
    db.commit()
    db.refresh(session)

    background_tasks.add_task(
        notify_enrollment_changed, db, payload.annee_academique_future_id,
        [{"etudiant_id": session.etudiant_id, "classes_id": classes_id_cible, "status": True}],
    )

    return session
