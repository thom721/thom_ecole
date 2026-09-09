from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MUser import User
from app.Models.MNotification import NotificationKind
from app.Models.MMessaging import (
    Conversation, ConversationMember, Message, MessageUserAction, ConversationUserAction,
    Contact, ContactRequest, BlockedUser,
    ConversationType, MessageActionType, ConversationActionType,
)
from app.Schemas.SMessaging import (
    ConversationSummaryOut, ConversationStartIndividualIn, ConversationStartGroupIn,
    ConversationDetailOut, MessageOut, MessageCreate, UserLookupOut,
    ContactOut, ContactRequestCreate, ContactRequestOut, PrivacyUpdate,
)
from app.dependencies.auth import get_current_active_user
from app.Helper.notifications import notify
from app.Helper.messaging import can_start_conversation, are_contacts, is_blocked

router = APIRouter(prefix="/messaging", tags=["messaging"])


def _conv_hash(user_a_id: str, user_b_id: str) -> str:
    return "-".join(sorted([user_a_id, user_b_id]))


def _get_member_or_403(db: Session, conversation_id: str, user_id: str) -> Conversation:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation introuvable")
    is_member = db.query(ConversationMember).filter(
        ConversationMember.conversation_id == conversation_id, ConversationMember.user_id == user_id,
    ).first()
    if is_member is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas membre de cette conversation")
    return conversation


@router.get("/conversations", response_model=list[ConversationSummaryOut])
def list_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    memberships = db.query(ConversationMember).filter(ConversationMember.user_id == current_user.id).all()
    out = []
    for m in memberships:
        conversation = m.conversation
        last_message = conversation.messages[-1] if conversation.messages else None

        deleted_ids = {
            a.message_id for a in
            db.query(MessageUserAction).filter(
                MessageUserAction.user_id == current_user.id, MessageUserAction.action == MessageActionType.deleted,
                MessageUserAction.message_id.in_([msg.id for msg in conversation.messages]),
            ).all()
        } if conversation.messages else set()
        read_ids = {
            a.message_id for a in
            db.query(MessageUserAction).filter(
                MessageUserAction.user_id == current_user.id, MessageUserAction.action == MessageActionType.read,
                MessageUserAction.message_id.in_([msg.id for msg in conversation.messages]),
            ).all()
        } if conversation.messages else set()
        unread_count = sum(
            1 for msg in conversation.messages
            if msg.sender_id != current_user.id and msg.id not in read_ids and msg.id not in deleted_ids
        )

        muted = db.query(ConversationUserAction).filter(
            ConversationUserAction.conversation_id == conversation.id, ConversationUserAction.user_id == current_user.id,
            ConversationUserAction.action == ConversationActionType.muted,
        ).first() is not None

        other_user_id = None
        if conversation.type == ConversationType.individual:
            other = next((mm for mm in conversation.members if mm.user_id != current_user.id), None)
            other_user_id = other.user_id if other else None

        out.append(ConversationSummaryOut(
            id=conversation.id, type=conversation.type, name=conversation.name, other_user_id=other_user_id,
            last_message=(last_message.content if last_message and last_message.id not in deleted_ids else None),
            last_message_at=last_message.created_at if last_message else None,
            unread_count=unread_count, muted=muted,
        ))
    out.sort(key=lambda c: c.last_message_at or datetime.min, reverse=True)
    return out


@router.post("/conversations/individual", response_model=ConversationSummaryOut, status_code=status.HTTP_201_CREATED)
def start_individual_conversation(
    data: ConversationStartIndividualIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if data.other_user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Impossible de démarrer une conversation avec soi-même")
    recipient = db.query(User).filter(User.id == data.other_user_id).first()
    if recipient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")

    conv_hash = _conv_hash(current_user.id, recipient.id)
    existing = db.query(Conversation).filter(Conversation.conv_hash == conv_hash).first()
    if existing is not None:
        return ConversationSummaryOut(id=existing.id, type=existing.type, name=existing.name, other_user_id=recipient.id)

    allowed, reason = can_start_conversation(db, current_user, recipient)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)

    conversation = Conversation(type=ConversationType.individual, conv_hash=conv_hash)
    db.add(conversation)
    db.flush()
    db.add(ConversationMember(conversation_id=conversation.id, user_id=current_user.id))
    db.add(ConversationMember(conversation_id=conversation.id, user_id=recipient.id))
    db.commit()
    db.refresh(conversation)
    return ConversationSummaryOut(id=conversation.id, type=conversation.type, name=conversation.name, other_user_id=recipient.id)


