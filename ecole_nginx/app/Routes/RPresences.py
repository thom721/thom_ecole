from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, case
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, time
import uuid
from app.database import get_db
from app.Models.MModels import Etudiant, Classe, AnneeAcademique, User
from app.Models.MRelations import Presence, ClasseEtudiant
from app.dependencies.Dependencie import get_current_user, require_role

PRESENCE_ROLES = ['admin', 'Responsable pédagogique', 'teacher']

router = APIRouter(prefix="/api/v1", tags=["presences"])


# ══════════════════════════════════════════════════════════════════════════
#  SCHEMAS
# ══════════════════════════════════════════════════════════════════════════

class PresenceItem(BaseModel):
    etudiant_id: str
    valeur: bool          # True = présent, False = absent

class AppelCreate(BaseModel):
    classes_id: str
    annee_academique_id: str
    date_daujourdhui: date
    presences: List[PresenceItem]

class PresenceOut(BaseModel):
    id: str
    etudiant_id: str
    classes_id: str
    annee_academique_id: str
    date_daujourdhui: datetime
    valeur: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════
#  GET /api/classes/{classe_id}/etudiants
#  Retourne les élèves d'une classe pour peupler le tableau d'appel
# ══════════════════════════════════════════════════════════════════════════

@router.get("/classes/{classe_id}/etudiants")
def get_etudiants_par_classe(
    classe_id: str,
    annee_academique_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PRESENCE_ROLES))
):
    """
    Retourne la liste des étudiants inscrits dans une classe.
    Si annee_academique_id est fourni, filtre par année académique.
    """
    # query = db.query(Etudiant).filter(Etudiant.classes_id == classe_id)

    # if annee_academique_id:
    #     query = query.filter(Etudiant.annee_academique_id == annee_academique_id)

#     query = (
#     db.query(Etudiant)
#     .join(Etudiant.classes)
#     .filter(ClassesEtudiants.classe_id == classe_id)
# )
    query = (
        db.query(Etudiant)
        .join(ClasseEtudiant, ClasseEtudiant.etudiant_id == Etudiant.id)
        .filter(ClasseEtudiant.classes_id == classe_id)
    )

    if annee_academique_id:
        query = query.filter(
            ClasseEtudiant.annee_academique_id == annee_academique_id
        )

    etudiants = query.order_by(Etudiant.nom).all()

    return [
        {
            "id":         e.id,
            "nom":        e.nom,
            "prenom":     e.prenom,
            "matricule":  getattr(e, "matricule", None),
        }
        for e in etudiants
    ]

@router.get("/stats-presence-aujourdhui")
def stats_presence_aujourdhui(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PRESENCE_ROLES))
):
    today = date.today()

    start_day = datetime.combine(today, time.min)
    end_day   = datetime.combine(today, time.max)

    # 📊 Stats par classe
    query = (
        db.query(
            Classe.nom_classe.label("classe"),
            func.sum(
                case(
                    (Presence.valeur == True, 1),
                    else_=0
                )
            ).label("presents"),
            func.count(Presence.id).label("total")
        )
        .join(Classe, Classe.id == Presence.classes_id)
        .filter(Presence.date_daujourdhui.between(start_day, end_day))
        .group_by(Classe.id, Classe.nom_classe)
        .order_by(Classe.nom_classe)
    )

    # 📊 Stats globales
    t_query = db.query(
        func.count(Presence.id).label("total_inscrits"),
        func.sum(
            case((Presence.valeur == True, 1), else_=0)
        ).label("presents"),
        func.sum(
            case((Presence.valeur == False, 1), else_=0)
        ).label("absents"),
    ).filter(
        Presence.date_daujourdhui.between(start_day, end_day)
    )

    t_result = t_query.first()

    total    = t_result.total_inscrits or 0
    presents = t_result.presents or 0
    absents  = t_result.absents or 0
    taux = round((presents / total) * 100, 2) if total else 0

    resultats = query.all()

    stats_classes = [
        {
            "classe": r.classe,
            "presents": int(r.presents or 0),
            "total": r.total,
            "val": round((r.presents / r.total) * 100, 2) if r.total else 0
        }
        for r in resultats
    ]

    return {
        "global": {
            "taux_presence": taux,
            "total_inscrits": total,
            "absents": absents,
            "retards": 0
        },
        "classes": stats_classes
    }

