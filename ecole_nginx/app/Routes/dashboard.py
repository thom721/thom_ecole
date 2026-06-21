from fastapi import APIRouter, Depends, Query,Body
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case, literal_column,or_,desc
from typing import Optional, List,Union
from datetime import datetime, date
import json

# from typing import 
from fastapi import Body
from app.Schemas.SMain import NiveauResponse
from app.Schemas.Etudiants import EtudiantResponseLive
from app.database import get_db
from app.Models.MSystems import Personnel,LogActive
from app.Models.MModels import (
    AnneeAcademique, Classe, Etudiant, 
    Cours, Professeur, Faculte, Niveau,User
)
from collections import defaultdict
# from typing import List
from app.Models.MRelations import ClasseEtudiant, Programme
from app.Models.MFinancials import Paiement
from app.Schemas.Dashboard import DashboardResponse, ClasseDetailResponse
from pydantic import BaseModel,Field
from app.Schemas.cours_schema import simpleCoursResponse
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role
from app.Helper.license_check import get_host_mac
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session   
from app.Schemas.ClassesByStudent import EtudiantClasseResponse, StudentsByClasseRequest,EtudiantClasseResponseAll
router = APIRouter(prefix="/api/v1", tags=["Dashboard"])

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard_stats(
    search: Optional[str] = Query(None, description="ID de l'année académique à rechercher"),
    db: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    """
    Récupère les statistiques du dashboard pour une année académique donnée.
    
    - Si 'search' est fourni, utilise cette année académique
    - Sinon, utilise l'année académique avec status=1 (année active)
    """
    try:
        # Obtenir l'année académique
        annee_actuelle = datetime.now().year
        
        if search:
            annee_id_obj = db.query(AnneeAcademique.id).filter(
                AnneeAcademique.id == search
            ).first()
        else:
            annee_id_obj = db.query(AnneeAcademique.id).filter(
                AnneeAcademique.status == True
            ).first()
        
        annee_id = annee_id_obj.id if annee_id_obj else None
        
        if not annee_id:
            return DashboardResponse(
                etudiant=0,
                personnel=0,
                cours=0,
                professeur=0,
                faculte=0,
                classes=0,
                paiement=0.0,
                devise="GDES",
                id_annee=None,
                classeDetails=[]
            )
        
        # 1. Compter les classes avec des étudiants pour cette année académique
        classes_query = db.query(
            ClasseEtudiant.classes_id,
            Classe.nom_classe
        ).join(
            Classe, ClasseEtudiant.classes_id == Classe.id
        ).join(
            Niveau, Classe.niveau_id == Niveau.id
        ).filter(
            ClasseEtudiant.annee_academique_id == annee_id,
            Niveau.status == True
        ).group_by(
            ClasseEtudiant.classes_id,
            Classe.nom_classe
        ).all()
        
        nombre_classes = len(classes_query)
        
        # 2. Obtenir les détails des classes
        # Construction de la sous-requête pour compter les étudiants
        etudiant_count_subquery = db.query(
            func.count(ClasseEtudiant.etudiant_id).label('count')
        ).select_from(ClasseEtudiant).join(
            Etudiant, Etudiant.id == ClasseEtudiant.etudiant_id
        ).filter(
            ClasseEtudiant.classes_id == Classe.id,
            ClasseEtudiant.annee_academique_id == annee_id
        ).correlate(Classe).scalar_subquery()
        
        # Sous-requête pour obtenir le professeur
        professeur_subquery = db.query(
            func.concat(Professeur.nom, ' ', Professeur.prenom)
        ).select_from(Professeur).join(
            Programme, Professeur.id == Programme.professeur_id
        ).join(
            ClasseEtudiant, 
            ClasseEtudiant.classes_id == Programme.class_
        ).filter(
            Classe.id == Programme.class_,
            ClasseEtudiant.niveau_id == Programme.niveau_id,
            Programme.annee_academique == annee_id
        ).limit(1).correlate(Classe).scalar_subquery()
        
        classe_details = db.query(
            Classe.id.label('classe_id'),
            Niveau.name.label('niveau_name'),
            Classe.nom_classe,
            ClasseEtudiant.annee_academique_id,
            etudiant_count_subquery.label('etudiant_count'),
            professeur_subquery.label('professeur')
        ).join(
            Niveau, Niveau.id == Classe.niveau_id
        ).join(
            ClasseEtudiant, ClasseEtudiant.classes_id == Classe.id
        ).filter(
            ClasseEtudiant.annee_academique_id == annee_id,
            Niveau.status == True
        ).group_by(
            Niveau.name,
            Classe.id,
            Classe.nom_classe,
            ClasseEtudiant.annee_academique_id
        ).all()
        
        # 3. Compter les étudiants pour cette année académique
        nombre_etudiants = db.query(
            func.count(distinct(Etudiant.id))
        ).select_from(Etudiant).join(
            ClasseEtudiant, ClasseEtudiant.etudiant_id == Etudiant.id
        ).filter(
            ClasseEtudiant.annee_academique_id == annee_id
        ).scalar()
        
        # 4. Compter le personnel
        nombre_personnel = db.query(func.count(Personnel.id)).scalar()
        
        # 5. Compter les cours
        nombre_cours = db.query(func.count(Cours.id)).scalar()
        
        # 6. Compter les professeurs
        nombre_professeurs = db.query(func.count(Professeur.id)).scalar()
        
        # 7. Compter les facultés
        nombre_facultes = db.query(func.count(Faculte.id)).scalar()
        
        # 8. Calculer le total des paiements d'aujourd'hui
        date_aujourdhui = datetime.now().strftime("%Y-%m-%d")
        date_aujourdhui_format = datetime.now().strftime("%d-%m-%Y")
        
        # Récupérer les paiements du jour
        paiements_du_jour = db.query(Paiement.paiement_details).filter(
            func.date(Paiement.updated_at) == date_aujourdhui
        ).all()
        
        total_depots = 0.0
        devise = "GDES"
        
        # Parser les JSON et calculer les totaux
        for paiement_tuple in paiements_du_jour:
            try:
                # Le paiement_details peut être un dict ou une string JSON
                paiement_data = paiement_tuple[0]
                
                if isinstance(paiement_data, str):
                    data = json.loads(paiement_data)
                elif isinstance(paiement_data, dict):
                    data = paiement_data
                else:
                    continue
                
                # Naviguer dans la structure JSON
                info_paiement = data.get('paiement_details', {}).get('info_paiement', {})
                
                # Parcourir toutes les dates dans info_paiement
                for date_key, details in info_paiement.items():
                    # Vérifier si la date correspond à aujourd'hui
                    if date_aujourdhui_format in date_key:
                        depot = details.get('depot', 0)
                        if depot:
                            total_depots += float(depot)
                        
                        # Récupérer la devise si disponible
                        if 'devise' in details:
                            devise = details['devise']
                            
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                # Log l'erreur mais continue le traitement
                continue
        
        # 9. Formatter les détails des classes
        classe_details_formatted = []
        for detail in classe_details:
            classe_details_formatted.append(ClasseDetailResponse(
                classe_id=detail.classe_id,
                niveau_name=detail.niveau_name,
                nom_classe=detail.nom_classe,
                annee_academique_id=detail.annee_academique_id,
                etudiant_count=detail.etudiant_count or 0,
                professeur=detail.professeur
            ))
        
        # 10. Retourner la réponse
        return DashboardResponse(
            etudiant=nombre_etudiants or 0,
            personnel=nombre_personnel or 0,
            cours=nombre_cours or 0,
            professeur=nombre_professeurs or 0,
            faculte=nombre_facultes or 0,
            classes=nombre_classes,
            paiement=round(total_depots, 2),
            devise=devise,
            id_annee=annee_id,
            classeDetails=classe_details_formatted
        )
        
    except Exception as e:
        # En cas d'erreur, retourner un message d'erreur détaillé
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Une erreur est survenue lors de la récupération des statistiques du dashboard"
            }
        )
    
