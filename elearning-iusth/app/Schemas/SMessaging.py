from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MMessaging import ConversationType
from app.Models.MUser import MessagePrivacy


class ConversationSummaryOut(BaseModel):
    id: str
    type: ConversationType
    name: str | None = None
    other_user_id: str | None = None  # individuel uniquement — pratique pour l'affichage
    last_message: str | None = None
    last_message_at: datetime | None = None
    unread_count: int = 0
    muted: bool = False


class ConversationStartIndividualIn(BaseModel):
    other_user_id: str


class ConversationStartGroupIn(BaseModel):
    name: str
    member_ids: list[str]


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    conversation_id: str
    sender_id: str
    content: str
    created_at: datetime | None = None


class MessageCreate(BaseModel):
    content: str


class ConversationDetailOut(BaseModel):
    id: str
    type: ConversationType
    name: str | None = None
    member_ids: list[str]
    muted: bool = False
    messages: list[MessageOut] = []


class UserLookupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    first_name: str
    last_name: str
    email: str


class ContactOut(BaseModel):
    id: str
    user_id: str
    contact_id: str
    other_user_id: str  # l'autre extrémité de la relation, du point de vue de l'appelant


class ContactRequestCreate(BaseModel):
    user_id: str


class ContactRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    requested_user_id: str
    created_at: datetime | None = None
    direction: str  # "incoming" | "outgoing"


class PrivacyUpdate(BaseModel):
    message_privacy: MessagePrivacy
