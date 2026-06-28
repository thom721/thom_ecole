from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4, Field
from typing import Optional
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.Models.MFinancials import Paiement
from app.Models.MSystems import Log
from app.Models.MModels import User  # Vos modèles SQLAlchemy
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,DualAuthChecker
from app.Helper.context import ActionContext,UserContext,AdminAuthorization,ReasonContext


class DeletePaiementRequest(BaseModel):
    id: str  # ou str selon votre type de PK
    index: str
    raison: str = Field(..., min_length=20, max_length=150, description="Motif du retour (20 à 150 caractères)")
 
def parse_json(field):
    """Utilitaire pour gérer les champs qui peuvent être str ou dict"""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except json.JSONDecodeError:
            return {}
    return field if field is not None else {}

# def supprimer_dernier_paiement(paiement_details: dict, cle_soumise: str, data, data_month_field: dict, current_user):
#     info_paiement = paiement_details.get('info_paiement', {})
#     print(info_paiement)
#     if cle_soumise not in info_paiement:
#         return False, "Clé de paiement introuvable"

#     # Récupérer et trier les clés par date (décroissant)
#     cles_paiement = list(info_paiement.keys())
#     try:
#         # Adaptation du usort PHP : on trie les clés ISO ou formatées en datetime
#         cles_paiement.sort(
#             key=lambda x: datetime.strptime(x.replace('/', '-'), "%d-%m-%Y -- %H:%M:%S") if '--' in x 
#             else datetime.strptime(x.replace('/', '-'), "%d-%m-%Y"), 
#             reverse=True
#         )
#     except Exception:
#         # Fallback si le format de clé est différent
#         cles_paiement.sort(reverse=True)

#     derniere_cle = cles_paiement[0]

#     if derniere_cle != cle_soumise:
#         print()
#         print()
#         print(derniere_cle, cle_soumise)
#         print()
#         print()
#         return False, "Seule la dernière transaction peut être retournée"

#     # Récupération du Log lié à la clé
#     last_key = data.last_paiement_key
#     log_entry = data.db.query(Log).filter(Log.paiement_key == last_key).first()

#     if not log_entry:
#         return False, "Aucun historique (log) trouvé pour cette transaction"

#     # Nettoyage du champ 'mois'
#     # On itère sur les éléments payés dans cette transaction pour les retirer du relevé global
#     items_to_remove = info_paiement[derniere_cle]
#     if 'mois' in paiement_details:
#         for key in items_to_remove:
#             if key in paiement_details['mois']:
#                 # On supprime des deux références (relevé et champ mois principal)
#                 data_month_field.get('mois', {}).pop(key, None)
#                 paiement_details['mois'].pop(key, None)

#     # Mise à jour du statut en 'retourné' (équivalent du remboursement)
#     old_status = info_paiement[derniere_cle].get('status_paiement')
    
#     info_paiement[derniere_cle].update({
#         "status": "retourné",
#         "status_paiement": {
#             "etat": "retourné",
#             "date": datetime.now().isoformat(),
#             "motif": "raison du remboursement",
#             "last_status": old_status
#         },
#         "return_by_id": str(current_user.id),
#         "return_by": current_user.name,
#         "date_created": derniere_cle,
#         "date_retour": datetime.now().strftime("%d %b %Y -- %H:%M:%S"),
#         "commentaire": "raison du remboursement"
#     })

#     return True, "Succès"

