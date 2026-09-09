from sqlalchemy.orm import Session

from app.Models.MAccessLog import AccessLog, AccessItemType
from app.Models.MUser import User, SystemRole
from app.Models.MEnrollment import Enrollment, CourseRole


def log_access(db: Session, user: User, course_id: str, item_type: AccessItemType, item_id: str | None = None) -> None:
    """Uniquement quand l'utilisateur est étudiant (voir plan Phase 5) —
    sinon les enseignants dominent leurs propres statistiques."""
    if user.system_role != SystemRole.student:
        return
    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id, Enrollment.user_id == user.id, Enrollment.role_in_course == CourseRole.student)
        .first()
    )
    if enrollment is None:
        return
    db.add(AccessLog(user_id=user.id, course_id=course_id, item_type=item_type, item_id=item_id))
    db.commit()
