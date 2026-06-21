from pydantic import BaseModel, Field
from typing import Optional
from fastapi.responses import  StreamingResponse
from app.Helper.pdf_personaliser import PDFGenerator
from itertools import groupby
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Dict
from datetime import date, datetime  
# Supposons que vous avez votre configuration DB dans database.py
from app.database import get_db 
from app.Models.MModels import AnneeAcademique 
from app.Models.MSystems import Profile  
from app.Models.MRelations import CoursEtudiant  


class PedagogiqueRequest(BaseModel):
    identifiant: Optional[bool] = False
    classe: str
    annee_ac: str
    cycle: str
    mois: Optional[str] = "Tous les mois"

router = APIRouter(prefix="/api/v1", tags=["PDF"])
pdf_gen = PDFGenerator()
 

def get_max_coefficients_for_class(db: Session, classe_id: str, annee_academique: str, mois: str):
    max_coeffs = {}
    
    # Récupérer les données des cours pour cette classe
    etudiants = db.query(CoursEtudiant).filter(
        CoursEtudiant.classe == classe_id,
        CoursEtudiant.annee_academique == annee_academique
    ).all()

    for etudiant in etudiants:
        try:
            # En Python, si c'est déjà stocké en JSON (JSONB), pas besoin de json.loads
            notes_data = json.loads(etudiant.data_etudiant) if isinstance(etudiant.data_etudiant, str) else etudiant.data_etudiant
            
            # On vérifie la structure { identifiant: { base: {}, orale: {} } }
            student_notes = notes_data.get(etudiant.identifiant, {})
            if not student_notes:
                continue

            for type_note in ['base', 'orale']:
                for matiere, detail in student_notes.get(type_note, {}).items():
                    coef = float(detail.get('coefficients', 0))
                    notes = detail.get('notes', {})

                    if not isinstance(notes, dict) or not notes:
                        continue

                    if mois != "Tous les mois":
                        if mois not in notes:
                            continue
                        total_coef = coef
                    else:
                        total_coef = coef * len(notes)

                    # On garde le coefficient maximum trouvé pour cette matière dans la classe
                    if matiere not in max_coeffs or total_coef > max_coeffs[matiere]:
                        max_coeffs[matiere] = total_coef
        except Exception:
            continue

    return sum(max_coeffs.values())

def calculer_moyenne_generale(data_etudiant_str, identifiant, max_coef, mois):
    try:
        # Laravel fait parfois un double encodage JSON selon la DB
        parse_data = json.loads(data_etudiant_str)
        if isinstance(parse_data, str):
            parse_data = json.loads(parse_data)
        
        data = parse_data.get(identifiant, {})
        total_notes = 0.0
        total_coefficients = 0.0

        for type_note in ['base', 'orale']:
            for matiere, details in data.get(type_note, {}).items():
                notes = details.get('notes', {})
                coef = float(details.get('coefficients', 0))

                if not isinstance(notes, dict) or not notes:
                    continue

                if mois != "Tous les mois":
                    if mois in notes:
                        notes_utilisees = [float(notes[mois])]
                    else:
                        continue
                else:
                    notes_utilisees = [float(v) for v in notes.values()]

                total_notes += sum(notes_utilisees)
                total_coefficients += coef * len(notes_utilisees)

        if max_coef <= 0:
            return [0.0, 0.0, 0.0]

        moyenne_generale = (total_notes / max_coef) * 10
        return [round(moyenne_generale, 2), total_notes, total_coefficients]
    
    except Exception:
        return [0.0, 0.0, 0.0]

# --- Route Principale ---

