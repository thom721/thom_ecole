from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class Glossary(Base):
    """Calque mdl_glossary — s'attache à une Section comme Forum/Choice.
    `is_main` est un flag au niveau du COURS (un seul glossaire principal
    par cours, pas par section) — appliqué en route, pas en contrainte DB
    (voir RGlossaries.py, même limite assumée que Moodle lui-même)."""

    __tablename__ = "glossaries"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    is_main = Column(Boolean, nullable=False, default=False)
    allow_student_entries = Column(Boolean, nullable=False, default=False)
    # N'a d'effet que si allow_student_entries est vrai.
    require_approval = Column(Boolean, nullable=False, default=False)
    allow_duplicates = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="glossaries")
    entries = relationship("GlossaryEntry", back_populates="glossary", cascade="all, delete-orphan")


class GlossaryEntry(Base):
    __tablename__ = "glossary_entries"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    glossary_id = Column(String(36), ForeignKey("glossaries.id"), nullable=False)
    concept = Column(String(255), nullable=False)
    definition = Column(Text, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_approved = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    glossary = relationship("Glossary", back_populates="entries")
