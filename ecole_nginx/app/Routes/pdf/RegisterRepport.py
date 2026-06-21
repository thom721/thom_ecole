from pydantic import BaseModel, Field
from typing import Optional
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from itertools import groupby
from app.database import get_db  # Votre config DB
from app.Models.MSystems import Profile   # Votre modèle Profile

from fastapi.responses import  StreamingResponse
from app.Helper.pdf_personaliser import PDFGenerator

class RegisterReportRequest(BaseModel):
    identifiant: Optional[bool] = None  # Reçoit "on" ou None du formulaire
    classe: str
    annee_ac: str
    cycle: str

# {
# "identifiant": True,
#  "classe": "0ec8281b-7171-49fe-b656-901c3f5c67ae",
#  "annee_ac": "8b0f7424-e2db-42f6-a64d-d1d1ea2f68d8", 
# "cycle": "e7f8d26b-e3c5-11ef-9913-3e7db61a5f8d"
# }
router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()

@router.post("/print-repport-register")
def print_register_report(report_req: RegisterReportRequest, db: Session = Depends(get_db)):
    print(report_req)
    try:
        # 1. Construction de la requête avec Jointures
        # On utilise mappings().all() pour simuler le comportement d'objet de Laravel
        query_sql = text("""
            SELECT 
                ce.*, 
                e.nom, e.prenom, e.identifiant as etudiant_identifiant,
                n.name as niveau_name,
                a.annee_academique,
                c.nom_classe
            FROM classes_etudiants ce
            JOIN etudiants e ON ce.etudiant_id = e.id
            JOIN niveaux n ON ce.niveau_id = n.id
            JOIN annee_academiques a ON ce.annee_academique_id = a.id
            JOIN classes c ON ce.classes_id = c.id
            WHERE ce.annee_academique_id = :annee_ac
            AND ce.status = 1
        """)

        params = {"annee_ac": report_req.annee_ac}

        # Filtres conditionnels
        if report_req.classe and report_req.classe != "Toutes les classes":
            query_sql = text(str(query_sql) + " AND ce.classes_id = :classe_id")
            params["classe_id"] = report_req.classe

        if report_req.cycle and report_req.cycle != "All":
            query_sql = text(str(query_sql) + " AND ce.niveau_id = :niveau_id")
            params["niveau_id"] = report_req.cycle

        # Ordre alphabétique
        query_sql = text(str(query_sql) + " ORDER BY c.nom_classe, e.nom")
        
        results = db.execute(query_sql, params).mappings().all()

        # 2. Préparation des données pour Jinja2 (Logique groupBy)
        # Transformation des résultats en liste de dictionnaires
        # print(results)
        # return results
        data_register = [dict(r) for r in results]
        print(data_register)
        # Simulation du identifiant == 'on'
        is_identifiant = True #if report_req.identifiant == "on" else False

        # Groupement par classe (pour le cas 'Toutes les classes')
        grouped_payments = {}
        if is_identifiant:
            for key, group in groupby(data_register, lambda x: x['classes_id']):
                grouped_payments[key] = list(group)

        # Groupement pour le récapitulatif Cycle/Section
        grouped_summary = {}
        for key, group in groupby(data_register, lambda x: f"{x['niveau_name']}-{x['nom_classe']}"):
            grouped_summary[key] = list(group)

        # 3. Récupération des infos du profil
        info = db.query(Profile).first()

        # 4. Retour des données au format attendu par le template
        data = {
            "data_register": data_register,
            "grouped_payments": grouped_payments,
            "grouped_summary": grouped_summary,
            "info": info,
            "classe": report_req.classe,
            "cycle": report_req.cycle,
            "identifiant": is_identifiant
        }
     
        pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        "register_repport.html",  # Votre template Jinja2
        data,
        "register_repport.pdf"
    )
        # return data
          # Retourner le PDF
        return StreamingResponse(
               pdf_buffer,
               media_type="application/pdf",
               headers={
                    "Content-Disposition": "attachment; filename=register_repport.pdf"
               }
          )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Une erreur s'est produite lors de l'affichage du rapport: {str(e)}"
        )
    

    
    # {"identifiant": True, "classe": "0ec8281b-7171-49fe-b656-901c3f5c67ae", "annee_ac": "8b0f7424-e2db-42f6-a64d-d1d1ea2f68d8", "cycle": "e7f8d26b-e3c5-11ef-9913-3e7db61a5f8d"}