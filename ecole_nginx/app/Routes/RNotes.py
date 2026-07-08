from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any, Optional  
import json
import logging
from app.Schemas.SNotes import *
from app.database import get_db
from app.Models.MRelations import CoursEtudiant
from app.Models.MModels import Professeur,User,Niveau,Classe
from app.Models.MSystems import Log
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe,require_role

PEDAGOGIC_ROLES = ['admin', 'Responsable pédagogique', 'teacher']
logger = logging.getLogger(__name__)
# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def parse_etudiant_data(data_etudiant: Any) -> Dict[str, Any]:
    """Parse les données JSON de l'étudiant de manière sécurisée"""
    try:
        if isinstance(data_etudiant, str):
            if not data_etudiant or data_etudiant.strip() == "":
                return {}
            return json.loads(data_etudiant)
        elif isinstance(data_etudiant, dict):
            return data_etudiant
        elif data_etudiant is None:
            return {}
        else:
            return {}
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Erreur de parsing JSON: {str(e)}")
        return {}

def check_note_sequence(
    data: Dict[str, Any],
    etudiant_id: str,
    type_matiere: str,
    cours: str,
    examen: str
) -> Dict[str, str]:
    """Vérifie la séquence correcte des notes (Contrôle ou Trimestre)"""
    
    contr = ["Contr. I", "Contr. II", "Contr. III", "Contr. IV"]
    trimestre = ["Trimestre I", "Trimestre II", "Trimestre III"]
    
    # Vérifier si c'est un contrôle ou un trimestre
    # is_controle = examen.startswith("Contr")
    # is_controle = examen.startswith("Contr")
    is_controle = examen and examen.startswith("Contr")
    sequence = contr if is_controle else trimestre
    sequence_name = "Contrôle" if is_controle else "Trimestre"
    # sequence = contr if is_controle sequence_name = "Contrôle" if is_controle else "Trimestre"
    
    # Si les données du cours n'existent pas encore
    if etudiant_id not in data or type_matiere not in data[etudiant_id] or cours not in data[etudiant_id][type_matiere]:
        # Vérifier que c'est le premier de la séquence
        if examen != sequence[0]:
            return {
                "error": f"Vous devez d'abord enregistrer les notes pour le {sequence[0]}."
            }
        return {"success": "ok"}
    
    # Vérifier la cohérence du type (pas de mélange Contrôle/Trimestre)
    existing_notes = data[etudiant_id][type_matiere][cours].get('notes', {})
    
    for existing_key in existing_notes.keys():
        if existing_key.startswith("Contr") != is_controle:
            return {
                "error": f"Vous ne pouvez pas enregistrer des notes pour ({sequence_name}), vous avez déjà utilisé ({existing_key.split()[0]}) pour cette année."
            }
    
    # Vérifier que le précédent est enregistré
    if examen in sequence:
        index = sequence.index(examen)
        if index > 0:
            precedent = sequence[index - 1]
            if precedent not in existing_notes:
                return {
                    "error": f"Vous devez d'abord soumettre les notes du {precedent}"
                }
    else:
        return {
            "error": f"Veuillez contacter les responsables pour ajouter les {sequence_name}s supplémentaires"
        }
    
    return {"success": "ok"}

def _scan_month_notes(data: Any, mois: str, delete: bool = False) -> int:
    """Parcourt récursivement le blob JSON de notes d'un étudiant
    (`CoursEtudiant.data_etudiant`) et compte — ou supprime si delete=True —
    les entrées `notes[mois]`, quelle que soit la profondeur d'imbrication
    (mois simple, session, contrôle/trimestre). Les clés utilisées pour les
    autres modes d'évaluation ("intra", "finale", "Contr. I", "Trimestre I"...)
    ne collisionnent jamais avec un nom de mois, donc ce scan générique reste
    précis même si la structure diffère selon le mode.
    """
    if not isinstance(data, dict):
        return 0
    removed = 0
    notes = data.get("notes")
    if isinstance(notes, dict) and mois in notes:
        removed += 1
        if delete:
            del notes[mois]
    for value in data.values():
        if isinstance(value, dict):
            removed += _scan_month_notes(value, mois, delete)
    return removed

