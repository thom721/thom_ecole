from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MEnrollment import CourseRole, EnrollmentStatus


class EnrollmentCreate(BaseModel):
    user_id: str
    role_in_course: CourseRole = CourseRole.student


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    course_id: str
    user_id: str
    role_in_course: CourseRole
    status: EnrollmentStatus
    enrolled_by: str | None = None
    enrolled_at: datetime
    method: str | None = None
    # Résolus depuis User dans list_enrollments (REnrollments.py) — pas des
    # colonnes d'Enrollment, juste pour l'affichage (nom au lieu de
    # user_id brut sur la page de détail du cours).
    user_name: str | None = None
    user_email: str | None = None