from app.Schemas.Academic import simpleProfesseurResponse
@router.get("/prof-for-combo", response_model=simpleProfesseurResponse)
def get_all_professeur(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prof = db.query(Professeur).offset(skip).limit(limit).all()
    
    return {"prof":prof} 

@router.get("/for-combo-cours", response_model=simpleCoursResponse)
def get_all_cours(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cours = db.query(Cours).offset(skip).limit(limit).all()
    return {"cours":cours} 



# class SearchStudent(BaseModel):
#     data:List[EtudiantResponse]
@router.post("/live-student", response_model=EtudiantResponseLive)#EtudiantResponseLive)
def fetch_live_student(
    val: Union[str, dict] = Body(...),
    db: Session = Depends(get_db)
):
    # Extraire la valeur selon le format
    if isinstance(val, dict):
        search_val = val.get("val", "")
    else:
        search_val = val
    
    if not search_val:
        raise HTTPException(status_code=400, detail="Le paramètre 'val' est requis")
    
    data = db.query(Etudiant)\
        .filter(
            or_(
                Etudiant.identifiant.ilike(f"%{search_val}%"),
                Etudiant.nom.ilike(f"%{search_val}%"),
                Etudiant.prenom.ilike(f"%{search_val}%"),
                Etudiant.code.ilike(f"%{search_val}%")
            )
        )\
        .limit(10)\
        .all()
    
    return {"data": data}
    return SearchStudent(data= data)
 

@router.get("/stats/etudiants")
def stats_etudiants(
    annee_id: Optional[str] = None,   # filtre optionnel sur une année
    db: Session = Depends(get_db)
):
    # ── Requête principale avec jointures ─────────────────────────────────
    query = (
        db.query(
            ClasseEtudiant.annee_academique_id,
            ClasseEtudiant.niveau_id,
            ClasseEtudiant.classes_id,
            func.count(ClasseEtudiant.id).label("total"),
            func.sum(
                case((Etudiant.sexe == "M", 1), else_=0)
            ).label("garcons"),
            func.sum(
                case((Etudiant.sexe == "F", 1), else_=0)
            ).label("filles"),
        )
        .join(Etudiant, Etudiant.id == ClasseEtudiant.etudiant_id)
        .filter(ClasseEtudiant.status == True)
        .group_by(
            ClasseEtudiant.annee_academique_id,
            ClasseEtudiant.niveau_id,
            ClasseEtudiant.classes_id,
        )
    )

    if annee_id:
        query = query.filter(ClasseEtudiant.annee_academique_id == annee_id)

    rows = query.all()

    # ── Construire la structure hiérarchique ──────────────────────────────
    # Charger les référentiels une seule fois
    annees  = {a.id: a for a in db.query(AnneeAcademique).all()}
    niveaux = {n.id: n for n in db.query(Niveau).all()}
    classes = {c.id: c for c in db.query(Classe).all()}

    # Agréger : annee → niveau → classe
    tree = {}   # { annee_id: { niveau_id: { classe_id: {total,g,f} } } }

    for row in rows:
        a_id = row.annee_academique_id
        n_id = row.niveau_id
        c_id = row.classes_id

        if a_id not in tree:
            tree[a_id] = {}
        if n_id not in tree[a_id]:
            tree[a_id][n_id] = {}

        tree[a_id][n_id][c_id] = {
            "total":   int(row.total   or 0),
            "garcons": int(row.garcons or 0),
            "filles":  int(row.filles  or 0),
        }

    # ── Sérialiser en JSON propre ─────────────────────────────────────────
    result = []

    for a_id, niv_dict in tree.items():
        annee_obj = annees.get(a_id)
        if not annee_obj:
            continue

        annee_total = annee_garcons = annee_filles = 0
        niveaux_list = []

        for n_id, cls_dict in niv_dict.items():
            niveau_obj = niveaux.get(n_id)
            if not niveau_obj:
                continue

            niv_total = niv_garcons = niv_filles = 0
            classes_list = []

            for c_id, counts in cls_dict.items():
                classe_obj = classes.get(c_id)
                if not classe_obj:
                    continue

                classes_list.append({
                    "classe":  { "id": c_id, "nom": classe_obj.nom_classe },
                    "total":   counts["total"],
                    "garcons": counts["garcons"],
                    "filles":  counts["filles"],
                })
                niv_total   += counts["total"]
                niv_garcons += counts["garcons"]
                niv_filles  += counts["filles"]

            # Trier classes par nom
            classes_list.sort(key=lambda x: x["classe"]["nom"])

            niveaux_list.append({
                "niveau":  { "id": n_id, "nom": niveau_obj.name },
                "total":   niv_total,
                "garcons": niv_garcons,
                "filles":  niv_filles,
                "classes": classes_list,
            })
            annee_total   += niv_total
            annee_garcons += niv_garcons
            annee_filles  += niv_filles

        # Trier niveaux par nom
        niveaux_list.sort(key=lambda x: x["niveau"]["nom"])

        result.append({
            "annee":   {
                "id":      a_id,
                "libelle": getattr(annee_obj, "libelle", None) or getattr(annee_obj, "nom", "—"),
            },
            "total":   annee_total,
            "garcons": annee_garcons,
            "filles":  annee_filles,
            "niveaux": niveaux_list,
        })

    # Trier années par libelle décroissant (la plus récente en premier)
    result.sort(key=lambda x: x["annee"]["libelle"], reverse=True)
    return result

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "school_api",
        "timestamp": datetime.utcnow().isoformat()
    }

# app/routes/etudiant.py (ajoutez cette route au fichier existant)


router_class = APIRouter(prefix="/api/v1", tags=["Étudiants Par classe"])

# ... (autres routes existantes) ...

@router_class.get("/student-with-classe", response_model=EtudiantClasseResponseAll)
def get_students_by_classe(
    classe_id: str = Query(..., description="ID de la classe"),
    annee_id: str = Query(..., description="ID de l'année académique"),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les étudiants d'une classe pour une année académique donnée.
    
    - **classe_id**: UUID de la classe (requis)
    - **annee_id**: UUID de l'année académique (requis)
    
    Returns:
        Liste des étudiants avec leurs informations de base et leur statut dans la classe
    """
    
    # Vérifier que la classe existe
    classe_exists = db.query(Classe).filter(Classe.id == classe_id).first()
    if not classe_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classe avec l'ID '{classe_id}' n'existe pas"
        )
    
    # Vérifier que l'année académique existe
    annee_exists = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == annee_id
    ).first()
    if not annee_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Année académique avec l'ID '{annee_id}' n'existe pas"
        )
    
    # Récupérer les étudiants avec leurs détails
    etudiants = db.query(
        Etudiant.id,
        Etudiant.identifiant,
        Etudiant.nom,
        Etudiant.prenom,
        Etudiant.sexe,
        ClasseEtudiant.id.label('id_cls_etudiant'),
        ClasseEtudiant.status.label('status_cls_etudiant')
    ).join(
        ClasseEtudiant, Etudiant.id == ClasseEtudiant.etudiant_id
    ).join(
        Classe, Classe.id == ClasseEtudiant.classes_id
    ).join(
        AnneeAcademique, AnneeAcademique.id == ClasseEtudiant.annee_academique_id
    ).filter(
        Classe.id == classe_id,
        AnneeAcademique.id == annee_id
    ).order_by(
        Etudiant.nom
    ).all()
    
    # Si aucun étudiant trouvé, retourner une liste vide (pas d'erreur)
    if not etudiants:
        return []
    
    return EtudiantClasseResponseAll(data=etudiants)

@router.get("/licence/derniere-cle")
def get_last_license_key(db: Session = Depends(get_db)):
    # On trie par created_at (ou le nom de ta colonne date) en descendant
    last_log = db.query(LogActive)\
                 .filter(LogActive.f_key.isnot(None))\
                 .order_by(desc(LogActive.created_at))\
                 .first()

    if not last_log:
        raise HTTPException(status_code=404, detail="Aucune clé trouvée.")

    return {
        "f_key": last_log.f_key,
        "nb_jours": last_log.nb_jours,
        "date_activation": last_log.created_at
    }


@router.get("/abonnement")
def get_abonnement(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Statut de l'abonnement/licence (table log_actives, alimentée par
    POST /log-activate) + historique complet des activations. Réservé aux
    administrateurs.
    """
    if not user_has_role(current_user, ['admin'], db):
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs.")

    historique = db.query(LogActive).order_by(desc(LogActive.created_at)).all()
    if not historique:
        raise HTTPException(status_code=404, detail="Aucune activation trouvée.")

    dernier = historique[0]
    jours_restants = None
    try:
        date_expiration = datetime.strptime(dernier.exprired_at, "%Y-%m-%d").date()
        jours_restants = (date_expiration - date.today()).days
    except (ValueError, TypeError):
        pass

    return {
        "actif": jours_restants is not None and jours_restants >= 0,
        "cle_actuelle": dernier.new_key,
        "date_expiration": dernier.exprired_at,
        "jours_restants": jours_restants,
        # mac DU SERVEUR (get_host_mac(), exécuté ici côté ecole_nginx) — c'est
        # cette adresse qui est enregistrée chez infini-software (POST
        # /api/save-data au premier compte admin), PAS celle du poste client
        # qui consulte cette page. Plusieurs postes peuvent se connecter à un
        # même serveur (voir "Postes clients"/client_infos) ; seul le mac du
        # serveur compte pour l'abonnement.
        "mac": get_host_mac(),
        "historique": [
            {
                "id": h.id,
                "ancienne_cle": h.last_key,
                "nouvelle_cle": h.new_key,
                "date_expiration": h.exprired_at,
                "date_activation": h.created_at,
            }
            for h in historique
        ],
    }

import requests
from datetime import datetime


import requests
from datetime import datetime

# def sync_with_company_server(self):
#     mac = get_mac_address()
#     server_url = "https://api.votre-serveur.com"
    
#     print("[*] Synchronisation de la licence...", end="", flush=True)
    
#     try:
#         # 1. Récupérer l'email du tout premier utilisateur (celui qui a l'ID le plus petit ou créé le premier)
#         cursor = self.db_local.cursor()
#         query_user = "SELECT email FROM users ORDER BY created_at ASC LIMIT 1"
#         cursor.execute(query_user)
#         user_row = cursor.fetchone()
        
#         if not user_row:
#             print(" ❌ Aucun utilisateur trouvé localement.")
#             return False
            
#         first_email = user_row[0] # ou user_row['email'] selon ton fetch

#         # 2. Envoi en POST au serveur central
#         payload = {
#             "mac_address": mac,
#             "admin_email": first_email
#         }
        
#         response = requests.post(f"{server_url}/check-cloud-license", json=payload, timeout=15)
        
#         if response.status_code == 200:
#             data = response.json()
            
#             # 3. Mise à jour de la dernière ligne de log
#             query_update = """
#                 UPDATE log_activites 
#                 SET f_key = %s, 
#                     nb_jours = %s, 
#                     created_at = %s 
#                 WHERE id = (
#                     SELECT id FROM (
#                         SELECT id FROM log_activites 
#                         ORDER BY created_at DESC 
#                         LIMIT 1
#                     ) as tmp
#                 )
#             """
#             values = (data['f_key'], data['nb_jours'], datetime.now())
#             cursor.execute(query_update, values)
            
#             # Si la table de log est vide, on insert
#             if cursor.rowcount == 0:
#                 cursor.execute("INSERT INTO log_activites (f_key, nb_jours, created_at) VALUES (%s, %s, %s)", values)
                
#             self.db_local.commit()
#             print(f" ✅ Licence mise à jour pour {first_email}.")
#             return True
#         else:
#             print(f" ❌ Serveur : {response.status_code}")
            
#     except Exception as e:
#         print(f" ❌ Erreur : {e}")
#     return False

class UpdateInClasseSchema(BaseModel):
    """
    Schema pour mettre à jour ou supprimer un étudiant dans une classe
    """
    classe_student_id: str = Field(..., description="ID de l'enregistrement classe_etudiant")
    delete: bool = Field(..., description="True pour supprimer, False pour toggle status")

    class Config:
        json_schema_extra = {
            "example": {
                "classe_student_id": "e7f8b370-e3c5-11ef-9913-3e7db61a5f8d",
                "delete": False
            }
        }

# ==================== ROUTE ====================

@router.put("/update-etudiant-classe")
@router.patch("/update-etudiant-classe")
async def update_in_classe(
    data: UpdateInClasseSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("Modifier etudiant"))
):
    """
    Mettre à jour le statut ou supprimer un étudiant d'une classe
    
    - **classe_student_id**: ID de l'enregistrement dans classes_etudiants
    - **delete**: True pour supprimer, False pour toggle le statut
    
    Returns:
        {"success": "Success"} en cas de succès
    """
    try:
        # Vérifier que l'enregistrement existe
        find_classe = db.query(ClasseEtudiant).filter(
            ClasseEtudiant.id == data.classe_student_id
        ).first()
        
        if not find_classe:
            raise HTTPException(
                status_code=404,
                detail=f"Enregistrement classe_etudiant avec l'ID {data.classe_student_id} introuvable"
            )
        
        # Si delete = True, supprimer l'enregistrement
        if data.delete:
            db.delete(find_classe)
            db.commit()
             
            return {"success": "Success", "message": "Étudiant supprimé de la classe"}
        
        # Sinon, vérifier l'autorisation et toggle le statut
        # AuthorizationHelper.authorize_with_admin_token(request, )
        
        # Toggle le statut (0 <-> 1)
        if find_classe.status:
            find_classe.status = 0
            action = "désactivé"
        else:
            find_classe.status = 1
            action = "activé"
        
        db.commit()
        db.refresh(find_classe)
     
        
        return {
            "success": "Success",
            "message": f"Statut {action}",
            "new_status": find_classe.status
        }
    
    except HTTPException:
        # Re-lever les HTTPException sans modification
        raise
    
    except Exception as e:
        # Logger l'erreur complète pour le débogage 
        db.rollback()
        
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )






