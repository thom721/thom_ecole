import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class WikiMode(str, enum.Enum):
    collaborative = "collaborative"
    individual = "individual"


class Wiki(Base):
    __tablename__ = "wikis"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    mode = Column(SAEnum(WikiMode), nullable=False, default=WikiMode.collaborative)
    first_page_title = Column(String(255), nullable=False, default="Accueil")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="wikis")
    subwikis = relationship("Subwiki", back_populates="wiki", cascade="all, delete-orphan")


class Subwiki(Base):
    """Instance concrète du wiki où vivent les pages. `owner_id` NULL =
    la sous-wiki partagée d'un wiki collaboratif ; sinon la sous-wiki d'un
    étudiant précis en mode individuel. Unicité garantie en route
    (get-or-create), pas par contrainte DB — voir plan (MySQL autorise
    plusieurs NULL sur une colonne, une UniqueConstraint ne suffirait pas
    à empêcher plusieurs sous-wikis "partagées")."""

    __tablename__ = "subwikis"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    wiki_id = Column(String(36), ForeignKey("wikis.id"), nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    wiki = relationship("Wiki", back_populates="subwikis")
    pages = relationship("WikiPage", back_populates="subwiki", cascade="all, delete-orphan")


class WikiPage(Base):
    __tablename__ = "wiki_pages"
    __table_args__ = (
        UniqueConstraint("subwiki_id", "title", name="uq_wiki_pages_subwiki_title"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    subwiki_id = Column(String(36), ForeignKey("subwikis.id"), nullable=False)
    title = Column(String(255), nullable=False)
    # Miroir du contenu de la dernière WikiVersion — évite un join à
    # chaque lecture (même rôle que mdl_wiki_pages.cachedcontent).
    cached_content = Column(Text, nullable=False, default="")
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_readonly = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    subwiki = relationship("Subwiki", back_populates="pages")
    versions = relationship("WikiVersion", back_populates="page", cascade="all, delete-orphan", order_by="WikiVersion.version")


class WikiVersion(Base):
    """Copie complète du contenu à chaque édition (comme le vrai Moodle) —
    le diff est calculé à la lecture (voir RWikis.py), jamais stocké."""

    __tablename__ = "wiki_versions"
    __table_args__ = (
        UniqueConstraint("page_id", "version", name="uq_wiki_versions_page_version"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    page_id = Column(String(36), ForeignKey("wiki_pages.id"), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    page = relationship("WikiPage", back_populates="versions")