@router.post("/print-repport-pedagogiques")
def print_pedagogique_rapport(req: PedagogiqueRequest, db: Session = Depends(get_db)):

    annee_obj = db.query(AnneeAcademique).filter(AnneeAcademique.id == req.annee_ac).first()
    if not annee_obj:
        raise HTTPException(status_code=404, detail="Année académique introuvable")
    
    annee_libelle = annee_obj.annee_academique
    
    sql_query = text("""
        SELECT ce.*, c.id as classeId, e.nom, e.prenom, e.identifiant, e.id as etudiant_id, 
               c.nom_classe, coe.data_etudiant,
               (SELECT CONCAT(p.nom, ' ', p.prenom)
                FROM professeurs p
                LEFT JOIN programmes pr ON p.id = pr.professeur_id
                WHERE c.id = pr.class 
                AND ce.niveau_id = pr.niveau_id
                AND pr.annee_academique = :annee_id
                LIMIT 1) as professeur
        FROM classes_etudiants ce
        JOIN etudiants e ON ce.etudiant_id = e.id
        JOIN cours_etudiants coe ON coe.etudiant_id = ce.etudiant_id
        JOIN classes c ON ce.classes_id = c.id
        WHERE ce.annee_academique_id = :annee_id
        AND coe.annee_academique = :annee_libelle
        AND ce.status = 1
    """)

    params = {"annee_id": req.annee_ac, "annee_libelle": annee_libelle}
    
    if req.classe and req.classe != "Toutes les classes":
        sql_query = text(str(sql_query) + " AND ce.classes_id = :classe_id")
        params["classe_id"] = req.classe

    results_proxy = db.execute(sql_query, params).mappings().all()

    # 3. Traitement des données
    data_pedagogique = []
    max_coeffs_cache = {}

    for row in results_proxy:
        if row['data_etudiant'] and row['data_etudiant'] != "[]":
            classe_id = row['classeId']
            
            if classe_id not in max_coeffs_cache:
                max_coeffs_cache[classe_id] = get_max_coefficients_for_class(
                    db, classe_id, annee_libelle, req.mois
                )

            max_coef = max_coeffs_cache[classe_id]
            stats = calculer_moyenne_generale(row['data_etudiant'], row['identifiant'], max_coef, req.mois)

            if "Kind " in row['nom_classe']:
                continue

            m_general = 6.5 if row['nom_classe'].startswith("CP") else 6.0

            data_pedagogique.append({
                "id": row['etudiant_id'],
                "nom": row['nom'],
                "prenom": row['prenom'],
                "professeur": row['professeur'],
                "classe": row['nom_classe'],
                "note": stats[1],
                "max": stats[2],
                "moyenne": stats[0],
                "status": "Succès" if stats[0] >= m_general else "Echec"
            })

    profile_info = db.query(Profile).first()

    
    data_pedagogique_sorted = sorted(data_pedagogique, key=lambda x: x['classe'])
 
    total_echec = sum(1 for item in data_pedagogique_sorted if item['status'] == "Echec")
 
    groupes = {}
    for key, group in groupby(data_pedagogique_sorted, lambda x: x['classe']):
         groupes[key] = list(group)

    # --- Nouveau dictionnaire pour regrouper par MATIÈRE ---
    matieres_stats = {} 
    if req.classe and req.classe != "Toutes les classes":
        for row in results_proxy:
            if row['data_etudiant'] and row['data_etudiant'] != "[]":
                # Parsing du JSON complexe
                raw_data = json.loads(row['data_etudiant'])
                if isinstance(raw_data, str): raw_data = json.loads(raw_data)
                
                student_id = row['identifiant']
                student_name = f"{row['nom']} {row['prenom']}"
                student_notes = raw_data.get(student_id, {})

                for type_note in ['base', 'orale']:
                    for nom_matiere, details in student_notes.get(type_note, {}).items():
                        # Initialiser la matière dans notre dictionnaire si elle n'existe pas
                        if nom_matiere not in matieres_stats:
                            matieres_stats[nom_matiere] = {
                                "nom": nom_matiere,
                                "professeur": row['professeur'] or "Non assigné",
                                "eleves": [],
                                "somme_notes": 0,
                                "nb_notes": 0
                            }
                        
                        # Extraire la note du mois choisi (ou moyenne des mois)
                        notes_dict = details.get('notes', {})
                        if req.mois != "Tous les mois":
                            valeur_note = notes_dict.get(req.mois)
                        else:
                            # Moyenne annuelle pour cette matière
                            vals = [float(v) for v in notes_dict.values() if v is not None]
                            valeur_note = sum(vals) / len(vals) if vals else None

                        if valeur_note is not None:
                            valeur_float = float(valeur_note)
                            matieres_stats[nom_matiere]["eleves"].append({
                                "nom": student_name,
                                "note": valeur_float,
                                "status": "Succès" if valeur_float >= 10 else "Echec"
                            })
                            matieres_stats[nom_matiere]["somme_notes"] += valeur_float
                            matieres_stats[nom_matiere]["nb_notes"] += 1

        # --- Finalisation des moyennes par matière ---
        for m in matieres_stats.values():
            if m["nb_notes"] > 0:
                m["moyenne_matiere"] = round(m["somme_notes"] / m["nb_notes"], 2)
                m["taux_reussite"] = round((sum(1 for e in m["eleves"] if e["note"] >= 10) / m["nb_notes"]) * 100, 1)
 
    data_to_render = {
     "data_pedagogique": data_pedagogique_sorted, # Données triées
     "totalEchec": total_echec,                   # Le compteur calculé
     "groupes": groupes,                         # Le dictionnaire groupé
     "_info": profile_info,
     "classe": req.classe,
     "identifiant": req.identifiant,
     'matieres_stats':matieres_stats
    #  "date": datetime.now().strftime("%d/%m/%Y"),
     }
    # return data_to_render
    

    

    pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        template_file="rapport_pedagogique.html",  # Votre template Jinja2
        data=data_to_render,
        output_filename="rapport_pedagogique.pdf"
    )
    # return data_to_render
          # Retourner le PDF
    return StreamingResponse(
          pdf_buffer,
          media_type="application/pdf",
          headers={
               "Content-Disposition": "attachment; filename=rapport_pedagogique.pdf"
          }
     )