@router_class.post("/by-classe/", response_model=List[EtudiantClasseResponse])
def get_students_by_classe_post(
    request: StudentsByClasseRequest,
    db: Session = Depends(get_db)
):
    """
    Récupère tous les étudiants d'une classe pour une année académique donnée (méthode POST).
    
    Alternative à la méthode GET pour les clients qui préfèrent POST.
    """
    
    # Vérifier que la classe existe
    classe_exists = db.query(Classe).filter(Classe.id == request.classe_id).first()
    if not classe_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classe avec l'ID '{request.classe_id}' n'existe pas"
        )
    
    # Vérifier que l'année académique existe
    annee_exists = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == request.annee_id
    ).first()
    if not annee_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Année académique avec l'ID '{request.annee_id}' n'existe pas"
        )
    
    # Récupérer les étudiants
    etudiants = db.query(
        Etudiant.id,
        Etudiant.identifiant,
        Etudiant.nom,
        Etudiant.prenom,
        Etudiant.sexe,
        ClasseEtudiant.id.label('id_cls_etudiant'),
        ClasseEtudiant.status.label('status_cls_etudiant')
    ).join(
        ClasseEtudiant, Etudiant.id == ClasseEtudiant.etudiant_id
    ).join(
        Classe, Classe.id == ClasseEtudiant.classes_id
    ).join(
        AnneeAcademique, AnneeAcademique.id == ClasseEtudiant.annee_academique_id
    ).filter(
        Classe.id == request.classe_id,
        AnneeAcademique.id == request.annee_id
    ).order_by(
        Etudiant.nom
    ).all()
    
    if not etudiants:
        return []
    
    return etudiants