def supprimer_dernier_paiement(paiement_details: dict, cle_soumise: str, data, data_month_field: dict, current_user, raison: str, authorized_by: Optional[str] = None):
    info_paiement = paiement_details.get('info_paiement', {})

    if not info_paiement:
        return False, "Aucune information de paiement trouvée"

    if cle_soumise not in info_paiement:
        return False, "Clé de paiement introuvable"

    # ✅ FIX 1 : Parser robuste couvrant tous les formats réels de vos clés
    def parse_cle(cle):
        for fmt in ("%d-%m-%Y %H:%M", "%d-%m-%Y %H:%M:%S", "%d-%m-%Y -- %H:%M:%S", "%d-%m-%Y"):
            try:
                return datetime.strptime(cle, fmt)
            except ValueError:
                continue
        raise ValueError(f"Format de clé non reconnu : {cle!r}")

    cles_paiement = list(info_paiement.keys())
    try:
        cles_paiement.sort(key=parse_cle, reverse=True)
    except ValueError as e:
        print(f"[WARN] Tri par date échoué : {e} — tri alphabétique utilisé")
        cles_paiement.sort(reverse=True)

    derniere_cle = cles_paiement[0]

    if derniere_cle != cle_soumise:
        print(f"[WARN] Clé soumise     : {cle_soumise!r}")
        print(f"[WARN] Dernière clé    : {derniere_cle!r}")
        return False, "Seule la dernière transaction peut être retournée"

    # ✅ FIX 2 : Vérifier que la transaction n'est pas déjà retournée
    transaction = info_paiement[derniere_cle]
    if transaction.get('status') == 'retourné':
        return False, "Cette transaction a déjà été retournée"

    # Récupération du log lié à la clé
    last_key = data.last_paiement_key
    log_entry = data.db.query(Log).filter(Log.paiement_key == last_key).first()

    if not log_entry:
        return False, "Aucun historique (log) trouvé pour cette transaction"

    # ✅ FIX 3 : items_to_remove doit être un dict — guard si c'est autre chose
    items_to_remove = transaction if isinstance(transaction, dict) else {}

    if 'mois' in paiement_details:
        for key in items_to_remove:
            if key in paiement_details['mois']:
                # d=data_month_field.get('mois', {})
                # print(d)
                # pass
                data_month_field.get('mois', {}).pop(key, None)
                paiement_details['mois'].pop(key, None)

    # ✅ FIX 4 : old_status récupéré depuis transaction (pas info_paiement[derniere_cle] qui est la même chose,
    #            mais c'est plus lisible et évite une double lookup)
    old_status = transaction.get('status_paiement')

    now = datetime.now()

    # ✅ FIX 5 : update sur transaction (référence locale) — plus lisible, même effet
    transaction.update({
        "status": "retourné",
        "status_paiement": {
            "etat": "retourné",
            "date": now.isoformat(),
            "motif": raison,
            "last_status": old_status
        },
        "return_by_id": str(current_user.id),
        "return_by": current_user.name,
        "date_created": derniere_cle,
        "date_retour": now.strftime("%d %b %Y -- %H:%M:%S"),
        "commentaire": raison,
        # Renseigné uniquement si un admin/Comptable a dû approuver l'action
        # pour un rôle qui n'a pas lui-même la permission (PIN ou autorisation-
        # access classique) — distinct de return_by, qui reste toujours
        # l'auteur réel de la demande.
        "authorized_by": authorized_by,
    })

    return True, "Succès"

router_return = APIRouter(prefix="/api/v1", tags=["Paiements"])

@router_return.post("/delete-paiement")
async def delete_last_paiement(
    req: DeletePaiementRequest,
    db: Session = Depends(get_db),
    # Pas de require_role ici : DualAuthChecker est le seul garde-fou — un
    # rôle sans la permission "Supprimer paiement" reçoit un 202 et peut
    # obtenir l'approbation d'un admin/Comptable via /auth/autorisation-
    # access-pin, plutôt qu'être bloqué avant même d'avoir une chance de
    # demander cette approbation.
    auth_data: dict = Depends(DualAuthChecker("Supprimer paiement")),
):
    # 1. Vérifier si le paiement existe
    # current_user: User = Depends(get_current_user),
    data = db.query(Paiement).filter(Paiement.id == req.id).first()
    # print(data.__dict__)
    if not data:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    current_user = auth_data["user_id"]
    current_admin = auth_data["admin_id"]

    UserContext.set_user_id(current_user)
    AdminAuthorization.set_admin_id(current_admin)
    ReasonContext.set_reason(req.raison)

    user = db.query(User).filter(User.id == current_user).first()
    admin_user = db.query(User).filter(User.id == current_admin).first() if current_admin else None
    ActionContext.set_action('retourné')
    try:
        # Décoder les champs JSON
        data_payment = parse_json(data.paiement_details)
        data_month_field = parse_json(data.mois)

        # Injection de la db dans l'objet pour la fonction utilitaire (similaire à Laravel)
        data.db = db

        if req.index:
            print(req.index)
            # Appel de la logique de suppression
            # Note: En Python, les dict sont passés par référence, donc modifiés in-place
            success, message = supprimer_dernier_paiement(
                data_payment['paiement_details'],
                req.index,
                data,
                data_month_field,
                user,
                req.raison,
                admin_user.name if admin_user else None,
            )

            if not success:
                raise HTTPException(status_code=422, detail=message)

            # 2. Sauvegarder les modifications
            new_p_key = str(uuid.uuid4())
            # data.last_paiement_key = new_p_key
            # data.paiement_details = data_payment
            # data.mois = data_month_field

            from sqlalchemy.orm.attributes import flag_modified

            data.last_paiement_key = new_p_key
            data.paiement_details = data_payment
            data.mois = data_month_field

            flag_modified(data, "paiement_details")
            flag_modified(data, "mois")

 
            db.commit()
            db.refresh(data)

            return {"message": "Le paiement a été marqué comme retourné avec succès", "last_key": new_p_key}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))