@router.post("/conversations/group", response_model=ConversationSummaryOut, status_code=status.HTTP_201_CREATED)
def start_group_conversation(
    data: ConversationStartGroupIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    member_ids = set(data.member_ids) | {current_user.id}
    if len(member_ids) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une conversation de groupe nécessite au moins 2 membres")

    conversation = Conversation(type=ConversationType.group, name=data.name)
    db.add(conversation)
    db.flush()
    for uid in member_ids:
        db.add(ConversationMember(conversation_id=conversation.id, user_id=uid))
    db.commit()
    db.refresh(conversation)
    return ConversationSummaryOut(id=conversation.id, type=conversation.type, name=conversation.name)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    conversation = _get_member_or_403(db, conversation_id, current_user.id)

    deleted_ids = {
        a.message_id for a in
        db.query(MessageUserAction).filter(
            MessageUserAction.user_id == current_user.id, MessageUserAction.action == MessageActionType.deleted,
        ).all()
    }
    visible_messages = [m for m in conversation.messages if m.id not in deleted_ids]

    # Marque lus en effet de bord (même patron que ForumReadState, Phase 4).
    for m in visible_messages:
        if m.sender_id == current_user.id:
            continue
        already_read = db.query(MessageUserAction).filter(
            MessageUserAction.message_id == m.id, MessageUserAction.user_id == current_user.id,
            MessageUserAction.action == MessageActionType.read,
        ).first()
        if already_read is None:
            db.add(MessageUserAction(message_id=m.id, user_id=current_user.id, action=MessageActionType.read))
    db.commit()

    muted = db.query(ConversationUserAction).filter(
        ConversationUserAction.conversation_id == conversation_id, ConversationUserAction.user_id == current_user.id,
        ConversationUserAction.action == ConversationActionType.muted,
    ).first() is not None

    return ConversationDetailOut(
        id=conversation.id, type=conversation.type, name=conversation.name,
        member_ids=[m.user_id for m in conversation.members], muted=muted,
        messages=[MessageOut.model_validate(m) for m in visible_messages],
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(
    conversation_id: str, data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    conversation = _get_member_or_403(db, conversation_id, current_user.id)

    message = Message(conversation_id=conversation_id, sender_id=current_user.id, content=data.content)
    db.add(message)
    db.commit()
    db.refresh(message)

    for member in conversation.members:
        if member.user_id == current_user.id:
            continue
        notify(db, member.user_id, NotificationKind.new_message,
               title=f"Nouveau message de {current_user.first_name} {current_user.last_name}",
               body=data.content[:200], link_url=f"/messages?conversation={conversation_id}")

    return message


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message_for_me(
    message_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message introuvable")
    _get_member_or_403(db, message.conversation_id, current_user.id)

    existing = db.query(MessageUserAction).filter(
        MessageUserAction.message_id == message_id, MessageUserAction.user_id == current_user.id,
        MessageUserAction.action == MessageActionType.deleted,
    ).first()
    if existing is None:
        db.add(MessageUserAction(message_id=message_id, user_id=current_user.id, action=MessageActionType.deleted))
        db.commit()


@router.post("/conversations/{conversation_id}/mute", status_code=status.HTTP_204_NO_CONTENT)
def mute_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _get_member_or_403(db, conversation_id, current_user.id)
    existing = db.query(ConversationUserAction).filter(
        ConversationUserAction.conversation_id == conversation_id, ConversationUserAction.user_id == current_user.id,
        ConversationUserAction.action == ConversationActionType.muted,
    ).first()
    if existing is None:
        db.add(ConversationUserAction(conversation_id=conversation_id, user_id=current_user.id, action=ConversationActionType.muted))
        db.commit()


@router.delete("/conversations/{conversation_id}/mute", status_code=status.HTTP_204_NO_CONTENT)
def unmute_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _get_member_or_403(db, conversation_id, current_user.id)
    db.query(ConversationUserAction).filter(
        ConversationUserAction.conversation_id == conversation_id, ConversationUserAction.user_id == current_user.id,
        ConversationUserAction.action == ConversationActionType.muted,
    ).delete()
    db.commit()


@router.get("/unread-count")
def unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    memberships = db.query(ConversationMember).filter(ConversationMember.user_id == current_user.id).all()
    total = 0
    for m in memberships:
        deleted_ids = {
            a.message_id for a in db.query(MessageUserAction).filter(
                MessageUserAction.user_id == current_user.id, MessageUserAction.action == MessageActionType.deleted,
            ).all()
        }
        read_ids = {
            a.message_id for a in db.query(MessageUserAction).filter(
                MessageUserAction.user_id == current_user.id, MessageUserAction.action == MessageActionType.read,
            ).all()
        }
        total += sum(
            1 for msg in m.conversation.messages
            if msg.sender_id != current_user.id and msg.id not in read_ids and msg.id not in deleted_ids
        )
    return {"count": total}


@router.get("/lookup", response_model=UserLookupOut)
def lookup_user(
    email: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Ouvert à tout authentifié (contrairement à /users/lookup) mais ne
    renvoie jamais un utilisateur que l'appelant n'a pas le droit de
    contacter — évite de confirmer l'existence d'un compte sans droit."""
    user = db.query(User).filter(User.email == email).first()
    if user is None or user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun utilisateur trouvé")
    allowed, _reason = can_start_conversation(db, current_user, user)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun utilisateur trouvé")
    return user


@router.get("/contacts", response_model=list[ContactOut])
def list_contacts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = db.query(Contact).filter(or_(Contact.user_id == current_user.id, Contact.contact_id == current_user.id)).all()
    return [
        ContactOut(id=c.id, user_id=c.user_id, contact_id=c.contact_id,
                   other_user_id=c.contact_id if c.user_id == current_user.id else c.user_id)
        for c in rows
    ]


@router.post("/contacts/requests", response_model=ContactRequestOut, status_code=status.HTTP_201_CREATED)
def send_contact_request(
    data: ContactRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if data.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Impossible de s'ajouter soi-même")
    if are_contacts(db, current_user.id, data.user_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà en contact")

    existing = db.query(ContactRequest).filter(
        or_(
            and_(ContactRequest.user_id == current_user.id, ContactRequest.requested_user_id == data.user_id),
            and_(ContactRequest.user_id == data.user_id, ContactRequest.requested_user_id == current_user.id),
        )
    ).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Une demande est déjà en cours")

    request = ContactRequest(user_id=current_user.id, requested_user_id=data.user_id)
    db.add(request)
    db.commit()
    db.refresh(request)
    return ContactRequestOut(id=request.id, user_id=request.user_id, requested_user_id=request.requested_user_id,
                              created_at=request.created_at, direction="outgoing")


@router.get("/contacts/requests", response_model=list[ContactRequestOut])
def list_contact_requests(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    incoming = db.query(ContactRequest).filter(ContactRequest.requested_user_id == current_user.id).all()
    outgoing = db.query(ContactRequest).filter(ContactRequest.user_id == current_user.id).all()
    return (
        [ContactRequestOut(id=r.id, user_id=r.user_id, requested_user_id=r.requested_user_id, created_at=r.created_at, direction="incoming") for r in incoming]
        + [ContactRequestOut(id=r.id, user_id=r.user_id, requested_user_id=r.requested_user_id, created_at=r.created_at, direction="outgoing") for r in outgoing]
    )


@router.post("/contacts/requests/{request_id}/accept", response_model=ContactOut)
def accept_contact_request(
    request_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    request = db.query(ContactRequest).filter(ContactRequest.id == request_id).first()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demande introuvable")
    if request.requested_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette demande ne vous est pas adressée")

    contact = Contact(user_id=request.user_id, contact_id=request.requested_user_id)
    db.add(contact)
    db.delete(request)
    db.commit()
    db.refresh(contact)
    return ContactOut(id=contact.id, user_id=contact.user_id, contact_id=contact.contact_id, other_user_id=contact.user_id)


@router.delete("/contacts/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def decline_or_cancel_contact_request(
    request_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    request = db.query(ContactRequest).filter(ContactRequest.id == request_id).first()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demande introuvable")
    if current_user.id not in (request.user_id, request.requested_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette demande ne vous concerne pas")
    db.delete(request)
    db.commit()


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_contact(
    contact_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact introuvable")
    if current_user.id not in (contact.user_id, contact.contact_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ce contact ne vous concerne pas")
    db.delete(contact)
    db.commit()


@router.get("/blocked", response_model=list[UserLookupOut])
def list_blocked(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    rows = db.query(BlockedUser).filter(BlockedUser.user_id == current_user.id).all()
    users = db.query(User).filter(User.id.in_([r.blocked_user_id for r in rows])).all() if rows else []
    return users


@router.post("/blocked/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def block_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Impossible de se bloquer soi-même")
    if not is_blocked(db, current_user.id, user_id):
        db.add(BlockedUser(user_id=current_user.id, blocked_user_id=user_id))
        db.commit()


@router.delete("/blocked/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unblock_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    db.query(BlockedUser).filter(BlockedUser.user_id == current_user.id, BlockedUser.blocked_user_id == user_id).delete()
    db.commit()


@router.patch("/privacy")
def update_privacy(
    data: PrivacyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    current_user.message_privacy = data.message_privacy
    db.commit()
    return {"message_privacy": current_user.message_privacy}