@router_class.get("/by-classe/{classe_id}/{annee_id}", response_model=List[EtudiantClasseResponse])
def get_students_by_classe_path(
    classe_id: str,
    annee_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère tous les étudiants d'une classe pour une année académique (path parameters).
    
    Alternative avec les paramètres dans l'URL.
    """
    
    # Vérifier que la classe existe
    classe_exists = db.query(Classe).filter(Classe.id == classe_id).first()
    if not classe_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classe avec l'ID '{classe_id}' n'existe pas"
        )
    
    # Vérifier que l'année académique existe
    annee_exists = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == annee_id
    ).first()
    if not annee_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Année académique avec l'ID '{annee_id}' n'existe pas"
        )
    
    # Récupérer les étudiants
    etudiants = db.query(
        Etudiant.id,
        Etudiant.identifiant,
        Etudiant.nom,
        Etudiant.prenom,
        Etudiant.sexe,
        ClasseEtudiant.id.label('id_cls_etudiant'),
        ClasseEtudiant.status.label('status_cls_etudiant')
    ).join(
        ClasseEtudiant, Etudiant.id == ClasseEtudiant.etudiant_id
    ).join(
        Classe, Classe.id == ClasseEtudiant.classes_id
    ).join(
        AnneeAcademique, AnneeAcademique.id == ClasseEtudiant.annee_academique_id
    ).filter(
        Classe.id == classe_id,
        AnneeAcademique.id == annee_id
    ).order_by(
        Etudiant.nom
    ).all()
    
    if not etudiants:
        return []
    
    return {"data":etudiants} 


# Route bonus : Statistiques de la classe
@router_class.get("/by-classe/stats/", response_model=dict)
def get_classe_statistics(
    classe_id: str = Query(..., description="ID de la classe"),
    annee_id: str = Query(..., description="ID de l'année académique"),
    db: Session = Depends(get_db)
):
    """
    Récupère des statistiques sur les étudiants d'une classe.
    
    Returns:
        Statistiques détaillées (total, répartition par sexe, statuts, etc.)
    """
    from sqlalchemy import func, case
    
    # Vérifications d'existence
    classe_exists = db.query(Classe).filter(Classe.id == classe_id).first()
    if not classe_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classe avec l'ID '{classe_id}' n'existe pas"
        )
    
    annee_exists = db.query(AnneeAcademique).filter(
        AnneeAcademique.id == annee_id
    ).first()
    if not annee_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Année académique avec l'ID '{annee_id}' n'existe pas"
        )
    
    # Compter total
    total = db.query(func.count(Etudiant.id)).join(
        ClasseEtudiant, Etudiant.id == ClasseEtudiant.etudiant_id
    ).filter(
        ClasseEtudiant.classes_id == classe_id,
        ClasseEtudiant.annee_academique_id == annee_id
    ).scalar()
    
    # Répartition par sexe
    sexe_stats = db.query(
        Etudiant.sexe,
        func.count(Etudiant.id).label('count')
    ).join(
        ClasseEtudiant, Etudiant.id == ClasseEtudiant.etudiant_id
    ).filter(
        ClasseEtudiant.classes_id == classe_id,
        ClasseEtudiant.annee_academique_id == annee_id
    ).group_by(Etudiant.sexe).all()
    
    # Répartition par statut
    status_stats = db.query(
        ClasseEtudiant.status,
        func.count(ClasseEtudiant.id).label('count')
    ).filter(
        ClasseEtudiant.classes_id == classe_id,
        ClasseEtudiant.annee_academique_id == annee_id
    ).group_by(ClasseEtudiant.status).all()
    
    return {
        "classe_id": classe_id,
        "annee_id": annee_id,
        "classe_nom": classe_exists.nom_classe,
        "annee_academique": annee_exists.annee_academique,
        "total_etudiants": total or 0,
        "repartition_sexe": {
            sexe: count for sexe, count in sexe_stats
        },
        "repartition_status": {
            str(status): count for status, count in status_stats
        }
    }

class NiveauResponse(BaseModel):
    id: str
    name: str
    status: int

    class Config:
        from_attributes = True

  

class ClasseResponse(BaseModel):
    id: str
    nom_classe: str
    niveau_id: str

    class Config:
        from_attributes = True

class FaculteResponse(BaseModel):
    id: str
    nom: str

    class Config:
        from_attributes = True

class CoursResponse(BaseModel):
    id: str
    cours_nom: str

    class Config:
        from_attributes = True

class NiveauWithClasseResponse(BaseModel):
    niveau: NiveauResponse
    cours: list[CoursResponse]
    facultes: list[FaculteResponse]
    classe_actuelle: list[ClasseResponse]

@router_class.get("/niveau-with-class/{niveau_id}", response_model=NiveauWithClasseResponse)
def get_niveau(niveau_id: str, db: Session = Depends(get_db)):
    if not niveau_id:
      return
    try:
        # Niveau actif
        niveau = db.query(Niveau)\
            .filter(Niveau.id == niveau_id, Niveau.status == 1)\
            .first()
        # print(niveau)
        if not niveau:
            raise HTTPException(status_code=404, detail="Niveau non trouvé")

        # Classes actuelles
        classe_actuelle = db.query(Classe)\
            .filter(Classe.niveau_id == niveau.id)\
            .order_by(Classe.created_at)\
            .all()

        # Cours
        cours = db.query(Cours)\
            .order_by(Cours.cours_nom)\
            .all()


        # Facultés
        facultes = db.query(Faculte).all()

        return {
            "niveau": niveau,
            # "niveau_detude": niveau_detude,
            "cours": cours,
            "facultes": facultes,
            "classe_actuelle": classe_actuelle
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



def parse_info_paiement(paiement_data) -> dict:
    """Extrait info_paiement depuis le champ paiement_details (str ou dict)."""
    try:
        if isinstance(paiement_data, str):
            data = json.loads(paiement_data)
        elif isinstance(paiement_data, dict):
            data = paiement_data
        else:
            return {}
        return data.get("paiement_details", {}).get("info_paiement", {})
    except (json.JSONDecodeError, AttributeError):
        return {}


# ══════════════════════════════════════════════════════════════════════════
#  GET /api/paiements/stats/annuel
#  Retourne les totaux par mois pour une année académique
#  Response :
#  {
#    "annee": "2024/2025",
#    "devise": "GDES",
#    "total_annuel": 450000,
#    "mois": [
#      { "mois": "Septembre 2024", "mois_key": "2024-09", "total": 85000,
#        "nb_versements": 12, "details": [...] },
#      ...
#    ]
#  }
# ══════════════════════════════════════════════════════════════════════════

@router.get("/paiements/stats/annuel")
def stats_annuelles(
    annee_academique: str,          # ex: "2024/2025"
    db: Session = Depends(get_db)
):
    paiements = db.query(Paiement.paiement_details).filter(
        Paiement.annee_academique == annee_academique
    ).all()

    # Agréger par mois (clé "YYYY-MM")
    mois_totaux = defaultdict(lambda: {
        "total": 0.0,
        "nb_versements": 0,
        "devise": "GDES",
        "details": []
    })

    total_annuel = 0.0
    devise_globale = "GDES"

    for (paiement_data,) in paiements:
        info_paiement = parse_info_paiement(paiement_data)

        for date_key, details in info_paiement.items():
            depot = details.get("depot", 0)
            if not depot:
                continue

            try:
                depot = float(depot)
            except (ValueError, TypeError):
                continue

            # Parser la date — format "DD-MM-YYYY HH:MM"
            try:
                dt = datetime.strptime(date_key.strip(), "%d-%m-%Y %H:%M")
            except ValueError:
                try:
                    dt = datetime.strptime(date_key.strip()[:10], "%d-%m-%Y")
                except ValueError:
                    continue

            mois_key = dt.strftime("%Y-%m")
            devise   = details.get("devise", "GDES")
            employer = details.get("employer", "—")

            mois_totaux[mois_key]["total"]         += depot
            mois_totaux[mois_key]["nb_versements"] += 1
            mois_totaux[mois_key]["devise"]         = devise
            mois_totaux[mois_key]["details"].append({
                "date":     date_key,
                "depot":    depot,
                "devise":   devise,
                "employer": employer,
                "aide":     details.get("aide_financiere", ""),
            })

            total_annuel   += depot
            devise_globale  = devise

    # Construire la liste triée par mois
    MOIS_FR = [
        "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]

    mois_liste = []
    for mois_key in sorted(mois_totaux.keys()):
        annee_str, mois_num = mois_key.split("-")
        mois_label = f"{MOIS_FR[int(mois_num)]} {annee_str}"

        mois_liste.append({
            "mois_key":      mois_key,
            "mois":          mois_label,
            "total":         round(mois_totaux[mois_key]["total"], 2),
            "nb_versements": mois_totaux[mois_key]["nb_versements"],
            "devise":        mois_totaux[mois_key]["devise"],
            "details":       sorted(
                mois_totaux[mois_key]["details"],
                key=lambda x: x["date"]
            ),
        })

    return {
        "annee":        annee_academique,
        "devise":       devise_globale,
        "total_annuel": round(total_annuel, 2),
        "nb_mois":      len(mois_liste),
        "mois":         mois_liste,
    }


# ══════════════════════════════════════════════════════════════════════════
#  GET /api/paiements/stats/journalier
#  Totaux par jour pour un mois donné (pour le drill-down)
#  Response :
#  {
#    "mois": "2024-09",
#    "total": 85000,
#    "jours": [
#      { "date": "04-09-2024", "total": 22500, "nb_versements": 3 },
#      ...
#    ]
#  }
# ══════════════════════════════════════════════════════════════════════════

@router.get("/paiements/stats/journalier")
def stats_journalieres(
    annee_academique: str,
    mois: str,                      # ex: "2024-09"
    db: Session = Depends(get_db)
):
    paiements = db.query(Paiement.paiement_details).filter(
        Paiement.annee_academique == annee_academique
    ).all()

    jours = defaultdict(lambda: {"total": 0.0, "nb_versements": 0, "depot_details": []})

    for (paiement_data,) in paiements:
        info_paiement = parse_info_paiement(paiement_data)

        for date_key, details in info_paiement.items():
            depot = details.get("depot", 0)
            if not depot:
                continue
            try:
                depot = float(depot)
                dt    = datetime.strptime(date_key.strip(), "%d-%m-%Y %H:%M")
            except (ValueError, TypeError):
                continue

            if dt.strftime("%Y-%m") != mois:
                continue

            jour_key = dt.strftime("%d-%m-%Y")
            jours[jour_key]["total"]         += depot
            jours[jour_key]["nb_versements"] += 1
            jours[jour_key]["depot_details"].append({
                "heure":    dt.strftime("%H:%M"),
                "depot":    depot,
                "employer": details.get("employer", "—"),
            })

    jours_liste = [
        {
            "date":          k,
            "total":         round(v["total"], 2),
            "nb_versements": v["nb_versements"],
            "depot_details": v["depot_details"],
        }
        for k, v in sorted(jours.items())
    ]

    return {
        "mois":  mois,
        "total": round(sum(j["total"] for j in jours_liste), 2),
        "jours": jours_liste,
    }


# ══════════════════════════════════════════════════════════════════════════
#  GET /api/paiements/stats/annees
#  Liste des années académiques disponibles dans la table paiements
# ══════════════════════════════════════════════════════════════════════════

@router.get("/paiements/stats/annees")
def liste_annees(db: Session = Depends(get_db)):
    rows = db.query(Paiement.annee_academique)\
             .distinct()\
             .order_by(Paiement.annee_academique.desc())\
             .all()
    return [r[0] for r in rows if r[0]]