@router.post("/print-repport-pedagogique")
def print_pedagogique_rapport(req: PedagogiqueRequest, db: Session = Depends(get_db)):
    # 1. Validation de l'année
    annee_obj = db.query(AnneeAcademique).filter(AnneeAcademique.id == req.annee_ac).first()
    if not annee_obj:
        raise HTTPException(status_code=404, detail="Année académique introuvable")
    print(req)
    annee_libelle = annee_obj.annee_academique

    # 2. Construction de la requête SQL flexible
    query_base = """
        SELECT ce.*, c.id as classeId, e.nom, e.prenom, e.identifiant, e.id as etudiant_id, 
               c.nom_classe, coe.data_etudiant,
               (SELECT CONCAT(p.nom, ' ', p.prenom)
                FROM professeurs p
                LEFT JOIN programmes pr ON p.id = pr.professeur_id
                WHERE c.id = pr.class 
                AND ce.niveau_id = pr.niveau_id
                AND pr.annee_academique = :annee_id
                LIMIT 1) as professeur
        FROM classes_etudiants ce
        JOIN etudiants e ON ce.etudiant_id = e.id
        JOIN cours_etudiants coe ON coe.etudiant_id = ce.etudiant_id
        JOIN classes c ON ce.classes_id = c.id
        WHERE ce.annee_academique_id = :annee_id
        AND coe.annee_academique = :annee_libelle
        AND ce.status = 1
    """
    
    params = {"annee_id": req.annee_ac, "annee_libelle": annee_libelle}
    if req.classe and req.classe != "Toutes les classes":
        query_base += " AND ce.classes_id = :classe_id"
        params["classe_id"] = req.classe

    results = db.execute(text(query_base), params).mappings().all()

    # 3. Traitement des données
    data_pedagogique = []
    max_coeffs_cache = {}
    liste_echecs_details = []

    for row in results:
        if not row['data_etudiant'] or row['data_etudiant'] == "[]":
            continue
        if "kind" in row['nom_classe'].lower():
            continue

        classe_id = row['classeId']
        
        if classe_id not in max_coeffs_cache:
            max_coeffs_cache[classe_id] = get_max_coefficients_for_class(
                db, classe_id, annee_libelle, req.mois
            )

        stats = calculer_moyenne_generale(row['data_etudiant'], row['identifiant'], max_coeffs_cache[classe_id], req.mois)
        
        
        m_passage = 6.5 if "CP" in row['nom_classe'] else 6.0
        status = "Succès" if stats[0] >= m_passage else "Echec"
 
        # matieres_faibles = []
        # raw_data = json.loads(row['data_etudiant'])
        # if isinstance(raw_data, str): raw_data = json.loads(raw_data)
        
        # student_notes = raw_data.get(row['identifiant'], {})
        # for type_n in ['base', 'orale']:
        #     for nom_m, det in student_notes.get(type_n, {}).items():
        #         notes_dict = det.get('notes', {})
                
        #         if req.mois != "Tous les mois":
        #             val_note = float(notes_dict.get(req.mois, 0))
        #         else:
        #             vals = [float(v) for v in notes_dict.values() if v is not None]
        #             val_note = sum(vals)/len(vals) if vals else 0
                
        #         if val_note < (float(det.get('coefficients', 0)) * 5):  
        #             matieres_faibles.append({"nom": nom_m, "note": round(val_note, 2)})

        # --- Analyse des matières en échec ---
        matieres_faibles = []

        # Sécurité : on s'assure que data_etudiant n'est pas vide
        if row['data_etudiant']:
            raw_data = json.loads(row['data_etudiant'])
            if isinstance(raw_data, str): 
                raw_data = json.loads(raw_data)


            student_notes = {}
            if isinstance(raw_data, dict):
                student_notes = raw_data.get(row['identifiant'], {})
            elif isinstance(raw_data, list) and len(raw_data) > 0:
                
                student_notes = raw_data[0].get(row['identifiant'], {}) if isinstance(raw_data[0], dict) else {}

            # On continue seulement si on a un dictionnaire
            if isinstance(student_notes, dict):
                for type_n in ['base', 'orale']:
                    details_section = student_notes.get(type_n, {})
                    if not isinstance(details_section, dict): continue
                    
                    for nom_m, det in details_section.items():
                        notes_dict = det.get('notes', {})
                        if not isinstance(notes_dict, dict): continue
                        
                        # Calcul de la note selon le filtre mois
                        if req.mois != "Tous les mois":
                            val_note = float(notes_dict.get(req.mois, 0))
                        else:
                            vals = [float(v) for v in notes_dict.values() if v is not None]
                            val_note = sum(vals)/len(vals) if vals else 0
                        
                        coeff_val = float(det.get('coefficients', 0))
                        if val_note < (coeff_val * 5): 
                            matieres_faibles.append({"nom": nom_m, "note": round(val_note, 2)})
    
        etudiant_obj = {
            "nom": row['nom'],
            "prenom": row['prenom'],
            "classe": row['nom_classe'],
            "moyenne": stats[0],
            "status": status,
            "matieres_faibles": matieres_faibles if status == "Echec" else []
        }
        
        data_pedagogique.append(etudiant_obj)
        if status == "Echec":
            liste_echecs_details.append(etudiant_obj)

    # 4. Calculs globaux pour le Header
    total_eleves = len(data_pedagogique)
    total_echec = len(liste_echecs_details)
    total_succes = total_eleves - total_echec
    pc_reussite = round((total_succes / total_eleves * 100), 2) if total_eleves > 0 else 0
 
    profile_info = db.query(Profile).first()
    
    data_to_render = {
        "total_eleves": total_eleves,
        "total_succes": total_succes,
        "total_echec": total_echec,
        "pourcentage_reussite": pc_reussite,
        "pourcentage_echec": round(100 - pc_reussite, 2),
        "liste_echecs": sorted(liste_echecs_details, key=lambda x: x['classe']),
        "periode": req.mois,
        "annee_libelle": annee_libelle,
        "_info": profile_info,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "date_export": "07/02/2026" # Exemple
    }
    # return data_to_render
    pdf_buffer = pdf_gen.generate_pdf_for_api_html(
        template_file="rapport_pedagogique.html",
        data=data_to_render,
        output_filename="rapport_pedagogique.pdf"
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=rapport_pedagogique.pdf"}
    )