# @router.get("/stats-presence-aujourdhui")
# def stats_presence_aujourdhui(
#     db: Session = Depends(get_db)
# ):
#     today = date.today()

#     start_day = datetime.combine(today, time.min)
#     end_day   = datetime.combine(today, time.max)

#     query = (
#         db.query(
#             Classe.nom_classe.label("classe"),
#             func.sum(
#                 case(
#                     (Presence.valeur == True, 1),
#                     else_=0
#                 )
#             ).label("val"),
#             func.count(Presence.id).label("total")
#         )
#         .join(Classe, Classe.id == Presence.classes_id)
#         .filter(Presence.date_daujourdhui.between(start_day, end_day))
#         .group_by(Classe.id, Classe.nom_classe)
#         .order_by(Classe.nom_classe)
#     )

#     t_query = db.query(
#         func.count(Presence.id).label("total_inscrits"),
#         func.sum(
#             case(
#                 (Presence.valeur == True, 1),
#                 else_=0
#             )
#         ).label("presents"),
#         func.sum(
#             case(
#                 (Presence.valeur == False, 1),
#                 else_=0
#             )
#         ).label("absents"),
#     ).filter(
#         Presence.date_daujourdhui.between(start_day, end_day)
#     )

#     t_result = t_query.first()

#     total    = t_result.total_inscrits or 0
#     presents = t_result.presents or 0
#     absents  = t_result.absents or 0
#     taux = round((presents / total) * 100, 2) if total else 0


#     resultats = query.all()

#     return [
#         "taux_presence": taux,
#         "total_inscrits": total,
#         "absents": absents,
#         "retards": 0,  # pour le moment
#         {
#             "classe": r.classe,
#             "taux": int(r.val or 0),
#             "total": r.total,
#             "val": round((r.val / r.total) * 100, 2) if r.total else 0
#         }
#         for r in resultats
#     ]

 
# ══════════════════════════════════════════════════════════════════════════
#  POST /api/presences
#  Enregistre l'appel complet d'une classe pour une date
# ══════════════════════════════════════════════════════════════════════════

