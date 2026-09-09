from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Course
from app.Models.MEnrollment import Enrollment, CourseRole, EnrollmentStatus
from app.Models.MUser import User
from app.Schemas.SWebhook import EnrollmentChangedIn, ProgrammeChangedIn, WebhookAckOut
from app.dependencies.webhook_auth import require_webhook_key
from app.Routes.RIntegration import resolve_courses_for_classe

router = APIRouter(prefix="/webhooks/ecole-nginx", tags=["webhooks"],
                    dependencies=[Depends(require_webhook_key)])


@router.post("/enrollment-changed", response_model=WebhookAckOut)
def enrollment_changed(data: EnrollmentChangedIn, db: Session = Depends(get_db)):
    """Synchronisation temps réel depuis ecole_nginx (voir plan Épic 20)
    — ne fait quoi que ce soit que si l'étudiant a déjà un email de
    connexion résolu côté ecole_nginx ET qu'un compte elearning-iusth
    existe déjà avec cet email exact (décision de périmètre 6 : ce
    webhook maintient à jour un lien déjà établi, ne crée jamais de
    nouveau compte tout seul — l'activation reste un acte humain, Épic 19).
    Un retrait de classe SUSPEND l'inscription, ne la supprime jamais
    (même principe que la synchronisation de cohorte, Épic 6)."""
    processed = 0
    skipped = 0
    courses_cache: dict[str, tuple[list[Course], list[str]]] = {}

    for change in data.changes:
        if not change.etudiant_login_email:
            skipped += 1
            continue
        user = db.query(User).filter(User.email == change.etudiant_login_email).first()
        if user is None:
            skipped += 1
            continue

        if change.classes_id not in courses_cache:
            courses_cache[change.classes_id] = resolve_courses_for_classe(db, change.classes_id, data.annee_academique_id)
        courses, _warnings = courses_cache[change.classes_id]

        for course in courses:
            enrollment = (
                db.query(Enrollment)
                .filter(Enrollment.course_id == course.id, Enrollment.user_id == user.id)
                .first()
            )
            if change.status:
                if enrollment is None:
                    db.add(Enrollment(course_id=course.id, user_id=user.id,
                                       role_in_course=CourseRole.student, status=EnrollmentStatus.active))
                elif enrollment.status == EnrollmentStatus.suspended:
                    enrollment.status = EnrollmentStatus.active
            else:
                if enrollment is not None and enrollment.role_in_course == CourseRole.student:
                    enrollment.status = EnrollmentStatus.suspended
        processed += 1

    db.commit()
    return WebhookAckOut(processed=processed, skipped=skipped)


@router.post("/programme-changed", response_model=WebhookAckOut)
def programme_changed(data: ProgrammeChangedIn, db: Session = Depends(get_db)):
    """Synchronisation temps réel d'un changement de professeur sur un
    Programme (voir plan Épic 20). N'ajoute JAMAIS le retrait d'un ancien
    professeur (décision de périmètre 4 — ecole_nginx ne transmet que le
    nouveau professeur_id, retirer l'ancien sur une supposition serait
    risqué)."""
    processed = 0
    skipped = 0

    for change in data.changes:
        if not change.professeur_login_email:
            skipped += 1
            continue
        user = db.query(User).filter(User.email == change.professeur_login_email).first()
        if user is None:
            skipped += 1
            continue
        course = (
            db.query(Course)
            .filter(Course.external_source == "ecole_nginx", Course.external_ref_id == change.programme_id)
            .first()
        )
        if course is None:
            skipped += 1
            continue

        enrollment = (
            db.query(Enrollment)
            .filter(Enrollment.course_id == course.id, Enrollment.user_id == user.id)
            .first()
        )
        if enrollment is None:
            db.add(Enrollment(course_id=course.id, user_id=user.id,
                               role_in_course=CourseRole.teacher, status=EnrollmentStatus.active))
        elif enrollment.status == EnrollmentStatus.suspended:
            enrollment.status = EnrollmentStatus.active
        processed += 1

    db.commit()
    return WebhookAckOut(processed=processed, skipped=skipped)