# @router.post("/print-repport-pedagogique")
# def print_pedagogique_rapport(req: PedagogiqueRequest, db: Session = Depends(get_db)):
#     # ... (Début de la route inchangé : validation année et exécution SQL) ...

#     data_pedagogique = []
#     max_coeffs_cache = {}
#     liste_echecs_details = []

#     for row in results:
#         # 1. Sauter si pas de données ou si c'est une classe "Kindergarten"
#         if not row['data_etudiant'] or row['data_etudiant'] == "[]":
#             continue
            
#         # Filtrer les classes "Kind" (insensible à la casse)
#         if "kind" in row['nom_classe'].lower():
#             continue

#         classe_id = row['classeId']
        
#         # 2. Gestion sécurisée du JSON pour calculer la moyenne
#         # On s'assure que calculer_moyenne_generale ne crash pas sur une liste
#         stats = calculer_moyenne_generale(row['data_etudiant'], row['identifiant'], max_coeffs_cache.get(classe_id, 0), req.mois)
        
#         m_passage = 6.5 if "CP" in row['nom_classe'] else 6.0
#         status = "Succès" if stats[0] >= m_passage else "Echec"

#         # 3. Analyse sécurisée des matières (Correction du crash AttributeError)
#         matieres_faibles = []
#         try:
#             raw_data = json.loads(row['data_etudiant'])
#             if isinstance(raw_data, str): 
#                 raw_data = json.loads(raw_data)

