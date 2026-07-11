from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.Schemas.SAnnulationArriere import (
    AnnulationArriereRequest,
    RevokeAnnulationArriereRequest,
    AnnulationArriereResponse,
)
from app.database import get_db
from app.Models.MModels import Etudiant, AnneeAcademique, User
from app.Models.MFinancials import AnnulationArriere, Paiement
from app.Models.MSystems import Role, ModelHasRole, Log
from app.dependencies.Dependencie import check_permission
from app.Helper.context import UserContext, ActionContext, ReasonContext
from app.Routes.RSavePaiement import _compute_previous_year_balance

logger = logging.getLogger(__name__)

router_annulation_arriere = APIRouter(prefix="/api/v1", tags=["Paiements"])


def _current_user_role_snapshot(user_id: str, db: Session) -> str:
    """Snapshot des rôles de l'utilisateur au moment de l'action — les
    rôles peuvent changer plus tard, le rapport doit rester fidèle à ce
    qu'ils étaient au moment de la dérogation."""
    roles = (
        db.query(Role.name)
        .join(ModelHasRole, ModelHasRole.role_id == Role.id)
        .filter(ModelHasRole.model_id == user_id)
        .all()
    )
    return ", ".join(r[0] for r in roles) or ""


@router_annulation_arriere.post("/annulation-arriere", response_model=AnnulationArriereResponse)
def creer_annulation_arriere(
    request: AnnulationArriereRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Annuler arriéré")),
):
    """Accorde une dérogation manuelle et réversible au blocage d'arriéré
    d'une année académique précédente pour un étudiant — voir
    RSavePaiement.py:_check_arrears_previous_year. Ne modifie jamais
    Paiement.paiement_details. L'étudiant et l'année sont dérivés du
    Paiement ciblé : les pages Paiement (web/Flutter) n'ont que son id,
    pas les ids étudiant/année séparément."""
    prev_paiement = db.query(Paiement).filter(Paiement.id == request.paiement_id).first()
    if not prev_paiement:
        raise HTTPException(status_code=422, detail={"errors": "Paiement introuvable"})

    etudiant = db.query(Etudiant).filter(Etudiant.id == prev_paiement.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=422, detail={"errors": "Étudiant introuvable"})

    annee = db.query(AnneeAcademique).filter(AnneeAcademique.annee_academique == prev_paiement.annee_academique).first()
    if not annee:
        raise HTTPException(status_code=422, detail={"errors": "Année académique introuvable"})

    existing_active = (
        db.query(AnnulationArriere)
        .filter(
            AnnulationArriere.etudiant_id == etudiant.id,
            AnnulationArriere.annee_academique_id == annee.id,
            AnnulationArriere.statut == "actif",
        )
        .first()
    )
    if existing_active:
        raise HTTPException(
            status_code=422,
            detail={"errors": "Une dérogation est déjà active pour cet étudiant et cette année. Annulez-la d'abord."},
        )

    if request.type_annulation == "total":
        montant_annule = _compute_previous_year_balance(prev_paiement)
        if montant_annule is None:
            raise HTTPException(
                status_code=422,
                detail={"errors": "Impossible de calculer automatiquement le solde restant. Utilisez un montant précis."},
            )
    else:
        montant_annule = request.montant_annule

    row = AnnulationArriere(
        etudiant_id=etudiant.id,
        annee_academique_id=annee.id,
        annee_academique=annee.annee_academique,
        type_annulation=request.type_annulation,
        montant_annule=montant_annule,
        ordonne_par=request.ordonne_par,
        ordonne_par_fonction=request.ordonne_par_fonction,
        executant_user_id=current_user.id,
        executant_nom=current_user.username or current_user.email,
        executant_role=_current_user_role_snapshot(current_user.id, db),
        raison=request.raison,
        contrat_accepte=request.contrat_accepte,
        statut="actif",
    )

    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("Dérogation d'arriéré accordée")
    ReasonContext.set_reason(request.raison)
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
        # Journalisation explicite (pas seulement via ObservableMixin) —
        # cette action doit être auditable de façon fiable, voir la note
        # dans revoquer_annulation_arriere() ci-dessous pour le pourquoi.
        db.add(Log(
            action="Dérogation d'arriéré accordée",
            user_id=current_user.id,
            model_type="AnnulationArriere",
            model_id=row.id,
            new_values={
                "etudiant_id": row.etudiant_id,
                "annee_academique": row.annee_academique,
                "montant_annule": float(row.montant_annule),
                "ordonne_par": f"{row.ordonne_par} ({row.ordonne_par_fonction})",
            },
            reason=request.raison,
        ))
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur création dérogation d'arriéré: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": f"Erreur interne : {str(e)}"})

    return _to_response(row)


