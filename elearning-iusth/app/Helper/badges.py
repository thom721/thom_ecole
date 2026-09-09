import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.Models.MBadge import Badge, BadgeCriterion, BadgeCriterionMet, BadgeIssued, BadgeStatus, BadgeCriteriaType, BadgeCriteriaLogic
from app.Models.MCompletion import ActivityCompletion
from app.Models.MEnrollmentMethod import CohortMember


def evaluate_criterion(db: Session, criterion: BadgeCriterion, student_id: str, course_id: str | None) -> bool:
    if criterion.criteria_type == BadgeCriteriaType.activity:
        return (
            db.query(ActivityCompletion)
            .filter(
                ActivityCompletion.student_id == student_id,
                ActivityCompletion.item_type == criterion.required_item_type,
                ActivityCompletion.item_id == criterion.required_item_id,
            )
            .first()
            is not None
        )

    if criterion.criteria_type == BadgeCriteriaType.course:
        if not course_id:
            return False
        from app.Routes.RCompletion import _course_visible_items

        tracked = _course_visible_items(db, course_id)
        if not tracked:
            return False
        completed_keys = {
            (c.item_type, c.item_id)
            for c in db.query(ActivityCompletion).filter(ActivityCompletion.student_id == student_id).all()
        }
        return all((item_type, item.id) in completed_keys for item_type, item in tracked)

    if criterion.criteria_type == BadgeCriteriaType.grade:
        if not course_id:
            return False
        from app.Routes.RGrades import _build_report

        report = _build_report(db, course_id, only_student_id=student_id)
        if not report.rows or report.rows[0].final_percent is None:
            return False
        return report.rows[0].final_percent >= criterion.min_percent

    if criterion.criteria_type == BadgeCriteriaType.cohort:
        return (
            db.query(CohortMember)
            .filter(CohortMember.cohort_id == criterion.cohort_id, CohortMember.user_id == student_id)
            .first()
            is not None
        )

    return False


def evaluate_badge_for_student(db: Session, badge: Badge, student_id: str) -> bool:
    """Renvoie True si le badge vient d'être émis (ou l'était déjà)."""
    already_issued = db.query(BadgeIssued).filter(BadgeIssued.badge_id == badge.id, BadgeIssued.user_id == student_id).first()
    if already_issued is not None:
        return True
    if badge.status != BadgeStatus.active or not badge.criteria:
        return False

    results = []
    for criterion in badge.criteria:
        met = evaluate_criterion(db, criterion, student_id, badge.course_id)
        if met:
            existing = db.query(BadgeCriterionMet).filter(
                BadgeCriterionMet.criterion_id == criterion.id, BadgeCriterionMet.user_id == student_id,
            ).first()
            if existing is None:
                db.add(BadgeCriterionMet(criterion_id=criterion.id, user_id=student_id))
                db.commit()
        results.append(met)

    satisfied = all(results) if badge.criteria_logic == BadgeCriteriaLogic.and_ else any(results)
    if not satisfied:
        return False

    expires_at = None
    if badge.expire_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=badge.expire_days)

    db.add(BadgeIssued(
        badge_id=badge.id, user_id=student_id, expires_at=expires_at,
        unique_hash=secrets.token_hex(32), awarded_manually=False,
    ))
    db.commit()
    return True


def evaluate_badges_for_student(db: Session, student_id: str, course_id: str | None) -> None:
    """Réévalue tous les badges applicables à cet étudiant : ceux du cours
    précis (si fourni) + les badges site."""
    query = db.query(Badge).filter(Badge.status == BadgeStatus.active)
    if course_id:
        from sqlalchemy import or_
        query = query.filter(or_(Badge.course_id == course_id, Badge.course_id.is_(None)))
    else:
        query = query.filter(Badge.course_id.is_(None))
    for badge in query.all():
        evaluate_badge_for_student(db, badge, student_id)


def evaluate_badges_for_cohort_member(db: Session, cohort_id: str, student_id: str) -> None:
    """Point de déclenchement dédié pour le critère `cohort` — appelé
    depuis RCohorts.py::add_cohort_member (voir plan Épic 12)."""
    badges_with_cohort_criterion = (
        db.query(Badge)
        .join(BadgeCriterion, BadgeCriterion.badge_id == Badge.id)
        .filter(Badge.status == BadgeStatus.active, BadgeCriterion.criteria_type == BadgeCriteriaType.cohort,
                BadgeCriterion.cohort_id == cohort_id)
        .all()
    )
    for badge in badges_with_cohort_criterion:
        evaluate_badge_for_student(db, badge, student_id)