#             # Sécurité : on s'assure que raw_data est un dictionnaire
#             student_notes = {}
#             if isinstance(raw_data, dict):
#                 student_notes = raw_data.get(row['identifiant'], {})
#             elif isinstance(raw_data, list) and len(raw_data) > 0:
#                 # Si c'est une liste qui contient un dict (cas fréquent en export PHP)
#                 if isinstance(raw_data[0], dict):
#                     student_notes = raw_data[0].get(row['identifiant'], {})

#             # Si on a bien trouvé un dictionnaire de notes
#             if isinstance(student_notes, dict):
#                 for type_n in ['base', 'orale']:
#                     section = student_notes.get(type_n, {})
#                     if not isinstance(section, dict): continue
                    
#                     for nom_m, det in section.items():
#                         notes_dict = det.get('notes', {})
#                         if not isinstance(notes_dict, dict): continue
                        
#                         # Calcul de la note
#                         if req.mois != "Tous les mois":
#                             val_note = float(notes_dict.get(req.mois, 0))
#                         else:
#                             vals = [float(v) for v in notes_dict.values() if v is not None]
#                             val_note = sum(vals)/len(vals) if vals else 0
                        
#                         # Seuil d'échec par matière (Note < 50% du coefficient)
#                         if val_note < (float(det.get('coefficients', 0)) * 5):
#                             matieres_faibles.append({"nom": nom_m, "note": round(val_note, 2)})
#         except Exception as e:
#             print(f"Erreur parsing notes pour {row['nom']}: {e}")
#             continue

#         # 4. Construction de l'objet
#         etudiant_obj = {
#             "nom": row['nom'],
#             "prenom": row['prenom'],
#             "classe": row['nom_classe'],
#             "moyenne": stats[0],
#             "status": status,
#             "matieres_faibles": matieres_faibles if status == "Echec" else []
#         }
        
#         data_pedagogique.append(etudiant_obj)
#         if status == "Echec":
#             liste_echecs_details.append(etudiant_obj)


# def calculer_moyenne_generale(data_etudiant_str, identifiant, max_coef, mois):
#     try:
#         parse_data = json.loads(data_etudiant_str)
#         if isinstance(parse_data, str):
#             parse_data = json.loads(parse_data)
        
#         # SÉCURITÉ : Si c'est une liste, on essaie de récupérer le dict
#         if isinstance(parse_data, list) and len(parse_data) > 0:
#             parse_data = parse_data[0]
            
#         if not isinstance(parse_data, dict):
#             return [0.0, 0.0, 0.0]

#         data = parse_data.get(identifiant, {}) 