# ============================================================================
# ROUTER
# ============================================================================
router_note = APIRouter(prefix="/api/v1", tags=["Cours Etudiants"])
@router_note.post("/coursEtudiant", response_model=StoreNoteResponse)
async def store_note(
    request: StoreNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PEDAGOGIC_ROLES))
):
    """
    Enregistrer ou mettre à jour les notes des étudiants
    
    Gère trois types de notation:
    1. Par mois (session=null, controle='Mois')
    2. Par session universitaire (session!=null, controle in ['Intra', 'Finale'])
    3. Par contrôle/trimestre (controle in ['Contr. I', 'Trimestre I', etc.])
    """

    if not user_has_permission(current_user, "Ajouter note",db):
            raise HTTPException(
                status_code=422,
                detail="Vous n'êtes pas autorisé à effectuer cette action"
            )
    if not user_has_permission(current_user, "Ajouter note", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorisé !"
        )
    
    try:
        # Vérifier que le professeur existe
        prof_exists = db.query(
            select(Professeur.id).where(Professeur.id == request.professeur_id).exists()
        ).scalar()
        
        if not prof_exists:
            raise HTTPException(
                status_code=422,
                detail={"errors": {"professeur_id": ["Le professeur spécifié n'existe pas"]}}
            )
        
        # Variables communes
        cours = request.cours
        coefficients = request.coefficients
        note_de_passage = request.note_de_passage  
        session = request.session
        professeur_id = request.professeur_id
        type_matiere = request.type_matiere.lower()
        annee_academique = request.annee_academique
        notes_to_update = request.notes
        logger.info(f"Traitement de {len(notes_to_update)} notes pour le cours {cours}")
        print()
        logger.info(f"cours {cours} \ncoefficients {coefficients} \nnote_de_passage {note_de_passage} session {session} \ntype_matiere {type_matiere} \nannee_academique {annee_academique} \nrequest.controle {request.controle}")
        
        # ====================================================================
        # CAS 1: NOTATION PAR MOIS (session=null, controle='Mois')
        # ====================================================================
        if session is None and request.controle and request.controle.lower() == "mois":
            
            if not coefficients or not request.examen or not cours:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": "Tous les champs (coefficient, examen et cours) doivent être remplis."}
                )
            
            examen = request.examen
            errors = []
            success_messages = []
            
            for item in notes_to_update:
                if not item.id or not item.identifiant:
                    errors.append("Données manquantes pour un étudiant.")
                    continue
                
                try:
                    # Récupérer l'étudiant
                    etudiant = db.query(CoursEtudiant).filter(
                        CoursEtudiant.etudiant_id == item.id,
                        CoursEtudiant.annee_academique == annee_academique
                    ).first()
                    
                    if not etudiant:
                        errors.append(f"Étudiant non trouvé : {item.id}")
                        continue
                    
                    # Parser les données
                    data_etudiant = parse_etudiant_data(etudiant.data_etudiant)
                    note_controle = item.note
                    
                    # Vérifier que la note ne dépasse pas le coefficient
                    if note_controle > coefficients:
                        errors.append(f"Note trop élevée pour {item.id} (max: {coefficients})")
                        continue
                    
                    # Vérifier si la note existe déjà (mise à jour)
                    if (
                        item.identifiant in data_etudiant and
                        type_matiere in data_etudiant[item.identifiant] and
                        cours in data_etudiant[item.identifiant][type_matiere] and
                        'notes' in data_etudiant[item.identifiant][type_matiere][cours] and
                        examen in data_etudiant[item.identifiant][type_matiere][cours]['notes']
                    ):
                        # Mise à jour
                        data_etudiant[item.identifiant][type_matiere][cours]['notes'][examen] = note_controle
                        data_etudiant[item.identifiant][type_matiere][cours]['coefficients'] = coefficients
                        
                        etudiant.data_etudiant = json.dumps(data_etudiant)
                        db.commit()
                        
                        success_messages.append(
                            f"Les notes du cours ({cours}) pour le mois de ({examen}) a été mise à jour avec succès !"
                        )
                    else:
                        # data_etudiant = {}
                        # Création
                        if item.identifiant not in data_etudiant:
                            data_etudiant[item.identifiant] = {}
                        if type_matiere not in data_etudiant[item.identifiant]:
                            data_etudiant[item.identifiant][type_matiere] = {}
                        if cours not in data_etudiant[item.identifiant][type_matiere]:
                            data_etudiant[item.identifiant][type_matiere][cours] = {
                                'type_matiere': type_matiere,
                                'professeur_id': professeur_id,
                                'coefficients': coefficients,
                                'note_de_passage': note_de_passage,
                                'notes': {}
                            }
                        
                        data_etudiant[item.identifiant][type_matiere][cours]['notes'][examen] = note_controle
                        
                        etudiant.data_etudiant = json.dumps(data_etudiant)
                        db.commit()
                        
                        success_messages.append(
                            f"Les notes du cours ({cours}) pour le mois de ({examen}) ajoutées avec succès !"
                        )
                
                except Exception as e:
                    db.rollback()
                    errors.append(f"Erreur interne pour {item.identifiant} : {str(e)}")
                    logger.error(f"Erreur: {str(e)}", exc_info=True)
            
            if errors:
                raise HTTPException(status_code=422, detail={"errors": errors})
            
            return StoreNoteResponse(success=success_messages[0] if success_messages else "Opération réussie")
        
        # ====================================================================
        # CAS 2: NOTATION PAR SESSION (session!=null, controle in ['Intra', 'Finale'])
        # ====================================================================
        elif session is not None and request.controle and request.controle.lower() != "mois":
            
            if not request.controle:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": "Vous devez choisir entre Intra ou Final"}
                )
            
            if note_de_passage in None:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": "Notes de passage null"}
                )
            
            controle = request.controle.lower()
            errors = []
            success_messages = []
            
            for item in notes_to_update:
                if not item.id or not item.identifiant:
                    errors.append("Données manquantes pour un étudiant.")
                    continue
                
                try:
                    etudiant = db.query(CoursEtudiant).filter(
                        CoursEtudiant.etudiant_id == item.id,
                        CoursEtudiant.annee_academique == annee_academique
                    ).first()
                    
                    if not etudiant:
                        errors.append(f"Étudiant non trouvé : {item.id}")
                        continue
                    
                    data_etudiant = parse_etudiant_data(etudiant.data_etudiant)
                    note_controle = item.note
                    
                    if note_controle > coefficients:
                        errors.append(f"Note trop élevée pour {item.id} (max: {coefficients})")
                        continue
                    
                    # Vérifier si la note existe déjà
                    if (
                        item.identifiant in data_etudiant and
                        session in data_etudiant[item.identifiant] and
                        controle in data_etudiant[item.identifiant][session] and
                        type_matiere in data_etudiant[item.identifiant][session][controle] and
                        cours in data_etudiant[item.identifiant][session][controle][type_matiere] and
                        'notes' in data_etudiant[item.identifiant][session][controle][type_matiere][cours] and
                        controle in data_etudiant[item.identifiant][session][controle][type_matiere][cours]['notes']
                    ):
                        # Mise à jour
                        data_etudiant[item.identifiant][session][controle][type_matiere][cours]['notes'][controle] = note_controle
                        
                        etudiant.data_etudiant = json.dumps(data_etudiant)
                        db.commit()
                        
                        success_messages.append(f"Les notes du cours ({cours}) a été mise à jour avec succès !")
                    else:
                        # Création
                        if controle == "intra":
                            # Initialiser la structure
                            if item.identifiant not in data_etudiant:
                                data_etudiant[item.identifiant] = {}
                            if session not in data_etudiant[item.identifiant]:
                                data_etudiant[item.identifiant][session] = {}
                            if controle not in data_etudiant[item.identifiant][session]:
                                data_etudiant[item.identifiant][session][controle] = {}
                            if type_matiere not in data_etudiant[item.identifiant][session][controle]:
                                data_etudiant[item.identifiant][session][controle][type_matiere] = {}
                            
                            data_etudiant[item.identifiant][session][controle][type_matiere][cours] = {
                                'type_matiere': type_matiere,
                                'professeur_id': professeur_id,
                                'coefficients': coefficients,
                                'note_de_passage': note_de_passage,
                                'notes': {controle: note_controle}
                            }
                            
                            etudiant.data_etudiant = json.dumps(data_etudiant)
                            db.commit()
                            
                            success_messages.append(f"Les notes intra du cours ({cours}) a été ajoutées avec succès !")
                        
                        elif controle == "finale":
                            # Vérifier que l'intra existe
                            if not (
                                item.identifiant in data_etudiant and
                                session in data_etudiant[item.identifiant] and
                                "intra" in data_etudiant[item.identifiant][session] and
                                type_matiere in data_etudiant[item.identifiant][session]["intra"] and
                                cours in data_etudiant[item.identifiant][session]["intra"][type_matiere] and
                                'notes' in data_etudiant[item.identifiant][session]["intra"][type_matiere][cours] and
                                "intra" in data_etudiant[item.identifiant][session]["intra"][type_matiere][cours]['notes']
                            ):
                                errors.append("Vous devez d'abord enregistrer les notes de l'Intra.")
                                continue
                            
                            # Initialiser la structure pour finale
                            if controle not in data_etudiant[item.identifiant][session]:
                                data_etudiant[item.identifiant][session][controle] = {}
                            if type_matiere not in data_etudiant[item.identifiant][session][controle]:
                                data_etudiant[item.identifiant][session][controle][type_matiere] = {}
                            if cours not in data_etudiant[item.identifiant][session][controle][type_matiere]:
                                data_etudiant[item.identifiant][session][controle][type_matiere][cours] = {'notes': {}}
                            
                            data_etudiant[item.identifiant][session][controle][type_matiere][cours]['notes'][controle] = note_controle
                            
                            etudiant.data_etudiant = json.dumps(data_etudiant)
                            db.commit()
                            
                            success_messages.append(f"Les notes finales du cours ({cours}) a été mise à jour avec succès !")
                
                except Exception as e:
                    db.rollback()
                    errors.append(f"Erreur interne pour {item.identifiant} : {str(e)}")
                    logger.error(f"Erreur: {str(e)}", exc_info=True)
            
            if errors:
                raise HTTPException(status_code=422, detail={"errors": errors[0]})
            
            return StoreNoteResponse(success=success_messages[0] if success_messages else "Opération réussie")
        
        # ====================================================================
     
        # ====================================================================
        elif request.examen and request.controle is not None:
            
            if not coefficients:
                raise HTTPException(status_code=422, detail={"errors": "Invalid format for coeff."})
            
            if not request.examen:
                raise HTTPException(
                    status_code=422,
                    detail={"errors": "Vous devez choisir dans le champs Evaluation / Examen"}
                )
            
            if not cours:
                raise HTTPException(status_code=422, detail={"errors": "Vous devez choisir un cours"})
            
            examen = request.examen
            
            for item in notes_to_update:
                if not item.id or not item.note or not item.identifiant:
                    raise HTTPException(status_code=422, detail={"errors": "Missing keys in note element."})
                
                try:
                    etudiant = db.query(CoursEtudiant).filter(
                        CoursEtudiant.etudiant_id == item.id,
                        CoursEtudiant.annee_academique == annee_academique
                    ).first()
                    
                    if not etudiant:
                        raise HTTPException(status_code=422, detail={"errors": "Aucun Etudiant trouvé"})
                    
                    data_etudiant = parse_etudiant_data(etudiant.data_etudiant)
                    note_controle = item.note
                    
                    if note_controle > coefficients:
                        raise HTTPException(
                            status_code=422,
                            detail={"errors": f"Veuillez vérifier les notes. Une note ne peut pas être supérieure à {coefficients}"}
                        )
                    
                    # Vérifier si la note existe déjà
                    if (
                        item.id in data_etudiant and
                        type_matiere in data_etudiant[item.id] and
                        cours in data_etudiant[item.id][type_matiere] and
                        'notes' in data_etudiant[item.id][type_matiere][cours] and
                        examen in data_etudiant[item.id][type_matiere][cours]['notes']
                    ):
                        raise HTTPException(status_code=422, detail={"errors": "Ces notes sont déjà enregistrées"})
                    
                    # Si le cours n'existe pas encore pour cet étudiant
                    if (
                        item.id not in data_etudiant or
                        type_matiere not in data_etudiant[item.id] or
                        cours not in data_etudiant[item.id][type_matiere]
                    ):
                        # Vérifier la cohérence avec les autres cours
                        if item.id in data_etudiant:
                            for matiere_key, matiere_data in data_etudiant[item.id].items():
                                for cours_key, cours_data in matiere_data.items():
                                    if 'notes' in cours_data:
                                        for note_key in cours_data['notes'].keys():
                                            if note_key[:5] != examen[:5]:
                                                error_msg = (
                                                    f"Vous ne pouvez pas enregistrer des notes pour ({'Contrôle' if examen[:5] == 'Contr' else 'Trimestre'}), "
                                                    f"vous avez déjà utilisé ({note_key.split()[0]}) pour cette année."
                                                )
                                                raise HTTPException(status_code=422, detail={"errors": error_msg})
                        
                        # Vérifier la séquence
                        check_result = check_note_sequence(data_etudiant, item.id, type_matiere, cours, examen)
                        if "error" in check_result:
                            raise HTTPException(status_code=422, detail={"errors": check_result["error"]})
                        
                        # Initialiser la structure
                        if item.id not in data_etudiant:
                            data_etudiant[item.id] = {}
                        if type_matiere not in data_etudiant[item.id]:
                            data_etudiant[item.id][type_matiere] = {}
                        
                        data_etudiant[item.id][type_matiere][cours] = {
                            'coefficients': coefficients,
                            'professeur_id': professeur_id,
                            'type_matiere': type_matiere,
                            'note_de_passage': note_de_passage,
                            'notes': {examen: note_controle}
                        }
                        
                        etudiant.data_etudiant = json.dumps(data_etudiant)
                        db.commit()
                        
                        return StoreNoteResponse(success="Notes ajoutées avec succès !")
                    
                    # Si le cours existe mais pas cette note
                    elif examen not in data_etudiant[item.id][type_matiere][cours].get('notes', {}):
                        # Vérifier la cohérence
                        for note_key in data_etudiant[item.id][type_matiere][cours]['notes'].keys():
                            if note_key[:5] != examen[:5]:
                                error_msg = (
                                    f"Vous ne pouvez pas enregistrer des notes pour ({'Contrôle' if examen[:5] == 'Contr' else 'Trimestre'}), "
                                    f"vous avez déjà utilisé ({note_key.split()[0]}) pour cette année!"
                                )
                                raise HTTPException(status_code=422, detail={"errors": error_msg})
                        
                        # Vérifier la séquence
                        check_result = check_note_sequence(data_etudiant, item.id, type_matiere, cours, examen)
                        if "error" in check_result:
                            raise HTTPException(status_code=422, detail={"errors": check_result["error"]})
                        
                        data_etudiant[item.id][type_matiere][cours]['notes'][examen] = note_controle
                        
                        etudiant.data_etudiant = json.dumps(data_etudiant)
                        db.commit()
                        
                        return StoreNoteResponse(success="Notes ajoutées avec succès !")
                    
                    else:
                        raise HTTPException(status_code=422, detail={"errors": "Note existe. 3"})
                
                except HTTPException:
                    db.rollback()
                    raise
                except Exception as e:
                    db.rollback()
                    logger.error(f"Erreur: {str(e)}", exc_info=True)
                    raise HTTPException(status_code=500, detail={"errors": f"Erreur interne : {str(e)}"})
        
        else:
            raise HTTPException(
                status_code=422,
                detail={"errors": "Contacter l'administration pour des ajouts supplémentaires"}
            )
    
    except HTTPException as e:
        pass
        # import traceback
        # traceback.print_exc()
    except Exception as e:
        logger.error(f"Erreur globale: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": str(e)})


