from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum
import enum

from app.database import Base, generate_uuid


class SystemRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"
    # Personnel non-enseignant synchronisé depuis ecole_nginx (Épic 23) —
    # jamais un alias de teacher/admin : connexion + réunions du personnel
    # (Épic 21) + messagerie (Épic 11) uniquement, aucune permission
    # granulaire (voir Helper/permissions.py::user_has_permission, qui
    # reste conditionné à system_role==admin, pas étendu à staff).
    staff = "staff"


class MessagePrivacy(str, enum.Enum):
    """Qui peut DÉMARRER une conversation individuelle avec cet
    utilisateur — n'affecte jamais une conversation déjà existante (voir
    plan Épic 11)."""
    course_member = "course_member"
    only_contacts = "only_contacts"
    site = "site"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    system_role = Column(SAEnum(SystemRole), nullable=False, default=SystemRole.student)
    is_active = Column(Boolean, nullable=False, default=True)
    avatar_path = Column(String(500), nullable=True)
    # Vrai pour un compte auto-provisionné (import ecole_nginx, mot de
    # passe aléatoire) tant que l'utilisateur n'a pas défini le sien.
    must_change_password = Column(Boolean, nullable=False, default=False)
    message_privacy = Column(SAEnum(MessagePrivacy), nullable=False, default=MessagePrivacy.course_member)
    # Proxy pour le bloc "utilisateurs en ligne" (Épic 15) — ce projet n'a
    # pas de suivi générique par page comme le vrai Moodle, la dernière
    # connexion sert d'approximation réelle, documentée.
    last_login_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
