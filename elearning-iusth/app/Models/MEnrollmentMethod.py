from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid
from app.Models.MEnrollment import CourseRole

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class CourseEnrollmentSettings(Base):
    __tablename__ = "course_enrollment_settings"
    __table_args__ = (
        UniqueConstraint("course_id", name="uq_course_enrollment_settings_course"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    self_enrollment_enabled = Column(Boolean, nullable=False, default=False)
    self_enrollment_key = Column(String(100), nullable=True)  # null = pas de code requis
    guest_access_enabled = Column(Boolean, nullable=False, default=False)
    guest_access_key = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Cohort(Base):
    """Transversal à toute la plateforme (pas rattaché à un cours) — calque
    mdl_cohort, géré par un admin uniquement."""

    __tablename__ = "cohorts"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    members = relationship("CohortMember", back_populates="cohort", cascade="all, delete-orphan")
    syncs = relationship("CohortSync", back_populates="cohort", cascade="all, delete-orphan")


class CohortMember(Base):
    __tablename__ = "cohort_members"
    __table_args__ = (
        UniqueConstraint("cohort_id", "user_id", name="uq_cohort_members_cohort_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cohort_id = Column(String(36), ForeignKey("cohorts.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    cohort = relationship("Cohort", back_populates="members")


class CohortSync(Base):
    """Un cours synchronisé avec une cohorte — voir Helper/cohort_sync.py
    pour le mécanisme d'inscription/suspension automatique."""

    __tablename__ = "cohort_syncs"
    __table_args__ = (
        UniqueConstraint("course_id", "cohort_id", name="uq_cohort_syncs_course_cohort"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    cohort_id = Column(String(36), ForeignKey("cohorts.id"), nullable=False)
    role = Column(SAEnum(CourseRole), nullable=False, default=CourseRole.student)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cohort = relationship("Cohort", back_populates="syncs")