@router_annulation_arriere.post("/annulation-arriere/{annulation_id}/annuler", response_model=AnnulationArriereResponse)
def revoquer_annulation_arriere(
    annulation_id: str,
    request: RevokeAnnulationArriereRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Annuler arriéré")),
):
    """Révoque une dérogation active — rétablit immédiatement le blocage
    d'arriéré pour cet étudiant et cette année (l'historique de paiement
    original n'a jamais été touché, rien à restaurer de ce côté)."""
    row = db.query(AnnulationArriere).filter(AnnulationArriere.id == annulation_id).first()
    if not row:
        raise HTTPException(status_code=404, detail={"errors": "Dérogation introuvable"})
    if row.statut != "actif":
        raise HTTPException(status_code=422, detail={"errors": "Cette dérogation n'est plus active"})

    row.statut = "annule"
    row.annule_le = datetime.utcnow()
    row.annule_par_user_id = current_user.id
    row.annule_raison = request.raison

    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("Dérogation d'arriéré révoquée")
    ReasonContext.set_reason(request.raison)
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
        # Journalisation explicite plutôt que de compter uniquement sur
        # ObservableMixin : vérifié que la session dédiée de l'observateur
        # (créée une fois au démarrage via register_observers(), voir
        # app/Models/observable.py) est distincte de la session de chaque
        # requête (app/database.py:get_db crée une session neuve à chaque
        # fois) — son log_activity() fait juste self.db.add(...) sans
        # commit() (pour éviter le ResourceClosedError déjà corrigé), ce qui
        # ne persiste de façon fiable que si cette session dédiée est
        # commit ailleurs. Pour une action financière auditée, on ne prend
        # pas ce risque : log explicite, sur la session de la requête.
        db.add(Log(
            action="Dérogation d'arriéré révoquée",
            user_id=current_user.id,
            model_type="AnnulationArriere",
            model_id=row.id,
            new_values={"statut": "annule"},
            reason=request.raison,
        ))
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur révocation dérogation d'arriéré: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": f"Erreur interne : {str(e)}"})

    return _to_response(row)


@router_annulation_arriere.get("/annulation-arriere", response_model=list[AnnulationArriereResponse])
def lister_annulations_arriere(
    paiement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Annuler arriéré")),
):
    """Liste les dérogations (actives et révoquées) pour l'étudiant/année du
    Paiement donné, pour que le bouton par ligne sache proposer 'Créer' ou
    'Annuler la dérogation active' avec son résumé."""
    paiement = db.query(Paiement).filter(Paiement.id == paiement_id).first()
    if not paiement:
        raise HTTPException(status_code=422, detail={"errors": "Paiement introuvable"})
    rows = (
        db.query(AnnulationArriere)
        .filter(
            AnnulationArriere.etudiant_id == paiement.etudiant_id,
            AnnulationArriere.annee_academique == paiement.annee_academique,
        )
        .order_by(AnnulationArriere.created_at.desc())
        .all()
    )
    return [_to_response(r) for r in rows]


def _to_response(row: AnnulationArriere) -> AnnulationArriereResponse:
    return AnnulationArriereResponse(
        id=row.id,
        etudiant_id=row.etudiant_id,
        annee_academique_id=row.annee_academique_id,
        annee_academique=row.annee_academique,
        type_annulation=row.type_annulation,
        montant_annule=float(row.montant_annule),
        ordonne_par=row.ordonne_par,
        ordonne_par_fonction=row.ordonne_par_fonction,
        executant_nom=row.executant_nom,
        executant_role=row.executant_role,
        raison=row.raison,
        statut=row.statut,
        annule_le=row.annule_le.isoformat() if row.annule_le else None,
        annule_raison=row.annule_raison,
        created_at=row.created_at.isoformat() if row.created_at else None,
    )
