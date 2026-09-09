from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MGrade import GradeItem, ManualGrade, GradeItemKind
from app.Models.MWorkshop import Workshop
from app.Models.MScale import Scale
from app.Models.MEnrollment import CourseRole, Enrollment, EnrollmentStatus
from app.Models.MUser import User
from app.Models.MNotification import NotificationKind
from app.Schemas.SGrade import GradeItemCreate, GradeItemUpdate, GradeItemOut, ManualGradeSet, ManualGradeOut
from app.dependencies.auth import require_course_role, assert_course_role, get_current_active_user
from app.Helper.notifications import notify

router = APIRouter(tags=["grade-items"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _to_out(item: GradeItem, db: Session) -> GradeItemOut:
    if item.kind == GradeItemKind.assignment:
        title, max_points = item.assignment.title, item.assignment.max_points
    elif item.kind == GradeItemKind.quiz:
        title, max_points = item.quiz.title, None  # pas de valeur canonique (voir plan Phase 3)
    elif item.kind == GradeItemKind.lesson:
        title, max_points = item.lesson.title, None  # pas de valeur canonique (voir plan Épic 9)
    elif item.kind in (GradeItemKind.workshop_submission, GradeItemKind.workshop_grading):
        workshop = db.query(Workshop).filter(Workshop.id == item.workshop_id).first()
        base = workshop.title if workshop else "Atelier"
        if item.kind == GradeItemKind.workshop_submission:
            title, max_points = base + " — soumission", workshop.grade if workshop else None
        else:
            title, max_points = base + " — qualité d'évaluation", workshop.gradinggrade if workshop else None
    else:
        title, max_points = item.title, item.max_points

    return GradeItemOut(
        id=item.id, course_id=item.course_id, grade_category_id=item.grade_category_id,
        kind=item.kind, assignment_id=item.assignment_id, quiz_id=item.quiz_id, lesson_id=item.lesson_id,
        workshop_id=item.workshop_id,
        title=title, max_points=max_points, scale_id=item.scale_id,
        is_visible=item.is_visible, sort_order=item.sort_order,
    )


@router.get("/courses/{course_id}/grade-items", response_model=list[GradeItemOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def list_items(course_id: str, db: Session = Depends(get_db)):
    items = db.query(GradeItem).filter(GradeItem.course_id == course_id).order_by(GradeItem.sort_order).all()
    return [_to_out(i, db) for i in items]


@router.post("/courses/{course_id}/grade-items", response_model=GradeItemOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def create_manual_item(course_id: str, data: GradeItemCreate, db: Session = Depends(get_db)):
    item = GradeItem(course_id=course_id, kind=GradeItemKind.manual, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_out(item, db)


def _get_item_or_404(db: Session, item_id: str) -> GradeItem:
    item = db.query(GradeItem).filter(GradeItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de note introuvable")
    return item


@router.patch("/grade-items/{item_id}", response_model=GradeItemOut)
def update_item(
    item_id: str, data: GradeItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    item = _get_item_or_404(db, item_id)
    assert_course_role(db, current_user, item.course_id, _TEACHING_ROLES)

    payload = data.model_dump(exclude_unset=True)
    if item.kind != GradeItemKind.manual:
        payload.pop("title", None)
        payload.pop("max_points", None)

    for field, value in payload.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return _to_out(item, db)


@router.delete("/grade-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    item = _get_item_or_404(db, item_id)
    assert_course_role(db, current_user, item.course_id, _TEACHING_ROLES)

    if item.kind != GradeItemKind.manual:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Un item lié à un devoir/quiz se supprime en supprimant le devoir/quiz lui-même")

    if db.query(ManualGrade).filter(ManualGrade.grade_item_id == item_id, ManualGrade.points.isnot(None)).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Des notes ont déjà été saisies pour cet item — suppression bloquée")

    db.delete(item)
    db.commit()


@router.get("/grade-items/{item_id}/grades", response_model=list[ManualGradeOut])
def list_manual_grades(
    item_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    item = _get_item_or_404(db, item_id)
    assert_course_role(db, current_user, item.course_id, _TEACHING_ROLES)
    if item.kind != GradeItemKind.manual:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet item n'est pas manuel")
    return db.query(ManualGrade).filter(ManualGrade.grade_item_id == item_id).all()


@router.patch("/grade-items/{item_id}/grades/{student_id}", response_model=ManualGradeOut)
def set_manual_grade(
    item_id: str, student_id: str, data: ManualGradeSet,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upsert : crée la ligne ManualGrade si elle n'existe pas encore
    (aucune action étudiante ne la pré-crée, contrairement à Submission)."""
    item = _get_item_or_404(db, item_id)
    assert_course_role(db, current_user, item.course_id, _TEACHING_ROLES)
    if item.kind != GradeItemKind.manual:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet item n'est pas manuel")

    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == item.course_id, Enrollment.user_id == student_id,
                Enrollment.role_in_course == CourseRole.student, Enrollment.status == EnrollmentStatus.active)
        .first()
    )
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet étudiant n'est pas inscrit à ce cours")

    if item.scale_id:
        scale = db.query(Scale).filter(Scale.id == item.scale_id).first()
        valid_ranks = {level.rank for level in scale.levels}
        if int(data.points) != data.points or int(data.points) not in valid_ranks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail=f"Cet item est noté par échelle — rang attendu parmi {sorted(valid_ranks)}")

    grade = (
        db.query(ManualGrade)
        .filter(ManualGrade.grade_item_id == item_id, ManualGrade.student_id == student_id)
        .first()
    )
    if grade is None:
        grade = ManualGrade(grade_item_id=item_id, student_id=student_id)
        db.add(grade)

    grade.points = data.points
    grade.feedback = data.feedback
    grade.graded_by = current_user.id
    grade.graded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(grade)

    title = item.title or "Note manuelle"
    notify(db, student_id, NotificationKind.new_grade,
           title=f"Note enregistrée : {title}", body=f"Note : {grade.points}",
           link_url=f"/student/courses/{item.course_id}/grades")

    return grade
