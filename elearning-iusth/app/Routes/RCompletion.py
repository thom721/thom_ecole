from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Course, Section
from app.Models.MResource import Resource
from app.Models.MAssignment import Assignment
from app.Models.MQuiz import Quiz
from app.Models.MCompletion import ActivityCompletion, ActivityCompletionConfig, CompletionItemType, CompletionMode
from app.Models.MEnrollment import Enrollment, CourseRole, EnrollmentStatus
from app.Models.MUser import User
from app.Schemas.SCompletion import CompletionMineOut, CompletionItemOut, CompletionReportRowOut, CompletionConfigOut, CompletionConfigUpdate
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role, require_course_role
from app.Helper.completion import mark_complete_if_absent
from app.Helper.completion_config import get_completion_mode
from app.Routes.RAccessConditions import _resolve_course_id

router = APIRouter(tags=["completion"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]

# item_type -> (modèle, attribut titre) — pour lister les items d'un type
# récemment devenu suivable (Forum/Choice, voir plan Épic 7) de la même
# façon que Resource/Assignment/Quiz déjà en place depuis la Phase 5.
_TITLE_ATTR = {
    CompletionItemType.resource: "title",
    CompletionItemType.assignment: "title",
    CompletionItemType.quiz: "title",
    CompletionItemType.forum: "title",
    CompletionItemType.choice: "title",
    CompletionItemType.lesson: "title",
    CompletionItemType.workshop: "title",
    CompletionItemType.live_session: "title",
    CompletionItemType.interactive_video: "title",
}


@router.post("/resources/{resource_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
def mark_resource_complete(
    resource_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ressource introuvable")
    section = db.query(Section).filter(Section.id == resource.section_id).first()
    if get_enrollment_or_none(db, section.course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    mark_complete_if_absent(db, current_user.id, CompletionItemType.resource, resource_id)


@router.delete("/resources/{resource_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
def unmark_resource_complete(
    resource_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    completion = (
        db.query(ActivityCompletion)
        .filter(ActivityCompletion.student_id == current_user.id, ActivityCompletion.item_type == CompletionItemType.resource,
                ActivityCompletion.item_id == resource_id)
        .first()
    )
    if completion is not None:
        db.delete(completion)
        db.commit()


@router.post("/completion/{item_type}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def mark_complete_generic(
    item_type: CompletionItemType, item_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Cochage manuel générique — pour tout item dont le mode
    d'achèvement résolu est `manual` (voir Helper/completion_config.py).
    Les ressources gardent aussi leur endpoint dédié ci-dessus
    (inchangé, pour ne rien casser côté frontend existant)."""
    course_id = _resolve_course_id(db, item_type, item_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    if get_completion_mode(db, item_type, item_id) != CompletionMode.manual:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet item n'est pas en achèvement manuel")
    mark_complete_if_absent(db, current_user.id, item_type, item_id)


@router.delete("/completion/{item_type}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def unmark_complete_generic(
    item_type: CompletionItemType, item_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    completion = (
        db.query(ActivityCompletion)
        .filter(ActivityCompletion.student_id == current_user.id, ActivityCompletion.item_type == item_type,
                ActivityCompletion.item_id == item_id)
        .first()
    )
    if completion is not None:
        db.delete(completion)
        db.commit()


@router.get("/completion-config/{item_type}/{item_id}", response_model=CompletionConfigOut)
def get_completion_config(
    item_type: CompletionItemType, item_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    course_id = _resolve_course_id(db, item_type, item_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return CompletionConfigOut(item_type=item_type, item_id=item_id, mode=get_completion_mode(db, item_type, item_id))


@router.patch("/completion-config/{item_type}/{item_id}", response_model=CompletionConfigOut)
def update_completion_config(
    item_type: CompletionItemType, item_id: str, data: CompletionConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    course_id = _resolve_course_id(db, item_type, item_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    config = (
        db.query(ActivityCompletionConfig)
        .filter(ActivityCompletionConfig.item_type == item_type, ActivityCompletionConfig.item_id == item_id)
        .first()
    )
    if config is None:
        config = ActivityCompletionConfig(item_type=item_type, item_id=item_id, mode=data.mode)
        db.add(config)
    else:
        config.mode = data.mode
    db.commit()
    return CompletionConfigOut(item_type=item_type, item_id=item_id, mode=config.mode)


def _course_visible_items(db: Session, course_id: str):
    """Ne renvoie que les items dont le mode d'achèvement résolu n'est pas
    `none` — Ressource/Devoir/Quiz restent suivis par défaut (rétrocompat
    Phase 5), Forum/Sondage seulement si explicitement configurés (voir
    Helper/completion_config.py)."""
    sections = db.query(Section).filter(Section.course_id == course_id, Section.is_visible.is_(True)).all()
    candidates: list[tuple[CompletionItemType, object]] = []
    for s in sections:
        candidates += [(CompletionItemType.resource, r) for r in s.resources if r.is_visible]
        candidates += [(CompletionItemType.assignment, a) for a in s.assignments if a.is_visible]
        candidates += [(CompletionItemType.quiz, q) for q in s.quizzes if q.is_visible]
        candidates += [(CompletionItemType.forum, f) for f in s.forums if f.is_visible]
        candidates += [(CompletionItemType.choice, c) for c in s.choices if c.is_visible]
        candidates += [(CompletionItemType.lesson, l) for l in s.lessons if l.is_visible]
        candidates += [(CompletionItemType.workshop, w) for w in s.workshops if w.is_visible]
        candidates += [(CompletionItemType.live_session, ls) for ls in s.live_sessions if ls.is_visible]
        candidates += [(CompletionItemType.interactive_video, iv) for iv in s.interactive_videos if iv.is_visible]

    return [(t, item) for t, item in candidates if get_completion_mode(db, t, item.id) != CompletionMode.none]


@router.get("/courses/{course_id}/completion/mine", response_model=CompletionMineOut)
def get_my_completion(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    tracked_items = _course_visible_items(db, course_id)
    completions = {
        (c.item_type, c.item_id): c.completed_at
        for c in db.query(ActivityCompletion).filter(ActivityCompletion.student_id == current_user.id).all()
    }

    items = []
    for item_type, item in tracked_items:
        key = (item_type, item.id)
        items.append(CompletionItemOut(
            item_type=item_type, item_id=item.id, title=getattr(item, _TITLE_ATTR[item_type]),
            is_complete=key in completions, completed_at=completions.get(key),
        ))

    completed_count = sum(1 for i in items if i.is_complete)
    percent = (completed_count / len(items) * 100) if items else 0.0
    return CompletionMineOut(course_id=course_id, percent=percent, items=items)


@router.get("/courses/{course_id}/completion/report", response_model=list[CompletionReportRowOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def get_completion_report(course_id: str, db: Session = Depends(get_db)):
    tracked_items = _course_visible_items(db, course_id)
    total_count = len(tracked_items)
    item_keys = [(item_type, item.id) for item_type, item in tracked_items]

    roster = (
        db.query(Enrollment, User)
        .join(User, User.id == Enrollment.user_id)
        .filter(Enrollment.course_id == course_id, Enrollment.role_in_course == CourseRole.student,
                Enrollment.status == EnrollmentStatus.active)
        .all()
    )

    rows = []
    for enrollment, student in roster:
        completions = {
            (c.item_type, c.item_id)
            for c in db.query(ActivityCompletion).filter(ActivityCompletion.student_id == student.id).all()
        }
        completed_count = sum(1 for k in item_keys if k in completions)
        percent = (completed_count / total_count * 100) if total_count else 0.0
        rows.append(CompletionReportRowOut(
            student_id=student.id, student_name=f"{student.first_name} {student.last_name}",
            percent=percent, completed_count=completed_count, total_count=total_count,
        ))
    return rows