# ============================================================================
# SUPPRESSION GROUPÉE DE NOTES (par niveau / classe / année / mois)
# ============================================================================
def _query_cours_etudiants_for_suppression(
    db: Session, niveau_id: str, classe_id: str, annee_academique: str
):
    return db.query(CoursEtudiant).filter(
        CoursEtudiant.niveau == niveau_id,
        CoursEtudiant.classe == classe_id,
        CoursEtudiant.annee_academique == annee_academique,
    ).all()


@router_note.get("/coursEtudiant/notes/apercu-suppression", response_model=DeleteNotesPreviewResponse)
def preview_delete_notes(
    niveau_id: str,
    classe_id: str,
    annee_academique: str,
    mois: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Supprimer note")),
):
    """Aperçu (lecture seule) du nombre d'étudiants/notes qui seraient
    affectés par une suppression, pour confirmation avant l'action réelle.
    """
    rows = _query_cours_etudiants_for_suppression(db, niveau_id, classe_id, annee_academique)

    etudiants_concernes = 0
    notes_a_supprimer = 0
    for row in rows:
        data = parse_etudiant_data(row.data_etudiant)
        count = _scan_month_notes(data, mois, delete=False)
        if count > 0:
            etudiants_concernes += 1
            notes_a_supprimer += count

    return DeleteNotesPreviewResponse(
        etudiants_concernes=etudiants_concernes,
        notes_a_supprimer=notes_a_supprimer,
    )


