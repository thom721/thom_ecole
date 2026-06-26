from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request,status
from sqlalchemy.orm import Session   
from fastapi.responses import JSONResponse
import hashlib
import hmac
from sqlalchemy import or_
from app.Models.MSystems import ClientInfo
from app.database import get_db
from pydantic import BaseModel
from typing import Optional, List  
from app.Models.MModels import User 
from app.Models.MSystems import ClientInfo, HeartAuto ,LogActive
import random
import string
import json
from app.Schemas.SClientInfos import *
from app.Helper.context import UserContext,ActionContext
from sqlalchemy import asc, desc
from app.services.ServiceAuth import AuthorizationService
import sys

from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role

router = APIRouter(prefix="/api/v1", tags=["Authorisation"])

class ActiveLogCreate(BaseModel):
    last_key: Optional[str] = None
    new_key: str
    exprired_at: str  # Tu peux mettre datetime si tu envoies un format ISO
    # Si ton API réclame email/password (vu l'erreur 422 précédente), ajoute-les :
    # email: str
    # password: str


class ApplyLicenceIn(BaseModel):
    new_key: str
    expiration_date: str
    days_valid: Optional[int] = None
  
@router.post("/log-activate")
async def store_log_activate(data: ActiveLogCreate, db: Session = Depends(get_db)):
    # 1. Récupérer le premier utilisateur (équivalent de User::first())
    ActionContext.set_action("Connect Autorisation")
    first_user = db.query(User).order_by(asc(User.created_at)).first()
    if not first_user:
        raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé")

    try:
        # 2. Préparer les données (équivalent de create($dataValid))
        new_log = LogActive(
            last_key=data.last_key,
            new_key=data.new_key,
            exprired_at=data.exprired_at,
            user_id=first_user.id
        )
        
        db.add(new_log)
        get_all_user(22,db)
        db.commit()
        db.refresh(new_log)

        return {"success": "success"}

    except Exception as e:
        db.rollback()
        # On renvoie une 422 pour rester cohérent avec ton code Laravel
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/licence/appliquer")
def appliquer_licence(
    data: ApplyLicenceIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Enregistre localement (log_actives + stockage local de licence) une clé
    émise par infini-software après un paiement de renouvellement réussi.
    Appelé par school_client (modèle "pull" : infini-software ne peut pas
    appeler directement ce serveur, voir docs/infini-software-PRD.md) après
    avoir constaté via GET /api/licence/derniere-cle qu'une clé plus récente
    existe que celle actuellement affichée par /api/v1/abonnement. Réservé
    aux administrateurs.
    """
    if not user_has_role(current_user, ['admin'], db):
        raise HTTPException(status_code=403, detail="Réservé aux administrateurs.")

    ActionContext.set_action("Connect Autorisation")
    first_user = db.query(User).order_by(asc(User.created_at)).first()
    if not first_user:
        raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé")

    dernier_log = db.query(LogActive).order_by(desc(LogActive.created_at)).first()

    # Stockage local de licence (fichier chiffré Mac/Linux, ou registre
    # Windows via QSettings — deux modules séparés, voir docs/ecole_nginx.md)
    # AVANT le commit en base : si cette étape échoue, /api/v1/abonnement
    # (qui lit log_actives) ne doit PAS se mettre à dire "Actif" alors que la
    # licence locale n'a en réalité pas été enregistrée — sinon
    # LicenceSyncWorker (school_client), qui ne redéclenche cet appel que si
    # la clé d'infini-software diffère de log_actives.new_key, ne retenterait
    # plus jamais l'écriture locale après cet échec.
    if sys.platform == "win32":
        from Helper.server_key_generate import apply_remote_licence
    else:
        from app.Helper.license_check import apply_remote_licence
    try:
        apply_remote_licence(data.new_key, data.expiration_date, data.days_valid)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Échec de l'enregistrement local de la licence : {e}",
        )

    new_log = LogActive(
        last_key=dernier_log.new_key if dernier_log else None,
        new_key=data.new_key,
        exprired_at=data.expiration_date,
        user_id=first_user.id,
    )
    db.add(new_log)
    db.commit()

    return {"success": True}


@router.post("/client-authorisation-connect", response_model=AuthorisationResponse)
def authorisation(
    data: dict,
    db: Session = Depends(get_db)
):
    id = data.get("id")
    certi_key = data.get("certi_key")
    client_mac = data.get("client_mac")
    client_name = data.get("client_name")
    username = data.get("email")
    password = data.get("password")
    login_as = data.get("login_as")

    # Récupère l'utilisateur ayant la date de création la plus ancienne
    # UserContext.set_user_id(user.id)
    ActionContext.set_action("Connect Autorisation")
    try:
        if id:
            user = db.query(User).order_by(asc(User.created_at)).first()
            client = db.query(ClientInfo).filter(ClientInfo.id == id).first()
            if not client:
                raise HTTPException(status_code=404, detail="Client non trouvé")
            
            if not username:
                raise HTTPException(status_code=422, detail="Vous devez indique votre information de connection pour effectuer cette action",headers={"Authorisation":"fales"})
            
            if not user_has_permission(user, "Modifier personnel", db) and not user_has_role(user,['admin'],db):
                raise HTTPException(status_code=401, detail="Vous n\'avez pas les permissions requise.")
            
            users = AuthorizationService.find_user_by_credentials(db, username, password,login_as)

            if not users:
                raise HTTPException(
                    status_code=401,
                    detail="Les informations de connexion sont incorrectes",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            client.authorisation = not client.authorisation
            if certi_key:
                client.certi_key = certi_key

            db.add(client)
            db.commit()
            db.refresh(client)

            return {
                "success": "Autorisation modifiée",
                "authorisation": client.authorisation,
                "id": client.id
            }

        if not client_mac or not client_name:
            raise HTTPException(status_code=422, detail="client_mac et client_name sont requis")

        client = db.query(ClientInfo).filter(ClientInfo.client_mac == client_mac).first()
        if client:
            client.client_name = client_name
            if certi_key:
                client.certi_key = certi_key
        else:
            client = ClientInfo(
                client_mac=client_mac,
                client_name=client_name,
                certi_key=certi_key
            )
            db.add(client)

        db.commit()
        db.refresh(client)

        return {
            "success": "Client enregistré",
            "authorisation": client.authorisation,
            "id": client.id
        }

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


# --------------------------
# 2️⃣ Liste de tous les clients
# --------------------------
@router.get("/client-authorisation-connect", response_model=ClientListResponse)
def get_authorisation(db: Session = Depends(get_db)):
    clients = db.query(ClientInfo).all()
    return {"data_client": clients}

# 84:A6:C8:F3:D5:B8
# B4:B5:2F:7F:F6:AF
# --------------------------
# 3️⃣ Récupérer client par MAC
# --------------------------
# @router.get("/client-authorisation-connect/{mac_address}", response_model=AskingResponse)
# def get_authorisation_mac(mac_address: str, db: Session = Depends(get_db)):
#     client = db.query(ClientInfo).filter(ClientInfo.client_mac == mac_address).first()
#     if not client:
#         raise HTTPException(status_code=404, detail="Client non trouvé")
#     return {"status":1,"data":client,"certy_ss":""}

@router.get("/client-authorisation-connect/{mac_address}", response_model=AskingResponse)
def get_authorisation_mac(mac_address: str, db: Session = Depends(get_db)):
    client = db.query(ClientInfo).filter(ClientInfo.client_mac == mac_address).first()
    
    if not client:
        return AskingResponse(
            status=404,
            data={"error": "Client non trouvé"},
            certy_ss=None
        )
    
    # Si data doit être un dict, convertissez le client
    client_dict = {
        "id": client.id,
        "client_mac": client.client_mac,
        "authorisation": client.authorisation,
        "client_name": client.client_name,
     #    "nom_user": client.nom_user,
        "status": 1,
        # ... autres champs
    }
    
    # Si certy_ss est censé être un dict, assurez-vous qu'il ne soit pas une string vide
    certy_ss_data = client.ss_certi if isinstance(client.ss_certi, dict) else None
#     certy_key_data = client.ss_certi if isinstance(client.ss_certi, dict) else None
    
    return AskingResponse(
        status=1,
        data=client_dict,  # Maintenant un dict
        certy_ss=certy_ss_data  # None ou un dict
    )

# client_name
# authorisation
# certi_key
# ss_certi

# --------------------------
# 4️⃣ Récupérer certi_key et ss_certi
# --------------------------
@router.get("/asking", response_model=AskingResponse)
def asking(mac_address: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    client = db.query(ClientInfo).filter(ClientInfo.client_mac == mac_address).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    if client.certi_key:
        return {
            "status": 1,
            "data": client.certi_key,
            "certy_ss": client.ss_certi
        }
    else:
        return {
            "status": 0,
            "data": "",
            "certy_ss": client.ss_certi
        }

@router.put("/ap/v1/update-user", response_model=List[ClientInfoSchema])
def update_certificat(
    certi_key: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Met à jour le certi_key de tous les clients qui en ont déjà un.
    """
    client = db.query(User).order_by(asc(User.created_at)).first()
    UserContext.set_user_id(client.id)
    ActionContext.set_action("Connect Autorisation")
    try:
        # Récupérer tous les clients qui ont déjà un certi_key
        clients = db.query(ClientInfo).filter(ClientInfo.certi_key.isnot(None)).all()

        for client in clients:
            client.certi_key = certi_key
            db.add(client)

        db.commit()

        # Retourner la liste mise à jour
        updated_clients = db.query(ClientInfo).filter(ClientInfo.certi_key.isnot(None)).all()
        return updated_clients

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    

 
# Fonction équivalente getAlluser
# --------------------------
def get_all_user(int_value: int, db: Session):
    # Récupérer les utilisateurs qui ne sont pas des étudiants
    users = db.query(User).filter(User.userable_type != "App\Models\Etudiant").all()

    letters = ''.join(random.choices(string.ascii_lowercase, k=2))

    for user in users:
        parts = user.id.split("-")
        parts[1] = f"{parts[1]}-{int_value}{letters}"
        new_client_infos = "-".join(parts)

        user.client_infos = new_client_infos
        db.add(user)

        # HeartAuto updateOrCreate
        heart = db.query(HeartAuto).filter(HeartAuto.user_id == user.id).first()
        if heart:
            heart.descript = f"{user.id}--{int_value}"
        else:
            heart = HeartAuto(user_id=user.id, descript=f"{user.id}--{int_value}")
            db.add(heart)

    db.commit()


# --------------------------
# Endpoint équivalent store
# --------------------------
@router.post("/activate-state")
def store(
    status: int = Body(...),
    ssl_ca: str = Body(...),
    ssl_cert: str = Body(...),
    ssl_key: str = Body(...),
    db: Session = Depends(get_db)
):
    client = db.query(User).order_by(asc(User.created_at)).first()
    UserContext.set_user_id(client.id)
    ActionContext.set_action("Connect Autorisation")

    if not isinstance(status, int):
        raise HTTPException(status_code=422, detail="status doit être numérique")

    # Appel de la fonction get_all_user
    get_all_user(status, db)

    # Mettre à jour ss_certi des clients
    try:
        clients = db.query(ClientInfo).filter(ClientInfo.ss_certi.is_(None)).all()
        for client in clients:
            client.ss_certi = {
                "ssl_ca": ssl_ca,
                "ssl_cert": ssl_cert,
                "ssl_key": ssl_key,
            }
            db.add(client)
        db.commit()

    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {"success": True, "message": "Clients mis à jour avec ss_certi"}


