import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid


class CourseRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    manager = "manager"


class EnrollmentStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"


class Enrollment(Base):
    """Remplace le RBAC polymorphique Laravel de ecole_nginx : un rôle par
    cours, une seule jointure pour vérifier une autorisation (voir
    app/dependencies/auth.py:require_course_role)."""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("course_id", "user_id", name="uq_enrollments_course_user"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"},
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_in_course = Column(SAEnum(CourseRole), nullable=False, default=CourseRole.student)
    status = Column(SAEnum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.active)
    enrolled_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    enrolled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # "manual"/"self"/"guest"/"cohort" — nul pour les inscriptions créées
    # avant l'Épic 6 (traité comme "manual" par convention dans le code,
    # jamais dans une contrainte). Permet à la synchronisation de cohorte
    # de ne suspendre QUE les inscriptions qu'elle a elle-même créées,
    # jamais une inscription manuelle du même utilisateur sur le même cours.
    method = Column(String(50), nullable=True)

    course = relationship("Course", back_populates="enrollments")
    user = relationship("User", foreign_keys=[user_id])
