import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class ConversationType(str, enum.Enum):
    individual = "individual"
    group = "group"


class MessageActionType(str, enum.Enum):
    read = "read"
    deleted = "deleted"


class ConversationActionType(str, enum.Enum):
    muted = "muted"


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    type = Column(SAEnum(ConversationType), nullable=False)
    name = Column(String(255), nullable=True)  # groupe uniquement
    # Paire d'ids triée — individuel uniquement, garantit la réutilisation
    # idempotente d'une conversation existante (voir plan Épic 11).
    conv_hash = Column(String(80), unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    members = relationship("ConversationMember", back_populates="conversation", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class ConversationMember(Base):
    __tablename__ = "conversation_members"
    __table_args__ = (
        UniqueConstraint("conversation_id", "user_id", name="uq_conversation_members_conversation_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="members")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")
    user_actions = relationship("MessageUserAction", back_populates="message", cascade="all, delete-orphan")


class MessageUserAction(Base):
    """Par utilisateur, par message — 'deleted' ne supprime jamais la
    ligne `Message` elle-même, seulement la visibilité pour CET
    utilisateur (voir plan Épic 11, comportement réel Moodle)."""

    __tablename__ = "message_user_actions"
    __table_args__ = (
        UniqueConstraint("message_id", "user_id", "action", name="uq_message_user_actions_message_user_action"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action = Column(SAEnum(MessageActionType), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    message = relationship("Message", back_populates="user_actions")


class ConversationUserAction(Base):
    __tablename__ = "conversation_user_actions"
    __table_args__ = (
        UniqueConstraint("conversation_id", "user_id", "action", name="uq_conversation_user_actions_conv_user_action"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action = Column(SAEnum(ConversationActionType), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Contact(Base):
    """Une seule ligne par paire de contacts acceptée (convention
    applicative — voir plan Épic 11, simplification assumée par rapport
    aux 2 lignes symétriques du vrai Moodle)."""

    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint("user_id", "contact_id", name="uq_contacts_user_contact"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    contact_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ContactRequest(Base):
    __tablename__ = "contact_requests"
    __table_args__ = (
        UniqueConstraint("user_id", "requested_user_id", name="uq_contact_requests_user_requested"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    requested_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class BlockedUser(Base):
    __tablename__ = "blocked_users"
    __table_args__ = (
        UniqueConstraint("user_id", "blocked_user_id", name="uq_blocked_users_user_blocked"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    blocked_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
