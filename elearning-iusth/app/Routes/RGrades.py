from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, desc
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MGrade import GradeCategory, GradeItem, ManualGrade, GradeItemKind
from app.Models.MQuiz import Quiz, QuizAttempt, QuizAttemptStatus
from app.Models.MLesson import Lesson, LessonAttempt, LessonAttemptStatus
from app.Models.MWorkshop import Workshop, WorkshopSubmission, WorkshopAssessment, WorkshopDimension
from app.Models.MInteractiveVideo import InteractiveVideo, InteractiveVideoCheckpoint, InteractiveVideoAttempt, InteractiveVideoAttemptStatus
from app.Models.MAssignment import Submission
from app.Models.MEnrollment import Enrollment, CourseRole, EnrollmentStatus
from app.Models.MUser import User
from app.Models.MScale import Scale
from app.Schemas.SGrade import (
    GradeReportOut, GradeReportCategoryOut, GradeReportItemOut,
    GradeEntryOut, CategorySubtotalOut, StudentGradeRowOut,
)
from app.dependencies.auth import require_course_role, get_current_active_user, get_enrollment_or_none
from app.Helper.scales import resolve_letter
from app.Helper.workshop_grading import submission_final_grade, reviewer_final_gradinggrade

router = APIRouter(tags=["grades"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _best_quiz_attempts(db: Session, course_id: str) -> dict[tuple[str, str], tuple[Decimal, Decimal]]:
    """Une requête fenêtrée pour tout le cours : meilleure tentative
    (classée par pourcentage, pas par score brut — voir plan Phase 3) par
    (quiz_id, student_id), tentatives entièrement notées uniquement."""
    ranked = (
        db.query(
            QuizAttempt.quiz_id.label("quiz_id"),
            QuizAttempt.student_id.label("student_id"),
            QuizAttempt.score.label("score"),
            QuizAttempt.max_score.label("max_score"),
            func.row_number().over(
                partition_by=(QuizAttempt.quiz_id, QuizAttempt.student_id),
                order_by=(
                    desc(QuizAttempt.score / QuizAttempt.max_score),
                    desc(QuizAttempt.score),
                    desc(QuizAttempt.submitted_at),
                ),
            ).label("rn"),
        )
        .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
        .join(Section, Section.id == Quiz.section_id)
        .filter(Section.course_id == course_id, QuizAttempt.status == QuizAttemptStatus.graded)
        .subquery()
    )
    rows = db.query(ranked).filter(ranked.c.rn == 1).all()
    return {(r.quiz_id, r.student_id): (r.score, r.max_score) for r in rows}


def _best_lesson_attempts(db: Session, course_id: str) -> dict[tuple[str, str], tuple[Decimal, Decimal]]:
    """Copie exacte de `_best_quiz_attempts` pour les leçons (voir plan
    Épic 9) — meilleure tentative par pourcentage, tentatives `completed`
    uniquement (jamais `pending_manual_grading`)."""
    ranked = (
        db.query(
            LessonAttempt.lesson_id.label("lesson_id"),
            LessonAttempt.student_id.label("student_id"),
            LessonAttempt.score.label("score"),
            LessonAttempt.max_score.label("max_score"),
            func.row_number().over(
                partition_by=(LessonAttempt.lesson_id, LessonAttempt.student_id),
                order_by=(
                    desc(LessonAttempt.score / LessonAttempt.max_score),
                    desc(LessonAttempt.score),
                    desc(LessonAttempt.completed_at),
                ),
            ).label("rn"),
        )
        .join(Lesson, Lesson.id == LessonAttempt.lesson_id)
        .join(Section, Section.id == Lesson.section_id)
        .filter(Section.course_id == course_id, LessonAttempt.status == LessonAttemptStatus.completed)
        .subquery()
    )
    rows = db.query(ranked).filter(ranked.c.rn == 1).all()
    return {(r.lesson_id, r.student_id): (r.score, r.max_score) for r in rows}


def _workshops_with_data(db: Session, workshop_ids: list[str]) -> dict[str, Workshop]:
    """Charge les ateliers concernés avec toutes leurs données imbriquées
    en un seul aller-retour (pas de N+1) — nécessaire car
    `workshop_grading.py` calcule tout en direct sur les objets ORM."""
    if not workshop_ids:
        return {}
    workshops = (
        db.query(Workshop)
        .options(
            joinedload(Workshop.dimensions).joinedload(WorkshopDimension.levels),
            joinedload(Workshop.submissions).joinedload(WorkshopSubmission.assessments).joinedload(WorkshopAssessment.grades),
        )
        .filter(Workshop.id.in_(workshop_ids))
        .all()
    )
    return {w.id: w for w in workshops}


def _workshop_submission_grades(workshops: dict[str, Workshop]) -> dict[tuple[str, str], Decimal]:
    """(workshop_id, author_id) -> note finale de soumission (voir plan
    Épic 10) — contrairement à Quiz/Lesson, pas de "meilleure tentative" :
    une seule soumission par étudiant."""
    result = {}
    for workshop in workshops.values():
        for submission in workshop.submissions:
            grade = submission_final_grade(submission)
            if grade is not None:
                result[(workshop.id, submission.author_id)] = grade
    return result


def _workshop_grading_grades(workshops: dict[str, Workshop]) -> dict[tuple[str, str], Decimal]:
    """(workshop_id, reviewer_id) -> note finale de qualité d'évaluation."""
    result = {}
    for workshop in workshops.values():
        reviewer_ids = {a.reviewer_id for s in workshop.submissions for a in s.assessments}
        for reviewer_id in reviewer_ids:
            grade = reviewer_final_gradinggrade(workshop, reviewer_id)
            if grade is not None:
                result[(workshop.id, reviewer_id)] = grade
    return result


def _interactive_videos_with_data(db: Session, video_ids: list[str]) -> dict[str, InteractiveVideo]:
    """Charge les vidéos concernées avec leurs checkpoints (pour
    calculer max_points même sans tentative encore) — pas de N+1."""
    if not video_ids:
        return {}
    videos = (
        db.query(InteractiveVideo)
        .options(joinedload(InteractiveVideo.checkpoints).joinedload(InteractiveVideoCheckpoint.question))
        .filter(InteractiveVideo.id.in_(video_ids))
        .all()
    )
    return {v.id: v for v in videos}


def _interactive_video_max_points(video: InteractiveVideo) -> Decimal:
    return sum((cp.points if cp.points is not None else cp.question.default_points) for cp in video.checkpoints) or Decimal("0")


def _interactive_video_grades(db: Session, video_ids: list[str]) -> dict[tuple[str, str], tuple[Decimal, Decimal]]:
    """(video_id, student_id) -> (score, max_score) — une seule tentative
    par étudiant (voir plan Épic 18), pas de "meilleure tentative" à
    résoudre, contrairement à Quiz/Leçon."""
    if not video_ids:
        return {}
    attempts = (
        db.query(InteractiveVideoAttempt)
        .filter(InteractiveVideoAttempt.video_id.in_(video_ids), InteractiveVideoAttempt.status == InteractiveVideoAttemptStatus.completed)
        .all()
    )
    return {(a.video_id, a.student_id): (a.score, a.max_score) for a in attempts}


def _build_report(db: Session, course_id: str, only_student_id: str | None = None) -> GradeReportOut:
    categories = db.query(GradeCategory).filter(GradeCategory.course_id == course_id).order_by(GradeCategory.sort_order).all()
    items = (
        db.query(GradeItem)
        .options(joinedload(GradeItem.assignment), joinedload(GradeItem.quiz), joinedload(GradeItem.lesson))
        .filter(GradeItem.course_id == course_id)
        .order_by(GradeItem.sort_order)
        .all()
    )

    roster_query = (
        db.query(Enrollment, User)
        .join(User, User.id == Enrollment.user_id)
        .filter(Enrollment.course_id == course_id, Enrollment.role_in_course == CourseRole.student,
                Enrollment.status == EnrollmentStatus.active)
    )
    if only_student_id:
        roster_query = roster_query.filter(Enrollment.user_id == only_student_id)
    roster = roster_query.all()

    assignment_item_ids = [i.assignment_id for i in items if i.kind == GradeItemKind.assignment]
    submissions = (
        db.query(Submission)
        .filter(Submission.assignment_id.in_(assignment_item_ids), Submission.grade.isnot(None))
        .all()
        if assignment_item_ids else []
    )
    submission_grades = {(s.assignment_id, s.student_id): s.grade for s in submissions}

    best_quiz = _best_quiz_attempts(db, course_id)
    best_lesson = _best_lesson_attempts(db, course_id)

    workshop_ids = list({i.workshop_id for i in items if i.workshop_id})
    workshops_by_id = _workshops_with_data(db, workshop_ids)
    workshop_submission_grades = _workshop_submission_grades(workshops_by_id)
    workshop_grading_grades = _workshop_grading_grades(workshops_by_id)

    interactive_video_ids = [i.interactive_video_id for i in items if i.kind == GradeItemKind.interactive_video]
    interactive_videos_by_id = _interactive_videos_with_data(db, interactive_video_ids)
    interactive_video_grades = _interactive_video_grades(db, interactive_video_ids)

    manual_item_ids = [i.id for i in items if i.kind == GradeItemKind.manual]
    manual_grades = (
        db.query(ManualGrade)
        .filter(ManualGrade.grade_item_id.in_(manual_item_ids), ManualGrade.points.isnot(None))
        .all()
        if manual_item_ids else []
    )
    manual_grade_map = {(m.grade_item_id, m.student_id): m.points for m in manual_grades}

    # Échelles référencées par les devoirs/items manuels de ce rapport
    # (voir plan Épic 8) — un seul aller-retour, pas de N+1.
    scale_ids = {i.assignment.scale_id for i in items if i.kind == GradeItemKind.assignment and i.assignment.scale_id}
    scale_ids |= {i.scale_id for i in items if i.kind == GradeItemKind.manual and i.scale_id}
    scales_by_id = {
        s.id: {level.rank: level.label for level in s.levels}
        for s in (db.query(Scale).filter(Scale.id.in_(scale_ids)).all() if scale_ids else [])
    }

    def item_scale_id(item: GradeItem) -> str | None:
        if item.kind == GradeItemKind.assignment:
            return item.assignment.scale_id
        if item.kind == GradeItemKind.manual:
            return item.scale_id
        return None

    def item_title(item: GradeItem) -> str:
        if item.kind == GradeItemKind.assignment:
            return item.assignment.title
        if item.kind == GradeItemKind.quiz:
            return item.quiz.title
        if item.kind == GradeItemKind.lesson:
            return item.lesson.title
        if item.kind in (GradeItemKind.workshop_submission, GradeItemKind.workshop_grading):
            workshop = workshops_by_id.get(item.workshop_id)
            base = workshop.title if workshop else "Atelier"
            suffix = " — soumission" if item.kind == GradeItemKind.workshop_submission else " — qualité d'évaluation"
            return base + suffix
        if item.kind == GradeItemKind.interactive_video:
            video = interactive_videos_by_id.get(item.interactive_video_id)
            return video.title if video else "Vidéo interactive"
        return item.title

    def item_max_points(item: GradeItem) -> Decimal | None:
        scale_id = item_scale_id(item)
        if scale_id and scale_id in scales_by_id:
            return Decimal(len(scales_by_id[scale_id]))
        if item.kind == GradeItemKind.assignment:
            return item.assignment.max_points
        if item.kind == GradeItemKind.manual:
            return item.max_points
        if item.kind == GradeItemKind.workshop_submission:
            workshop = workshops_by_id.get(item.workshop_id)
            return workshop.grade if workshop else None
        if item.kind == GradeItemKind.workshop_grading:
            workshop = workshops_by_id.get(item.workshop_id)
            return workshop.gradinggrade if workshop else None
        if item.kind == GradeItemKind.interactive_video:
            video = interactive_videos_by_id.get(item.interactive_video_id)
            return _interactive_video_max_points(video) if video else None
        return None  # quiz/leçon : pas de valeur canonique, résolu par étudiant ci-dessous

    def _scale_label(item: GradeItem, earned: Decimal | None) -> str | None:
        scale_id = item_scale_id(item)
        if scale_id and earned is not None and scale_id in scales_by_id:
            return scales_by_id[scale_id].get(int(earned))
        return None

    def student_entry(item: GradeItem, student_id: str) -> GradeEntryOut:
        if item.kind == GradeItemKind.assignment:
            earned = submission_grades.get((item.assignment_id, student_id))
            possible = item_max_points(item)
            return GradeEntryOut(earned=earned, possible=possible if earned is not None else None,
                                  is_graded=earned is not None, label=_scale_label(item, earned))
        if item.kind == GradeItemKind.quiz:
            best = best_quiz.get((item.quiz_id, student_id))
            if best is None:
                return GradeEntryOut(earned=None, possible=None, is_graded=False)
            score, max_score = best
            return GradeEntryOut(earned=score, possible=max_score, is_graded=True)
        if item.kind == GradeItemKind.lesson:
            best = best_lesson.get((item.lesson_id, student_id))
            if best is None:
                return GradeEntryOut(earned=None, possible=None, is_graded=False)
            score, max_score = best
            return GradeEntryOut(earned=score, possible=max_score, is_graded=True)
        if item.kind == GradeItemKind.workshop_submission:
            earned = workshop_submission_grades.get((item.workshop_id, student_id))
            possible = item_max_points(item)
            return GradeEntryOut(earned=earned, possible=possible if earned is not None else None, is_graded=earned is not None)
        if item.kind == GradeItemKind.workshop_grading:
            earned = workshop_grading_grades.get((item.workshop_id, student_id))
            possible = item_max_points(item)
            return GradeEntryOut(earned=earned, possible=possible if earned is not None else None, is_graded=earned is not None)
        if item.kind == GradeItemKind.interactive_video:
            best = interactive_video_grades.get((item.interactive_video_id, student_id))
            possible = item_max_points(item)
            if best is None:
                return GradeEntryOut(earned=None, possible=possible, is_graded=False)
            score, _max_score = best
            return GradeEntryOut(earned=score, possible=possible, is_graded=True)
        # manual
        points = manual_grade_map.get((item.id, student_id))
        possible = item_max_points(item)
        return GradeEntryOut(earned=points, possible=possible if points is not None else None,
                              is_graded=points is not None, label=_scale_label(item, points))

    categories_out = [GradeReportCategoryOut(id=c.id, name=c.name, weight_percent=c.weight_percent, sort_order=c.sort_order, evaluation_phase=c.evaluation_phase) for c in categories]
    items_out = [GradeReportItemOut(id=i.id, grade_category_id=i.grade_category_id, kind=i.kind,
                                     assignment_id=i.assignment_id, quiz_id=i.quiz_id, lesson_id=i.lesson_id,
                                     workshop_id=i.workshop_id,
                                     title=item_title(i), max_points=item_max_points(i), scale_id=item_scale_id(i),
                                     sort_order=i.sort_order) for i in items]

    rows: list[StudentGradeRowOut] = []
    for enrollment, student in roster:
        entries: dict[str, GradeEntryOut] = {}
        by_category: dict[str | None, list[GradeEntryOut]] = {}

        for item in items:
            entry = student_entry(item, student.id)
            entries[item.id] = entry
            if entry.is_graded:
                by_category.setdefault(item.grade_category_id, []).append(entry)

        category_subtotals: dict[str, CategorySubtotalOut] = {}
        weighted_sum = Decimal("0")
        weight_used = Decimal("0")
        # Totaux indépendants par phase (voir plan Épic 24) — une catégorie
        # taguée evaluation_phase compte À LA FOIS dans le blend général
        # ci-dessus ET dans son total de phase ; les deux calculs sont
        # indépendants, pas exclusifs.
        #
        # ATTENTION : ce total de phase n'est PAS une moyenne pondérée
        # relative comme final_percent ci-dessus (où le poids d'une seule
        # catégorie s'annule dans earned/weight_used). weight_percent y
        # représente une allocation ABSOLUE du total de la phase côté
        # ecole_nginx (ex: "ce devoir vaut 25% de l'Intra") — donc chaque
        # catégorie contribue weight_percent × (percent_catégorie / 100),
        # additionné SANS division par la somme des poids. Avec un seul
        # devoir à 25% noté 7/10 (70%), la contribution est 25 × 0.70 =
        # 17.5 (17.5% de l'Intra), pas juste 70% — voir plan Épic 24.
        phase_weighted_sum = {"intra": Decimal("0"), "finale": Decimal("0")}
        phase_has_data = {"intra": False, "finale": False}

        for category in categories:
            graded_entries = by_category.get(category.id, [])
            if not graded_entries:
                continue
            earned = sum((e.earned for e in graded_entries), Decimal("0"))
            possible = sum((e.possible for e in graded_entries), Decimal("0"))
            percent = (earned / possible * 100) if possible else Decimal("0")
            category_subtotals[category.id] = CategorySubtotalOut(earned=earned, possible=possible, percent=percent)
            weighted_sum += percent * category.weight_percent
            weight_used += category.weight_percent
            if category.evaluation_phase in phase_weighted_sum:
                phase_weighted_sum[category.evaluation_phase] += category.weight_percent * percent / 100
                phase_has_data[category.evaluation_phase] = True

        uncategorized_entries = by_category.get(None, [])
        uncategorized_subtotal = None
        if uncategorized_entries:
            earned = sum((e.earned for e in uncategorized_entries), Decimal("0"))
            possible = sum((e.possible for e in uncategorized_entries), Decimal("0"))
            percent = (earned / possible * 100) if possible else Decimal("0")
            uncategorized_subtotal = CategorySubtotalOut(earned=earned, possible=possible, percent=percent)
            uncategorized_weight = max(Decimal("0"), Decimal("100") - sum((c.weight_percent for c in categories if c.id in category_subtotals), Decimal("0")))
            weighted_sum += percent * uncategorized_weight
            weight_used += uncategorized_weight

        final_percent = (weighted_sum / weight_used) if weight_used else None
        intra_percent = phase_weighted_sum["intra"] if phase_has_data["intra"] else None
        finale_percent = phase_weighted_sum["finale"] if phase_has_data["finale"] else None

        rows.append(StudentGradeRowOut(
            student_id=student.id, student_name=f"{student.first_name} {student.last_name}",
            entries=entries, category_subtotals=category_subtotals,
            uncategorized_subtotal=uncategorized_subtotal, final_percent=final_percent,
            final_letter=resolve_letter(db, course_id, final_percent),
            intra_percent=intra_percent, finale_percent=finale_percent,
        ))

    return GradeReportOut(course_id=course_id, categories=categories_out, items=items_out, rows=rows)


@router.get("/courses/{course_id}/grades/report", response_model=GradeReportOut,
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def get_report(course_id: str, db: Session = Depends(get_db)):
    return _build_report(db, course_id)


@router.get("/courses/{course_id}/grades/mine", response_model=GradeReportOut)
def get_my_grades(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return _build_report(db, course_id, only_student_id=current_user.id)
