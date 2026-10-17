# app/Models/MMessages.py — messagerie interne (conversations 1-à-1)
"""Un message relie deux comptes users. Une "conversation" n'est pas une
table : c'est l'ensemble des messages échangés entre deux users.

id auto-incrémenté (et non UUID comme ailleurs) : le temps réel WebSocket
repose sur "les messages d'id > dernier id vu" (voir
app/services/message_realtime.py), ce qui exige un ordre monotone."""

from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
from app.database import Base


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_recipient_read", "recipient_id", "read_at"),
        Index("ix_messages_pair", "sender_id", "recipient_id"),
        {
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB',
        },
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sender_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