@router.post("/presences")
def enregistrer_appel(
    payload: AppelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PRESENCE_ROLES))
):
    """
    Crée ou met à jour les présences d'une classe pour une date donnée.
    Utilise UPSERT : si une présence existe déjà pour (etudiant, classe, date),
    elle est mise à jour plutôt que dupliquée.
    """
    date_dt = datetime.combine(payload.date_daujourdhui, datetime.min.time())

    # Vérifier que la classe existe
    classe = db.query(Classe).filter(Classe.id == payload.classes_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    saved = []

    for item in payload.presences:
        # Chercher si une présence existe déjà pour ce jour
        existing = db.query(Presence).filter(
            and_(
                Presence.etudiant_id          == item.etudiant_id,
                Presence.classes_id           == payload.classes_id,
                Presence.annee_academique_id  == payload.annee_academique_id,
                func.date(Presence.date_daujourdhui) == payload.date_daujourdhui,
            )
        ).first()

        if existing:
            # Mise à jour
            existing.valeur     = item.valeur
            existing.updated_at = datetime.utcnow()
            saved.append(existing)
        else:
            # Création
            presence = Presence(
                id                   = str(uuid.uuid4()),
                etudiant_id          = item.etudiant_id,
                classes_id           = payload.classes_id,
                annee_academique_id  = payload.annee_academique_id,
                date_daujourdhui     = date_dt,
                valeur               = item.valeur,
            )
            db.add(presence)
            saved.append(presence)

    db.commit()

    return {
        "message":  f"{len(saved)} présence(s) enregistrée(s)",
        "classe_id": payload.classes_id,
        "date":      str(payload.date_daujourdhui),
        "total":     len(saved),
        "presents":  sum(1 for p in saved if p.valeur),
        "absents":   sum(1 for p in saved if not p.valeur),
    }


# ══════════════════════════════════════════════════════════════════════════
#  GET /api/presences/historique
#  Résumé des absences par étudiant (pour l'onglet Historique)
# ══════════════════════════════════════════════════════════════════════════

@router.get("/presences/historique")
def historique_presences(
    classe_id:            Optional[str] = None,
    annee_academique_id:  Optional[str] = None,
    mois:                 Optional[str] = None,   # format "2025-02"
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PRESENCE_ROLES))
):
    """
    Retourne par étudiant :
      - nombre d'absences (valeur=False)
      - nombre de jours total
      - taux de présence calculé
    """
    # query = db.query(
    #     Presence.etudiant_id,
    #     func.count(Presence.id).label("total_jours"),
    #     func.sum(
    #         func.cast(Presence.valeur == True, db.bind.dialect.name == "mysql" and "UNSIGNED" or "INTEGER")
    #     ).label("presents"),
    # ).group_by(Presence.etudiant_id)

    query = db.query(
    Presence.etudiant_id,
    func.count(Presence.id).label("total_jours"),
    func.sum(
        case(
            (Presence.valeur == True, 1),
            else_=0
        )
    ).label("presents"),
    ).group_by(Presence.etudiant_id)

    if classe_id:
        query = query.filter(Presence.classes_id == classe_id)
    if annee_academique_id:
        query = query.filter(Presence.annee_academique_id == annee_academique_id)
    if mois:
        try:
            annee, m = mois.split("-")
            query = query.filter(
                func.year(Presence.date_daujourdhui)  == int(annee),
                func.month(Presence.date_daujourdhui) == int(m),
            )
        except ValueError:
            pass

    rows = query.all()

    result = []
    for row in rows:
        etudiant = db.query(Etudiant).filter(Etudiant.id == row.etudiant_id).first()
        if not etudiant:
            continue

        total    = row.total_jours or 0
        presents = int(row.presents or 0)
        absents  = total - presents
        taux     = round((presents / total) * 100) if total > 0 else 0

        # Nom de la classe
        classe_nom = "—"
        if classe_id:
            c = db.query(Classe).filter(Classe.id == classe_id).first()
            classe_nom = c.nom_classe if c else "—"

        result.append({
            "id":       etudiant.id,
            "nom":      f"{etudiant.prenom} {etudiant.nom}".strip(),
            "classe":   classe_nom,
            "absences": absents,
            "retards":  0,      # votre modèle n'a pas de retard
            "taux":     taux,
        })

    # Trier par taux de présence croissant (les plus absents en premier)
    result.sort(key=lambda x: x["taux"])
    return result


# ══════════════════════════════════════════════════════════════════════════
#  GET /api/presences/jour
#  Retourne l'appel déjà enregistré pour une classe+date (pour pré-remplir)
# ══════════════════════════════════════════════════════════════════════════

@router.get("/presences/jour")
def get_appel_du_jour(
    classes_id:          str,
    annee_academique_id: str,
    date:                str,    # "2025-02-24"
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PRESENCE_ROLES))
):
    """
    Retourne les présences déjà enregistrées pour une classe à une date.
    Utilisé pour pré-remplir les boutons si l'appel a déjà été fait.
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail="Format de date invalide (attendu: YYYY-MM-DD)")

    presences = db.query(Presence).filter(
        and_(
            Presence.classes_id           == classes_id,
            Presence.annee_academique_id  == annee_academique_id,
            func.date(Presence.date_daujourdhui) == date_obj,
        )
    ).all()

    return {
        etudiant_id: p.valeur
        for p in presences
        for etudiant_id in [p.etudiant_id]
    }
