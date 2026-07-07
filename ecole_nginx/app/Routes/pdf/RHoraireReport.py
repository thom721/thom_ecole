from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.Models.MModels import Professeur, Cours, Classe, Niveau, Faculte, AnneeAcademique, User
from app.Models.MRelations import Programme
from app.Models.MSystems import Profile
from app.Helper.pdf_personaliser import PDFGenerator
from app.dependencies.Dependencie import check_permission

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()


@router.get("/print-horaire")
def print_horaire(
    niveau_id: str = Query(...),
    classe_id: str = Query(...),
    annee_academique: str = Query(..., description="AnneeAcademique.id"),
    faculte_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Imprimer rapport pedagogique")),
):
    """Emploi du temps d'une classe pour une année académique — mirror du
    bouton 'Imprimer horaire' de Cours.vue (web), dont l'endpoint
    /print-horaire n'existait pas côté backend (bouton mort)."""
    niveau = db.query(Niveau).filter(Niveau.id == niveau_id).first()
    if not niveau:
        raise HTTPException(status_code=404, detail="Niveau introuvable")
    classe = db.query(Classe).filter(Classe.id == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == annee_academique).first()
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")
    faculte = db.query(Faculte).filter(Faculte.id == faculte_id).first() if faculte_id else None

    query = db.query(Programme).filter(
        Programme.niveau_id == niveau_id,
        Programme.class_ == classe_id,
        Programme.annee_academique == annee_academique,
    )
    if faculte_id:
        query = query.filter(Programme.Faculte_id == faculte_id)

    rows = []
    for p in query.all():
        cours = db.query(Cours).filter(Cours.id == p.Cours_id).first()
        professeur = db.query(Professeur).filter(Professeur.id == p.professeur_id).first()
        rows.append({
            "cours_nom": cours.cours_nom if cours else "—",
            "professeur": f"{professeur.prenom} {professeur.nom}" if professeur else "—",
            "jours": p.jours,
            "heure": p.heure,
        })

    profile = db.query(Profile).first()
    data = {
        "info": profile,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "niveau_nom": niveau.name,
        "classe_nom": classe.nom_classe,
        "faculte_nom": faculte.nom if faculte else None,
        "annee_label": annee.annee_academique,
        "rows": rows,
    }

    pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "horaire_classe.html", data, "horaire.pdf"
    )
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=horaire.pdf"},
    )


@router.get("/print-programme-professeur")
def print_programme_professeur(
    professeur_id: str = Query(...),
    annee_academique: str = Query(..., description="AnneeAcademique.id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Imprimer rapport pedagogique")),
):
    """Charge d'enseignement d'un professeur pour une année académique :
    liste des cours/classes assignés (via Programme). Pas de vraie donnée
    d'heures fiable dans Programme.heure aujourd'hui (voir discussion) — on
    affiche donc un décompte de cours/classes, pas une durée en heures."""
    professeur = db.query(Professeur).filter(Professeur.id == professeur_id).first()
    if not professeur:
        raise HTTPException(status_code=404, detail="Professeur introuvable")
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.id == annee_academique).first()
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique introuvable")

    programmes = db.query(Programme).filter(
        Programme.professeur_id == professeur_id,
        Programme.annee_academique == annee_academique,
    ).all()

    rows = []
    for p in programmes:
        cours = db.query(Cours).filter(Cours.id == p.Cours_id).first()
        niveau = db.query(Niveau).filter(Niveau.id == p.niveau_id).first()
        classe = db.query(Classe).filter(Classe.id == p.class_).first()
        faculte = db.query(Faculte).filter(Faculte.id == p.Faculte_id).first() if p.Faculte_id else None
        rows.append({
            "cours_nom": cours.cours_nom if cours else "—",
            "niveau_nom": niveau.name if niveau else "—",
            "classe_nom": classe.nom_classe if classe else "—",
            "faculte_nom": faculte.nom if faculte else None,
        })

    # Faculté/Option n'a de sens que pour Technique/Universitaire (comme
    # note_entry_screen.dart) — colonne masquée si aucune ligne ne concerne
    # ces niveaux, plutôt que d'afficher "—" pour tout le monde.
    show_faculte = any(r["niveau_nom"] in ("Technique", "Universitaire") for r in rows)

    profile = db.query(Profile).first()
    data = {
        "info": profile,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "professeur_nom": f"{professeur.prenom} {professeur.nom}",
        "annee_label": annee.annee_academique,
        "rows": rows,
        "show_faculte": show_faculte,
    }

    pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "programme_professeur.html", data, "charge-enseignement.pdf"
    )
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=charge-enseignement.pdf"},
    )
