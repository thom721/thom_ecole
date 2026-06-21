from pydantic import BaseModel, field_validator
from datetime import date
from app.Models.MModels import Classe
class PaymentReportRequest(BaseModel):
    classe: str
    date_debut: date
    date_fin: date
    versement: str

    @field_validator('date_fin')
    @classmethod
    def check_dates(cls, v, info):
        if 'date_debut' in info.data and v < info.data['date_debut']:
            raise ValueError('La date de fin doit être après la date de début')
        return v
    
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.Models.MModels import Etudiant, AnneeAcademique
from app.Models.MFinancials import Paiement
from app.Models.MRelations import ClasseEtudiant
from app.Models.MSystems import  Profile
# Importez votre helper de génération PDF (WeasyPrint ou Jinja2 + pdfkit)
# from .helpers.pdf_generator import generate_pdf 

router = APIRouter()

def calculate_payments(payments_json, data_students, req: PaymentReportRequest, all_versements=True):
    resultat = {}
    
    # Initialisation des étudiants
    for s in data_students:
        if not all_versements and s.nom_classe != req.classe:
            continue
            
        resultat[s.id] = {
            "identifiant": s.identifiant,
            "cycle": s.cycle_name or "Non défini",
            "nom": s.nom,
            "prenom": s.prenom,
            "aide_financiere": s.aide_financiere or "Aucune",
            "classe_name": s.nom_classe,
            "paiements": {"total": 0, "avance": 0, "balance": 0}
        }

    for p in payments_json:
        # On assume que p.paiement_details est déjà un dict (JSONB) ou on le parse
        details = p if isinstance(p, dict) else json.loads(p)
        info_paiement = details.get('paiement_details', {}).get('info_paiement', {})
        check_echeance = details.get('paiement_details', {}).get('check_echeance', {})
        student_id_ref = details.get('paiement_details', {}).get('details_etudiant', {}).get('identifiant')

        for date_str, donnees in info_paiement.items():
            # Logique de calcul des balances
            current_total = float(donnees.get('total_verse', 0))
            
            for student_id, r_data in resultat.items():
                if r_data['identifiant'] == student_id_ref:
                    for ech_name, ech_val in check_echeance.items():
                        if all_versements or ech_name == req.versement:
                            if ech_val <= current_total:
                                r_data['paiements'][ech_name] = True
                                if ech_name == req.versement:
                                    r_data['paiements']['total'] = ech_val
                                current_total -= ech_val
                            else:
                                if current_total > 0:
                                    r_data['paiements'][ech_name] = current_total
                                    r_data['paiements']['balance'] = ech_val - current_total
                                    r_data['paiements']['avance'] = current_total
                                else:
                                    r_data['paiements'][ech_name] = False
                                current_total = 0
    
    return list(resultat.values())

@router.post("/print-payment-report")
def print_payment_report(req: PaymentReportRequest, db: Session = Depends(get_db)):
    # 1. Obtenir l'année académique active
    annee = db.query(AnneeAcademique).filter(AnneeAcademique.status == 1).first()
    if not annee:
        raise HTTPException(status_code=404, detail="Année académique non définie")

    # 2. Récupérer les paiements (Pluck paiement_details)
    payments = db.query(Paiement.paiement_details).filter(
        Paiement.annee_academique == annee.annee_academique
    ).all()
    # payments est une liste de tuples -> [({"details":...},), ...]
    payment_list = [p[0] for p in payments]

    # 3. Récupérer les données étudiants (Le gros Join)
    students = db.query(
        Etudiant.id, Etudiant.identifiant, Etudiant.nom, Etudiant.prenom, Etudiant.aide_financiere,
        Classe.nom_classe, # Supposant que cette colonne existe ou via jointure Classe
        # ... rajouter les autres champs nécessaires
    ).join(ClasseEtudiant, Etudiant.id == ClasseEtudiant.etudiant_id)\
    .join(Classe, Classe.id == ClasseEtudiant.classes_id)\
     .filter(ClasseEtudiant.annee_academique_id == annee.id)\
     .order_by(Etudiant.nom).all()

    # 4. Traitement des données
    is_all = req.versement == "tous les versements"
    final_data = calculate_payments(payment_list, students, req, all_versements=is_all)

    # 5. Préparation PDF
    profile = db.query(Profile).first()
    
    context = {
        "data_payment": final_data,
        "info": profile,
        "versement": req.versement,
        "debut": req.date_debut,
        "fin": req.date_fin,
        "classe": req.classe
    }
    return context
    # Génération via votre helper (utilisant Jinja2)
    pdf_content = generate_pdf("pdf/Payment-rapport.html", context)

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=rapport-paiement.pdf"}
    )