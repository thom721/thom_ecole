from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Text, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class Scale(Base):
    """`course_id` NULL = échelle "site", réutilisable par n'importe quel
    cours (réservée admin) ; sinon propre à un cours (créable par
    l'enseignant du cours)."""

    __tablename__ = "scales"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    levels = relationship("ScaleLevel", back_populates="scale", cascade="all, delete-orphan", order_by="ScaleLevel.rank")


class ScaleLevel(Base):
    __tablename__ = "scale_levels"
    __table_args__ = (
        UniqueConstraint("scale_id", "rank", name="uq_scale_levels_scale_rank"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scale_id = Column(String(36), ForeignKey("scales.id"), nullable=False)
    label = Column(String(255), nullable=False)
    # 1 = pire niveau, croissant — sert aussi de valeur numérique stockée
    # directement dans Submission.grade / ManualGrade.points (voir plan).
    rank = Column(Integer, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    scale = relationship("Scale", back_populates="levels")


class GradeLetter(Base):
    """Absence totale de ligne pour un cours = barème par défaut appliqué
    en code (voir Helper/scales.py), jamais semé en base."""

    __tablename__ = "grade_letters"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    # Pas limité à une seule lettre (A/B/C...) malgré le nom — un
    # établissement peut préférer des libellés ("Satisfaisant"...).
    letter = Column(String(50), nullable=False)
    lower_boundary = Column(Numeric(5, 2), nullable=False)
