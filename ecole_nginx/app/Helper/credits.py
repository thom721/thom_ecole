# app/Helper/credits.py — calcul GPA/crédits pour le système à crédits
# (niveau "Universitaire" uniquement, voir app/Models/MCredits.py).
#
# Volontairement séparé des 5 implémentations existantes de moyenne
# pondérée par coefficient (app/Helper/calcule.py, pdf/BulletinPrint.py,
# pdf/MasBulletinPrint.py, pdf/PedaRepport.py, pdf/PedagogicRepport.py) :
# celles-ci pèsent des notes par coefficient sur le blob JSON CoursEtudiant
# du système par année, un calcul et un stockage structurellement
# différents. Ne pas les toucher ni tenter de converger les deux ici.

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.Models.MCredits import CoursInscription
from app.Models.MModels import Niveau

# Statuts pris en compte pour le calcul de moyenne (un cours abandonné ou
# encore en cours ne doit pas peser dans la moyenne pondérée).
_STATUTS_NOTES = ("valide", "echoue")


def calculer_moyenne_ponderee_credits(db: Session, etudiant_id: str, annee_academique_id: str | None = None) -> tuple[float, float]:
    """sum(note_globale * credits) / sum(credits) sur les CoursInscription
    validées/échouées de cet étudiant — par année si annee_academique_id
    est fourni, cumulatif (tout le cursus) sinon. Renvoie (gpa, credits_total).

    note_globale (pas note_finale, qui n'est que la note de la phase
    Final depuis l'ajout d'Intra/Final — voir plan Épic 24) est la note
    combinée qui pilote le GPA."""
    query = db.query(CoursInscription).filter(
        CoursInscription.etudiant_id == etudiant_id,
        CoursInscription.statut.in_(_STATUTS_NOTES),
        CoursInscription.note_globale.isnot(None),
    )
    if annee_academique_id is not None:
        query = query.filter(CoursInscription.annee_academique_id == annee_academique_id)

    inscriptions = query.all()
    total_credits = sum(float(i.credits) for i in inscriptions)
    if total_credits <= 0:
        return 0.0, 0.0

    total_pondere = sum(float(i.note_globale) * float(i.credits) for i in inscriptions)
    return total_pondere / total_credits, total_credits


def calculer_credits_valides(db: Session, etudiant_id: str) -> float:
    """Somme des crédits obtenus (statut='valide'), tout le cursus — les
    crédits vers le total requis pour le diplôme."""
    total = (
        db.query(func.sum(CoursInscription.credits_obtenus))
        .filter(CoursInscription.etudiant_id == etudiant_id, CoursInscription.statut == "valide")
        .scalar()
    )
    return float(total) if total is not None else 0.0


def resume_progres_etudiant(db: Session, etudiant_id: str) -> dict:
    """Vue d'ensemble : GPA cumulatif, crédits validés, détail par cours —
    consommé par GET /api/v1/credits/etudiants/{id}/progres (RCredits.py)."""
    gpa, credits_tentes = calculer_moyenne_ponderee_credits(db, etudiant_id)
    credits_valides = calculer_credits_valides(db, etudiant_id)
    inscriptions = (
        db.query(CoursInscription)
        .filter(CoursInscription.etudiant_id == etudiant_id)
        .order_by(CoursInscription.created_at.asc())
        .all()
    )
    return {
        "gpa": round(gpa, 2),
        "credits_tentes": credits_tentes,
        "credits_valides": credits_valides,
        "inscriptions": [
            {
                "id": i.id,
                "cours_id": i.cours_id,
                "annee_academique_id": i.annee_academique_id,
                "credits": float(i.credits),
                "note_intra": float(i.note_intra) if i.note_intra is not None else None,
                "note_finale": float(i.note_finale) if i.note_finale is not None else None,
                "note_globale": float(i.note_globale) if i.note_globale is not None else None,
                "credits_obtenus": float(i.credits_obtenus) if i.credits_obtenus is not None else None,
                "statut": i.statut,
            }
            for i in inscriptions
        ],
    }


def require_universitaire_actif(db: Session, niveau_id: str | None = None) -> Niveau:
    """Gate du système à crédits : n'agit que si le niveau "Universitaire"
    existe ET est actif (Niveau.status déjà existant, même convention que
    RParamExam.py/RAcademic.py/dashboard.py — pas de nouveau champ).

    Appelé par TOUS les endpoints de RCredits.py, lecture comme écriture
    (403 explicite plutôt qu'une liste vide silencieuse quand le système
    est désactivé). `niveau_id` : passer le niveau_id de la ressource
    concernée (Cours.niveau_id, CoursInscription.niveau_id) quand
    disponible, pour vérifier qu'elle appartient bien au niveau
    Universitaire ; laisser None pour les endpoints sans ressource
    cours/inscription précise (ex: vue de progrès d'un étudiant), qui ne
    vérifient alors que l'état global du niveau Universitaire."""
    query = db.query(Niveau).filter(Niveau.name == "Universitaire")
    if niveau_id is not None:
        query = query.filter(Niveau.id == niveau_id)
    niveau = query.first()
    if not niveau or not niveau.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Le système de crédits n'est pas activé pour ce niveau",
        )
    return niveau
