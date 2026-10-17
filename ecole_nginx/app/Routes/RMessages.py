# app/Routes/RMessages.py — messagerie interne + WebSocket temps réel
"""Conversations 1-à-1 entre comptes users (voir app/Models/MMessages.py).

Qui peut écrire à qui (_contact_ids) :
- Personnel (administration) : tout le monde ;
- Professeur : le personnel, les autres professeurs, et les étudiants de ses
  classes pour l'année active ;
- Étudiant : le personnel et les professeurs de ses classes (année active).
On peut toujours répondre à quelqu'un qui nous a écrit.

Temps réel : WebSocket /api/v1/ws/messages?token=<jwt> (le navigateur ne
peut pas poser d'en-tête Authorization sur une WebSocket), alimentée par
app/services/message_realtime.py."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.database import SessionLocal, get_db
from app.dependencies.Dependencie import get_current_user
from app.Models.MMessages import Message
from app.Models.MModels import AnneeAcademique, Etudiant, Professeur, User
from app.Models.MRelations import ClasseEtudiant, Programme
from app.Models.MSystems import Personnel
from app.services.message_realtime import hub, serialize_message

router = APIRouter(prefix="/api/v1/messages", tags=["Messagerie"])
ws_router = APIRouter(prefix="/api/v1/ws", tags=["Messagerie"])

PROF = "App\\Models\\Professeur"
ETUDIANT = "App\\Models\\Etudiant"
PERSONNEL = "App\\Models\\Personnel"
ROLE_LABELS = {PROF: "Professeur", ETUDIANT: "Étudiant", PERSONNEL: "Administration"}
MAX_BODY = 5000


class MessageCreate(BaseModel):
    recipient_id: str
    body: str

    @field_validator("body")
    @classmethod
    def body_non_vide(cls, v):
        v = (v or "").strip()
        if not v:
            raise ValueError("Le message ne peut pas être vide")
        if len(v) > MAX_BODY:
            raise ValueError(f"Le message ne peut pas dépasser {MAX_BODY} caractères")
        return v


def _display_names(db: Session, users) -> dict:
    """{user_id: "Prénom Nom"} à partir de la fiche liée (User.name ne
    contient souvent que le prénom)."""
    par_type = {}
    for u in users:
        par_type.setdefault(u.userable_type, []).append(u.userable_id)
    fiches = {}
    for type_, model in ((PROF, Professeur), (ETUDIANT, Etudiant), (PERSONNEL, Personnel)):
        ids = par_type.get(type_)
        if ids:
            for f in db.query(model.id, model.prenom, model.nom).filter(model.id.in_(ids)).all():
                fiches[(type_, f.id)] = f"{f.prenom or ''} {f.nom or ''}".strip()
    return {
        u.id: fiches.get((u.userable_type, u.userable_id)) or u.name or u.username or u.email
        for u in users
    }


def _user_view(u: User, names: dict) -> dict:
    return {
        "id": u.id,
        "name": names.get(u.id) or u.name,
        "email": u.email,
        "role": ROLE_LABELS.get(u.userable_type, "Utilisateur"),
    }


def _contact_ids(db: Session, me: User) -> Optional[set]:
    """Ids des users joignables par `me`, ou None = tout le monde."""
    if me.userable_type == PERSONNEL:
        return None

    annee = db.query(AnneeAcademique).filter(AnneeAcademique.status == 1).first()
    staff = {u.id for u in db.query(User.id).filter(User.userable_type == PERSONNEL).all()}
    ids = set(staff)

    if me.userable_type == PROF:
        ids |= {u.id for u in db.query(User.id).filter(User.userable_type == PROF).all()}
        if annee:
            classes = db.query(Programme.class_).filter(
                Programme.professeur_id == me.userable_id,
                Programme.annee_academique == annee.id,
            ).distinct()
            etudiants = db.query(ClasseEtudiant.etudiant_id).filter(
                ClasseEtudiant.classes_id.in_(classes),
                ClasseEtudiant.annee_academique_id == annee.id,
            )
            ids |= {u.id for u in db.query(User.id).filter(
                User.userable_type == ETUDIANT, User.userable_id.in_(etudiants)
            ).all()}
    elif me.userable_type == ETUDIANT and annee:
        classes = db.query(ClasseEtudiant.classes_id).filter(
            ClasseEtudiant.etudiant_id == me.userable_id,
            ClasseEtudiant.annee_academique_id == annee.id,
        )
        profs = db.query(Programme.professeur_id).filter(
            Programme.class_.in_(classes), Programme.annee_academique == annee.id
        )
        ids |= {u.id for u in db.query(User.id).filter(
            User.userable_type == PROF, User.userable_id.in_(profs)
        ).all()}

    ids.discard(me.id)
    return ids


def _peut_ecrire(db: Session, me: User, dest_id: str) -> bool:
    contacts = _contact_ids(db, me)
    if contacts is None or dest_id in contacts:
        return True
    # Répondre à quelqu'un qui nous a déjà écrit
    return db.query(Message.id).filter(
        Message.sender_id == dest_id, Message.recipient_id == me.id
    ).first() is not None


@router.get("/contacts")
def list_contacts(
    q: str = Query("", max_length=100),
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    query = db.query(User).filter(User.id != me.id, User.status != "0")
    contacts = _contact_ids(db, me)
    if contacts is not None:
        if not contacts:
            return {"contacts": []}
        query = query.filter(User.id.in_(contacts))
    users = query.all()
    names = _display_names(db, users)
    terme = q.strip().lower()
    result = [
        _user_view(u, names) for u in users
        if not terme or terme in (names.get(u.id) or "").lower() or terme in (u.email or "").lower()
    ]
    result.sort(key=lambda c: (c["role"], c["name"].lower()))
    return {"contacts": result[:50]}


@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    autre = case((Message.sender_id == me.id, Message.recipient_id), else_=Message.sender_id)
    derniers = (
        db.query(autre.label("autre_id"), func.max(Message.id).label("last_id"))
        .filter(or_(Message.sender_id == me.id, Message.recipient_id == me.id))
        .group_by(autre)
        .all()
    )
    if not derniers:
        return {"conversations": [], "unread_total": 0}

    last_ids = [r.last_id for r in derniers]
    messages = {m.id: m for m in db.query(Message).filter(Message.id.in_(last_ids)).all()}
    non_lus = dict(
        db.query(Message.sender_id, func.count(Message.id))
        .filter(Message.recipient_id == me.id, Message.read_at.is_(None))
        .group_by(Message.sender_id)
        .all()
    )
    users = db.query(User).filter(User.id.in_([r.autre_id for r in derniers])).all()
    names = _display_names(db, users)
    users_by_id = {u.id: u for u in users}

    conversations = []
    for r in derniers:
        u = users_by_id.get(r.autre_id)
        if not u:
            continue
        conversations.append({
            "user": _user_view(u, names),
            "last_message": serialize_message(messages[r.last_id]),
            "unread": non_lus.get(r.autre_id, 0),
        })
    conversations.sort(key=lambda c: c["last_message"]["id"], reverse=True)
    return {"conversations": conversations, "unread_total": sum(non_lus.values())}


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    n = db.query(func.count(Message.id)).filter(
        Message.recipient_id == me.id, Message.read_at.is_(None)
    ).scalar()
    return {"unread": n or 0}


@router.get("/with/{user_id}")
def get_thread(
    user_id: str,
    before_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    me: User = Depends(get_current_user),
):
    autre = db.query(User).filter(User.id == user_id).first()
    if not autre:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    query = db.query(Message).filter(or_(
        and_(Message.sender_id == me.id, Message.recipient_id == user_id),
        and_(Message.sender_id == user_id, Message.recipient_id == me.id),
    ))
    if before_id:
        query = query.filter(Message.id < before_id)
    rows = query.order_by(Message.id.desc()).limit(limit).all()

    names = _display_names(db, [autre])
    return {
        "user": _user_view(autre, names),
        "messages": [serialize_message(m) for m in reversed(rows)],
        "has_more": len(rows) == limit,
    }


@router.post("/with/{user_id}/read")
def mark_read(user_id: str, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    n = db.query(Message).filter(
        Message.sender_id == user_id,
        Message.recipient_id == me.id,
        Message.read_at.is_(None),
    ).update({Message.read_at: datetime.utcnow()}, synchronize_session=False)
    db.commit()
    return {"marked": n}


@router.post("")
def send_message(data: MessageCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    if data.recipient_id == me.id:
        raise HTTPException(status_code=400, detail="Impossible de s'envoyer un message à soi-même")
    dest = db.query(User).filter(User.id == data.recipient_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destinataire introuvable")
    if not _peut_ecrire(db, me, dest.id):
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas écrire à ce destinataire")

    msg = Message(sender_id=me.id, recipient_id=dest.id, body=data.body)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    # La diffusion WebSocket se fait via le hub (sondage de la table), sur
    # tous les workers — rien d'autre à faire ici.
    return {"message": serialize_message(msg)}


def _user_from_token(token: str) -> Optional[User]:
    """Même validation que get_current_user (blacklist + JWT), hors
    dépendance FastAPI."""
    db = SessionLocal()
    try:
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = get_current_user(credentials=creds, db=db)
        db.expunge(user)
        return user
    except HTTPException:
        return None
    finally:
        db.close()


@ws_router.websocket("/messages")
async def messages_ws(websocket: WebSocket, token: str = Query("")):
    user = await run_in_threadpool(_user_from_token, token) if token else None
    # accept() puis close(4401) plutôt qu'un refus de handshake : le
    # navigateur ne voit qu'un code 1006 sur un refus et réessaierait sans
    # fin ; 4401 dit au client (useMessages.js) d'arrêter.
    await websocket.accept()
    if not user:
        await websocket.close(code=4401)
        return

    await hub.connect(user.id, websocket)
    try:
        while True:
            # Le client envoie "ping" régulièrement : garde la connexion
            # ouverte à travers nginx (proxy_read_timeout)
            if await websocket.receive_text() == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        hub.disconnect(user.id, websocket)
