from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.database import get_db
from app.Models.MModels import User, Professeur, Cours
from app.Models.MSystems import Personnel
from app.Models.MRelations import Programme, Pointage
from app.Models.MFinancials import Payroll, PayrollVersement, ParametrePayroll
from app.Schemas.SPayroll import (
    PayrollSchema,
    PayrollCreateSchema,
    PayrollVersementCreateSchema,
    PaginatedPayrollResponse,
)
from app.dependencies.Dependencie import get_current_user, user_has_permission
from app.Helper.context import UserContext, ActionContext

router = APIRouter(prefix="/api/v1", tags=["Payroll"])

MOIS_NUM = {
    "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4, "Mai": 5, "Juin": 6,
    "Juillet": 7, "Août": 8, "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12,
}


@router.get("/payroll", response_model=PaginatedPayrollResponse)
def index_payroll(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Payroll).options(
        joinedload(Payroll.user), joinedload(Payroll.versements)
    ).order_by(Payroll.created_at.desc())

    total = query.count()
    skip = (page - 1) * per_page
    rows = query.offset(skip).limit(per_page).all()

    return {
        "data": [PayrollSchema.from_model(p) for p in rows],
        "meta": {
            "current_page": page,
            "last_page": (total + per_page - 1) // per_page if total else 1,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if rows else 0,
            "to": skip + len(rows) if rows else 0,
        },
    }


@router.get("/payroll/bilan-mensuel")
def bilan_mensuel_professeurs(
    mois: str = Query(..., description="Nom du mois, ex. 'Janvier'"),
    annee: str = Query(...),
    db: Session = Depends(get_db),
):
    """Vue d'ensemble par mois : pour chaque professeur, son Payroll de la
    période (mois/année) s'il existe déjà — montant dû/versé/solde/statut —
    ou 'Aucun' sinon. Sert à voir d'un coup d'œil qui a déjà été traité ce
    mois-ci et qui ne l'a pas encore été."""
    professeurs = db.query(Professeur).options(joinedload(Professeur.user)).all()

    user_ids = [p.user.id for p in professeurs if p.user]
    payrolls = db.query(Payroll).filter(
        Payroll.user_id.in_(user_ids),
        Payroll.mois == mois,
        Payroll.annee == annee,
    ).all() if user_ids else []
    payroll_by_user = {p.user_id: p for p in payrolls}

    result = []
    for professeur in professeurs:
        if not professeur.user:
            continue
        payroll = payroll_by_user.get(professeur.user.id)
        montant_du = float(payroll.montant_du) if payroll and payroll.montant_du is not None else None
        remaining = float(payroll.remaining_balance) if payroll and payroll.remaining_balance is not None else None
        montant_verse = (montant_du - remaining) if montant_du is not None and remaining is not None else None
        result.append({
            "professeur_id": professeur.id,
            "nom": f"{professeur.prenom} {professeur.nom}",
            "payroll_id": payroll.id if payroll else None,
            "montant_du": montant_du,
            "montant_verse": montant_verse,
            "solde_restant": remaining,
            "statut": payroll.statut if payroll else "Aucun",
        })

    result.sort(key=lambda r: r["nom"])
    return {"data": result}