@router_note.delete("/coursEtudiant/notes/suppression", response_model=DeleteNotesResponse)
def delete_notes(
    request: DeleteNotesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Supprimer note")),
):
    """Supprime les notes d'un mois donné pour tous les étudiants d'un
    niveau/classe/année. Action groupée et irréversible : toutes les
    modifications sont regroupées dans une seule transaction (tout ou rien)
    et chaque étudiant affecté génère une entrée dans la table `logs` pour
    garder une trace de qui a supprimé quoi.
    """
    niveau = db.query(Niveau).filter(Niveau.id == request.niveau_id).first()
    if not niveau:
        raise HTTPException(status_code=422, detail={"errors": "Niveau introuvable"})

    classe = db.query(Classe).filter(Classe.id == request.classe_id).first()
    if not classe:
        raise HTTPException(status_code=422, detail={"errors": "Classe introuvable"})

    rows = _query_cours_etudiants_for_suppression(
        db, request.niveau_id, request.classe_id, request.annee_academique
    )

    etudiants_affectes = 0
    notes_supprimees = 0
    try:
        for row in rows:
            data = parse_etudiant_data(row.data_etudiant)
            count = _scan_month_notes(data, request.mois, delete=True)
            if count == 0:
                continue

            row.data_etudiant = json.dumps(data)
            db.add(row)
            db.add(Log(
                action="Suppression groupée de notes (mois)",
                user_id=current_user.id,
                model_type="CoursEtudiant",
                model_id=row.id,
                new_values={"mois": request.mois, "notes_supprimees": count},
                reason=(
                    f"{niveau.name} / {classe.nom_classe} / "
                    f"{request.annee_academique} / {request.mois}"
                    + (f" — {request.raison}" if request.raison else "")
                )[:255],
            ))
            etudiants_affectes += 1
            notes_supprimees += count

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur suppression groupée de notes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"errors": f"Erreur interne : {str(e)}"})

    if notes_supprimees == 0:
        return DeleteNotesResponse(
            success="Aucune note trouvée pour ces critères.",
            etudiants_affectes=0,
            notes_supprimees=0,
        )

    return DeleteNotesResponse(
        success=f"{notes_supprimees} note(s) supprimée(s) pour {etudiants_affectes} étudiant(s).",
        etudiants_affectes=etudiants_affectes,
        notes_supprimees=notes_supprimees,
    )
