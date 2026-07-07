from datetime import datetime, date as date_cls
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from typing import Optional
from app.database import get_db
from app.Models.MModels import User, Professeur
from app.Models.MSystems import Personnel
from app.Models.MRelations import Pointage
from app.Schemas.SPointage import (
    PointagePersonnelListResponse,
    PointageActionSchema,
    PointageHistoriqueResponse,
    PointageHistoriqueEntry,
)
from app.dependencies.Dependencie import get_current_user, user_has_permission
from app.Helper.context import UserContext, ActionContext

router = APIRouter(prefix="/api/v1", tags=["Pointage"])

# Fixe en heure d'Haïti (UTC-5, pas de changement d'heure) plutôt que de
# dépendre de l'horloge système du poste — sur un poste de dev/test réglé
# sur un autre fuseau (ou un serveur mal configuré), datetime.now() afficherait
# une heure d'arrivée/départ fausse. L'école étant en Haïti, ce fuseau est fixe.
HAITI_TZ = ZoneInfo("America/Port-au-Prince")


def _now_haiti() -> datetime:
    return datetime.now(HAITI_TZ).replace(tzinfo=None)


def _parse_date(value: Optional[str]) -> date_cls:
    if not value:
        return _now_haiti().date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def _duree_heures(pointage: Pointage) -> Optional[float]:
    if not pointage.heure_arrivee or not pointage.heure_depart:
        return None
    delta = pointage.heure_depart - pointage.heure_arrivee
    return round(delta.total_seconds() / 3600, 2)


@router.get("/pointage/personnel", response_model=PointagePersonnelListResponse)
def list_personnel_pointage(
    date: Optional[str] = Query(None, description="Format YYYY-MM-DD, défaut aujourd'hui"),
    db: Session = Depends(get_db),
):
    # Même join que get-data-user-for-loans (RVente.py) : Professeur + Personnel
    Prof = aliased(Professeur)
    Pers = aliased(Personnel)

    users = db.query(User, Prof.nom.label("prof_nom"), Prof.prenom.label("prof_prenom"),
                      Pers.nom.label("pers_nom"), Pers.prenom.label("pers_prenom")) \
        .outerjoin(Prof, (User.userable_id == Prof.id)) \
        .outerjoin(Pers, (User.userable_id == Pers.id)) \
        .filter(User.userable_id.in_([Pers.id, Prof.id])) \
        .all()

    jour = _parse_date(date)
    pointages = {
        p.user_id: p
        for p in db.query(Pointage).filter(Pointage.date == jour).all()
    }

    result = []
    for u, prof_nom, prof_prenom, pers_nom, pers_prenom in users:
        if u.userable_type == "App\\Models\\Professeur":
            nom, prenom = prof_nom or "", prof_prenom or ""
        else:
            nom, prenom = pers_nom or "", pers_prenom or ""

        p = pointages.get(u.id)
        result.append({
            "user_id": u.id,
            "nom": nom,
            "prenom": prenom,
            "type": u.userable_type,
            "heure_arrivee": p.heure_arrivee.strftime("%H:%M") if p and p.heure_arrivee else None,
            "heure_depart": p.heure_depart.strftime("%H:%M") if p and p.heure_depart else None,
        })

    return {"data": result}


@router.post("/pointage/arrivee")
def pointer_arrivee(
    data: PointageActionSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Ajouter paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("create")

    jour = _now_haiti().date()
    pointage = db.query(Pointage).filter(
        Pointage.user_id == data.user_id, Pointage.date == jour
    ).first()

    if pointage and pointage.heure_arrivee:
        return {"success": True, "heure_arrivee": pointage.heure_arrivee.strftime("%H:%M")}

    if not pointage:
        pointage = Pointage(user_id=data.user_id, date=jour)
        db.add(pointage)

    pointage.heure_arrivee = _now_haiti()
    db.commit()
    db.refresh(pointage)
    return {"success": True, "heure_arrivee": pointage.heure_arrivee.strftime("%H:%M")}


@router.post("/pointage/depart")
def pointer_depart(
    data: PointageActionSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Ajouter paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("update")

    jour = _now_haiti().date()
    pointage = db.query(Pointage).filter(
        Pointage.user_id == data.user_id, Pointage.date == jour
    ).first()

    if not pointage or not pointage.heure_arrivee:
        raise HTTPException(status_code=422, detail="Aucun pointage d'arrivée trouvé pour aujourd'hui")

    if not pointage.heure_depart:
        pointage.heure_depart = _now_haiti()
        db.commit()
        db.refresh(pointage)

    return {"success": True, "heure_depart": pointage.heure_depart.strftime("%H:%M")}


@router.get("/pointage/historique", response_model=PointageHistoriqueResponse)
def historique_pointage(
    user_id: str = Query(...),
    mois: int = Query(..., ge=1, le=12),
    annee: int = Query(...),
    db: Session = Depends(get_db),
):
    rows = db.query(Pointage).filter(
        Pointage.user_id == user_id,
    ).all()

    entries = []
    total_heures = 0.0
    for p in rows:
        if p.date.month != mois or p.date.year != annee:
            continue
        duree = _duree_heures(p)
        if duree:
            total_heures += duree
        entries.append(PointageHistoriqueEntry(
            date=p.date.strftime("%Y-%m-%d"),
            heure_arrivee=p.heure_arrivee.strftime("%H:%M") if p.heure_arrivee else None,
            heure_depart=p.heure_depart.strftime("%H:%M") if p.heure_depart else None,
            duree_heures=duree,
        ))

    entries.sort(key=lambda e: e.date)
    return PointageHistoriqueResponse(data=entries, total_heures=round(total_heures, 2))
