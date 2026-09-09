from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey

from app.database import Base, generate_uuid


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(100), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    # Non NULL seulement une fois consommé — un token n'est utilisable
    # qu'une seule fois, jamais réinitialisé.
    used_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
