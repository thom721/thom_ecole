from sqlalchemy.orm import Session

from app.Models.MEnrollment import Enrollment, EnrollmentStatus
from app.Models.MEnrollmentMethod import CohortSync


def sync_member_added(db: Session, cohort_id: str, user_id: str) -> None:
    """Un utilisateur rejoint une cohorte — l'inscrit (ou réactive son
    inscription suspendue) dans tous les cours synchronisés avec cette
    cohorte. N'écrase jamais une inscription existante d'une autre méthode
    (contrainte unique course_id/user_id — voir Enrollment)."""
    syncs = db.query(CohortSync).filter(CohortSync.cohort_id == cohort_id).all()
    for sync in syncs:
        existing = (
            db.query(Enrollment)
            .filter(Enrollment.course_id == sync.course_id, Enrollment.user_id == user_id)
            .first()
        )
        if existing is None:
            db.add(Enrollment(
                course_id=sync.course_id, user_id=user_id, role_in_course=sync.role,
                status=EnrollmentStatus.active, method="cohort",
            ))
        elif existing.method == "cohort" and existing.status == EnrollmentStatus.suspended:
            existing.status = EnrollmentStatus.active
    db.commit()


def sync_member_removed(db: Session, cohort_id: str, user_id: str) -> None:
    """Un utilisateur quitte une cohorte — SUSPEND (ne supprime jamais,
    préserve l'historique de notes) son inscription dans les cours
    synchronisés, seulement si elle provient bien de cette cohorte
    (method="cohort") — une inscription manuelle du même utilisateur au
    même cours n'est jamais touchée."""
    syncs = db.query(CohortSync).filter(CohortSync.cohort_id == cohort_id).all()
    for sync in syncs:
        enrollment = (
            db.query(Enrollment)
            .filter(Enrollment.course_id == sync.course_id, Enrollment.user_id == user_id, Enrollment.method == "cohort")
            .first()
        )
        if enrollment is not None:
            enrollment.status = EnrollmentStatus.suspended
    db.commit()


def sync_created(db: Session, cohort_id: str, course_id: str, role) -> None:
    """Un CohortSync vient d'être créé — inscrit immédiatement tous les
    membres actuels de la cohorte."""
    from app.Models.MEnrollmentMethod import CohortMember

    members = db.query(CohortMember).filter(CohortMember.cohort_id == cohort_id).all()
    for member in members:
        existing = (
            db.query(Enrollment)
            .filter(Enrollment.course_id == course_id, Enrollment.user_id == member.user_id)
            .first()
        )
        if existing is None:
            db.add(Enrollment(
                course_id=course_id, user_id=member.user_id, role_in_course=role,
                status=EnrollmentStatus.active, method="cohort",
            ))
        elif existing.method == "cohort" and existing.status == EnrollmentStatus.suspended:
            existing.status = EnrollmentStatus.active
    db.commit()


def sync_removed(db: Session, cohort_id: str, course_id: str) -> None:
    """Un CohortSync vient d'être supprimé — suspend les inscriptions
    method="cohort" de ce cours (préserve l'historique)."""
    enrollments = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id, Enrollment.method == "cohort")
        .all()
    )
    from app.Models.MEnrollmentMethod import CohortMember

    member_user_ids = {
        m.user_id for m in db.query(CohortMember).filter(CohortMember.cohort_id == cohort_id).all()
    }
    for enrollment in enrollments:
        if enrollment.user_id in member_user_ids:
            enrollment.status = EnrollmentStatus.suspended
    db.commit()
