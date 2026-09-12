from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Course
from app.Models.MEnrollment import Enrollment, CourseRole, EnrollmentStatus
from app.Models.MUser import User
from app.Schemas.SWebhook import EnrollmentChangedIn, ProgrammeChangedIn, ProgrammeDeletedIn, WebhookAckOut, DevoirGradeOut
from app.dependencies.webhook_auth import require_webhook_key
from app.Routes.RIntegration import resolve_courses_for_classe, _upsert_course_from_programme
from app.Routes.RGrades import _build_report

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
    """Synchronisation temps réel d'un Programme créé ou modifié côté
    ecole_nginx (voir plan Épic 20) — upserte le Course correspondant avec
    le même helper que l'import complet (_upsert_course_from_programme,
    RIntegration.py), pour ne jamais diverger entre les deux chemins.
    `skipped` ne compte ici que les lignes sans email professeur connu ET
    sans compte elearning-iusth existant (le Course est upserté dans tous
    les cas, seul le rattachement enseignant peut être sauté)."""
    processed = 0
    skipped = 0
    category_cache: dict[str, str] = {}
    teacher_cache: dict[str, "User | None"] = {}
    unmatched_courses_by_label: dict[str, list[str]] = {}

    for programme in data.changes:
        _course, _is_new, _account_created_label = _upsert_course_from_programme(
            db, programme, category_cache, teacher_cache, unmatched_courses_by_label
        )
        processed += 1

    skipped = sum(len(courses) for courses in unmatched_courses_by_label.values())

    db.commit()
    return WebhookAckOut(processed=processed, skipped=skipped)


@router.post("/programme-deleted", response_model=WebhookAckOut)
def programme_deleted(data: ProgrammeDeletedIn, db: Session = Depends(get_db)):
    """Un Programme supprimé côté ecole_nginx n'est jamais rattrapé par un
    import (l'import n'upserte que ce qu'il reçoit, il ne supprime rien de
    ce qui manque en face) — sans cet évènement dédié, le cours resterait
    visible indéfiniment côté elearning-iusth. On masque (is_visible=False)
    plutôt que de supprimer le Course : ça préserve tout contenu déjà
    construit dessus (sections, devoirs...) au cas où le programme
    réapparaîtrait plus tard (voir _upsert_course_from_programme, qui
    remet is_visible=True sur un cours retrouvé)."""
    course = (
        db.query(Course)
        .filter(Course.external_source == "ecole_nginx", Course.external_ref_id == data.programme_id)
        .first()
    )
    if course is None:
        return WebhookAckOut(processed=0, skipped=1)

    course.is_visible = False
    db.commit()
    return WebhookAckOut(processed=1, skipped=0)


@router.get("/devoirs-grades", response_model=list[DevoirGradeOut])
def devoirs_grades(programme_id: str, db: Session = Depends(get_db)):
    """Export tiré par ecole_nginx (jamais poussé) pour afficher, sur ses
    propres écrans de saisie de notes, la contribution des devoirs gérés
    ici — voir plan Épic 24. Réutilise _build_report (RGrades.py) tel
    quel : c'est le même calcul pondéré par GradeCategory que la page
    Gradebook du professeur, pas une nouvelle logique d'agrégation.
    Aucun Course synchronisé pour ce Programme => liste vide, jamais une
    erreur (ecole_nginx doit pouvoir afficher une note sans intégration
    elearning-iusth active)."""
    course = (
        db.query(Course)
        .filter(Course.external_source == "ecole_nginx", Course.external_ref_id == programme_id)
        .first()
    )
    if course is None:
        return []

    report = _build_report(db, course.id)
    student_ids = [row.student_id for row in report.rows]
    emails = {
        u.id: u.email
        for u in db.query(User).filter(User.id.in_(student_ids)).all()
    } if student_ids else {}

    return [
        DevoirGradeOut(
            email=emails[row.student_id],
            note_devoirs=float(row.final_percent) if row.final_percent is not None else None,
            note_devoirs_intra=float(row.intra_percent) if row.intra_percent is not None else None,
            note_devoirs_finale=float(row.finale_percent) if row.finale_percent is not None else None,
        )
        for row in report.rows
        if row.student_id in emails
    ]
