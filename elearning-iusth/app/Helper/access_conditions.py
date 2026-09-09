from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.Models.MAccessCondition import AccessCondition, AccessConditionType, AccessLogic
from app.Models.MCompletion import ActivityCompletion, CompletionItemType
from app.Models.MEnrollment import CourseRole
from app.Models.MGrade import GradeItem
from app.Models.MUser import User, SystemRole
from app.dependencies.auth import get_enrollment_or_none
from app.Helper.groups import get_user_group_ids

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _is_teaching(db: Session, current_user: User, course_id: str) -> bool:
    if current_user.system_role == SystemRole.admin:
        return True
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    return enrollment is not None and enrollment.role_in_course in _TEACHING_ROLES


def _evaluate_one(db: Session, current_user: User, course_id: str, condition: AccessCondition) -> tuple[bool, str]:
    if condition.condition_type == AccessConditionType.date:
        now = datetime.now(timezone.utc)
        if condition.available_from and now < condition.available_from.replace(tzinfo=timezone.utc):
            return False, f"Disponible à partir du {condition.available_from.strftime('%d/%m/%Y %H:%M')}"
        if condition.available_until and now > condition.available_until.replace(tzinfo=timezone.utc):
            return False, f"Disponible jusqu'au {condition.available_until.strftime('%d/%m/%Y %H:%M')}"
        return True, ""

    if condition.condition_type == AccessConditionType.grade:
        # Réutilise directement le calcul de note déjà existant (Phase 3)
        # plutôt que de le réimplémenter — voir plan Épic 7.
        from app.Routes.RGrades import _build_report

        report = _build_report(db, course_id, only_student_id=current_user.id)
        if not report.rows:
            return False, "Note requise non disponible"
        entry = report.rows[0].entries.get(condition.grade_item_id)
        if entry is None or not entry.is_graded or not entry.possible:
            return False, f"Nécessite une note ≥ {condition.min_percent}% sur un item non encore noté"
        percent = (entry.earned / entry.possible) * 100
        if percent < condition.min_percent:
            return False, f"Nécessite une note ≥ {condition.min_percent}% (actuelle : {percent:.1f}%)"
        return True, ""

    if condition.condition_type == AccessConditionType.activity_completion:
        done = (
            db.query(ActivityCompletion)
            .filter(
                ActivityCompletion.student_id == current_user.id,
                ActivityCompletion.item_type == condition.required_item_type,
                ActivityCompletion.item_id == condition.required_item_id,
            )
            .first()
            is not None
        )
        return done, "Nécessite d'avoir terminé une autre activité au préalable" if not done else ""

    if condition.condition_type == AccessConditionType.group:
        member = condition.group_id in get_user_group_ids(db, course_id, current_user.id)
        return member, "Réservé à un groupe précis" if not member else ""

    return True, ""


def is_item_accessible(db: Session, current_user: User, course_id: str, item_type: CompletionItemType, item_id: str) -> tuple[bool, list[str]]:
    if _is_teaching(db, current_user, course_id):
        return True, []

    conditions = (
        db.query(AccessCondition)
        .filter(AccessCondition.item_type == item_type, AccessCondition.item_id == item_id)
        .all()
    )
    if not conditions:
        return True, []

    results = [_evaluate_one(db, current_user, course_id, c) for c in conditions]
    logic = conditions[0].logic
    passed = all(ok for ok, _ in results) if logic == AccessLogic.and_ else any(ok for ok, _ in results)
    reasons = [] if passed else [reason for ok, reason in results if not ok and reason]
    return passed, reasons