@router.get("/payroll/professeur-info")
def get_professeur_info_for_payroll(
    user_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """Résout un User (id renvoyé par get-data-user-for-loans, réutilisé
    par le dropdown employé du formulaire payroll) vers son Professeur OU
    son Personnel — le formulaire n'a que le user_id, mais cours-payroll/
    heures-pointees ont besoin du professeur_id, et l'UI a besoin de
    type_paiement/salaire_fixe pour savoir quel mode afficher. Personnel
    n'a pas de type_paiement (toujours 'fixe', pas de notion de cours/
    heures) mais peut avoir un salaire_fixe comme Professeur.

    Cas particulier — Personnel avec une "casquette enseignante" (rôle
    teacher/Enseignant, voir RAcademic.py:_sync_shadow_professeur) : cette
    personne peut avoir DEUX salaires distincts (salaire fixe Personnel +
    rémunération horaire/fixe de sa fiche Professeur liée, ex. salaire de
    base + heures supplémentaires d'enseignement). On renvoie donc les deux
    identités quand les deux existent, avec `has_linked_professeur=True` —
    au formulaire de laisser l'utilisateur choisir laquelle payer via un
    petit sélecteur, plutôt que de forcer un seul choix silencieux."""
    default = {
        "is_professeur": False,
        "salaire_fixe": None,
        "has_linked_professeur": False,
        "personnel_salaire_fixe": None,
    }
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return default

    if user.userable_type == "App\\Models\\Professeur":
        professeur = db.query(Professeur).filter(Professeur.id == user.userable_id).first()
        if not professeur:
            return default
        return {
            "is_professeur": True,
            "professeur_id": professeur.id,
            "type_paiement": professeur.type_paiement,
            "salaire_fixe": float(professeur.salaire_fixe) if professeur.salaire_fixe is not None else None,
            "has_linked_professeur": False,
            "personnel_salaire_fixe": None,
        }

    if user.userable_type == "App\\Models\\Personnel":
        personnel = db.query(Personnel).filter(Personnel.id == user.userable_id).first()
        if not personnel:
            return default

        personnel_salaire = float(personnel.salaire_fixe) if personnel.salaire_fixe is not None else None

        professeur = db.query(Professeur).filter(
            Professeur.personnel_id == personnel.id, Professeur.status == True
        ).first()
        if professeur:
            return {
                "is_professeur": True,
                "professeur_id": professeur.id,
                "type_paiement": professeur.type_paiement,
                "salaire_fixe": float(professeur.salaire_fixe) if professeur.salaire_fixe is not None else None,
                "has_linked_professeur": True,
                "personnel_salaire_fixe": personnel_salaire,
            }

        return {
            "is_professeur": False,
            "type_paiement": "fixe",
            "salaire_fixe": personnel_salaire,
            "has_linked_professeur": False,
            "personnel_salaire_fixe": personnel_salaire,
        }

    return {"is_professeur": False, "salaire_fixe": None}


@router.get("/professeur/{professeur_id}/cours-payroll")
def get_cours_payroll(
    professeur_id: str,
    annee_academique: str = Query(...),
    db: Session = Depends(get_db),
):
    """Cours enseignés par ce professeur pour l'année donnée (via Programme),
    avec le taux horaire configuré (ParametrePayroll) s'il existe — utilisé
    par le formulaire "Verser un salaire" en mode horaire."""
    rows = (
        db.query(Programme.Cours_id, Cours.cours_nom)
        .join(Cours, Cours.id == Programme.Cours_id)
        .filter(
            Programme.professeur_id == professeur_id,
            Programme.annee_academique == annee_academique,
        )
        .distinct()
        .all()
    )

    result = []
    for cours_id, cours_nom in rows:
        taux = db.query(ParametrePayroll).filter(
            ParametrePayroll.cours_id == cours_id,
            ParametrePayroll.annee_academique == annee_academique,
        ).first()
        result.append({
            "cours_id": cours_id,
            "cours_nom": cours_nom,
            "taux_horaire": float(taux.taux_horaire) if taux else None,
        })

    return {"data": result}


@router.get("/professeur/{professeur_id}/heures-pointees")
def get_heures_pointees(
    professeur_id: str,
    mois: int = Query(..., ge=1, le=12),
    annee: int = Query(...),
    db: Session = Depends(get_db),
):
    """Total d'heures pointées (Pointage) pour ce professeur sur le mois —
    affiché comme référence dans le formulaire, pas injecté automatiquement
    dans le calcul (un professeur peut enseigner plusieurs cours à des taux
    différents ; répartir ce total entre eux reste une décision manuelle)."""
    professeur = db.query(Professeur).options(joinedload(Professeur.user)).filter(
        Professeur.id == professeur_id
    ).first()
    if not professeur or not professeur.user:
        return {"total_heures": 0.0}

    rows = db.query(Pointage).filter(Pointage.user_id == professeur.user.id).all()
    total = 0.0
    for p in rows:
        if p.date.month != mois or p.date.year != annee:
            continue
        if p.heure_arrivee and p.heure_depart:
            total += (p.heure_depart - p.heure_arrivee).total_seconds() / 3600

    return {"total_heures": round(total, 2)}


@router.post("/payroll", response_model=PayrollSchema, status_code=201)
def store_payroll(
    data: PayrollCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Ajouter paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to create payroll entry")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("create")

    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employé introuvable")

    details_horaires = None
    heures_pointees_ref = None

    if data.type_calcul == "horaire":
        if not data.details_horaires:
            raise HTTPException(status_code=422, detail="Au moins un cours avec des heures est requis")
        if not data.annee_academique_id:
            raise HTTPException(status_code=422, detail="Année académique requise pour un calcul horaire")

        montant_du = Decimal("0")
        details_horaires = []
        for ligne in data.details_horaires:
            cours = db.query(Cours).filter(Cours.id == ligne.cours_id).first()
            if not cours:
                raise HTTPException(status_code=404, detail=f"Cours introuvable : {ligne.cours_id}")
            taux_param = db.query(ParametrePayroll).filter(
                ParametrePayroll.cours_id == ligne.cours_id,
                ParametrePayroll.annee_academique == data.annee_academique_id,
            ).first()
            if not taux_param:
                raise HTTPException(
                    status_code=422,
                    detail=f"Aucun taux horaire configuré pour le cours « {cours.cours_nom} » pour cette année académique",
                )
            taux = Decimal(str(taux_param.taux_horaire))
            heures = Decimal(str(ligne.heures))
            sous_total = taux * heures
            montant_du += sous_total
            details_horaires.append({
                "cours_id": cours.id,
                "cours_nom": cours.cours_nom,
                "heures": float(heures),
                "taux": float(taux),
                "sous_total": float(sous_total),
            })

        professeur = db.query(Professeur).filter(
            Professeur.id == user.userable_id
        ).first()
        mois_num = MOIS_NUM.get(data.mois)
        if professeur and professeur.user and mois_num:
            rows = db.query(Pointage).filter(Pointage.user_id == professeur.user.id).all()
            total = 0.0
            for p in rows:
                if p.date.month == mois_num and p.date.year == int(data.annee) and p.heure_arrivee and p.heure_depart:
                    total += (p.heure_depart - p.heure_arrivee).total_seconds() / 3600
            heures_pointees_ref = round(total, 2)

        montant_final = montant_du
    else:
        if not data.montant or data.montant <= 0:
            raise HTTPException(status_code=422, detail="Montant requis pour un versement à salaire fixe")
        montant_final = Decimal(str(data.montant))

    payroll = Payroll(
        user_id=data.user_id,
        montant=montant_final,
        mois=data.mois,
        annee=data.annee,
        methode_paiement=data.methode_paiement,
        statut="En attente",
        type_calcul=data.type_calcul,
        montant_du=montant_final,
        remaining_balance=montant_final,
        details_horaires=details_horaires,
        heures_pointees_ref=heures_pointees_ref,
    )
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    return PayrollSchema.from_model(payroll)


@router.post("/payroll/{payroll_id}/verser", response_model=PayrollSchema)
def verser_payroll(
    payroll_id: str,
    data: PayrollVersementCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enregistre un versement (partiel ou intégral) contre un Payroll —
    mirror exact de POST /loans/repay (RVente.py)."""
    if not user_has_permission(current_user, "Modifier paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to update payroll entry")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("update")

    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Versement introuvable")

    solde_actuel = Decimal(str(payroll.remaining_balance if payroll.remaining_balance is not None else payroll.montant_du or payroll.montant))
    montant_verse = Decimal(str(data.montant))

    if montant_verse > solde_actuel:
        raise HTTPException(status_code=422, detail="Le montant dépasse le solde restant dû")

    versement = PayrollVersement(
        payroll_id=payroll_id,
        montant=montant_verse,
        date_versement=datetime.utcnow().date(),
        methode_paiement=data.methode_paiement,
        note=data.note,
        collected_by=current_user.id,
    )
    db.add(versement)

    payroll.remaining_balance = solde_actuel - montant_verse
    if payroll.remaining_balance <= 0:
        payroll.remaining_balance = 0
        payroll.statut = "Payé"
        payroll.date_versement = datetime.utcnow()
    else:
        payroll.statut = "Partiel"

    db.commit()
    db.refresh(payroll)
    return PayrollSchema.from_model(payroll)


@router.delete("/payroll/{payroll_id}")
def delete_payroll(
    payroll_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Supprimer paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to delete payroll entry")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("delete")

    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(status_code=404, detail="Versement introuvable")

    db.delete(payroll)
    db.commit()
    return {"success": "Opération réussie"}
