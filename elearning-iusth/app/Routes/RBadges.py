from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MBadge import Badge, BadgeCriterion, BadgeCriterionMet, BadgeIssued, BadgeCriteriaType
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SBadge import (
    BadgeCreate, BadgeUpdate, BadgeOut, BadgeDetailOut, BadgeCriteriaUpdate, BadgeCriterionOut,
    BadgeAwardIn, BadgeIssuedOut, BadgeMineOut, BadgeProgressCriterionOut,
)
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role, require_role
from app.Helper.badges import evaluate_criterion, evaluate_badges_for_student

router = APIRouter(tags=["badges"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]
_COURSE_SCOPED_TYPES = {BadgeCriteriaType.course, BadgeCriteriaType.grade}


def _get_badge_or_404(db: Session, badge_id: str) -> Badge:
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if badge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Badge introuvable")
    return badge


def _to_detail_out(badge: Badge) -> BadgeDetailOut:
    return BadgeDetailOut(
        id=badge.id, course_id=badge.course_id, name=badge.name, description=badge.description,
        image_emoji=badge.image_emoji, status=badge.status, criteria_logic=badge.criteria_logic,
        expire_days=badge.expire_days, criteria=[BadgeCriterionOut.model_validate(c) for c in badge.criteria],
    )


@router.get("/courses/{course_id}/badges", response_model=list[BadgeOut])
def list_course_badges(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if get_enrollment_or_none(db, course_id, current_user.id) is None and current_user.system_role != SystemRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return db.query(Badge).filter(or_(Badge.course_id == course_id, Badge.course_id.is_(None))).all()


@router.post("/courses/{course_id}/badges", response_model=BadgeOut, status_code=status.HTTP_201_CREATED)
def create_course_badge(
    course_id: str, data: BadgeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    badge = Badge(course_id=course_id, created_by=current_user.id, **data.model_dump())
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


@router.post("/badges/site", response_model=BadgeOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role([SystemRole.admin]))])
def create_site_badge(
    data: BadgeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    badge = Badge(course_id=None, created_by=current_user.id, **data.model_dump())
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


@router.get("/badges/mine", response_model=list[BadgeMineOut])
def my_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    issued = db.query(BadgeIssued).filter(BadgeIssued.user_id == current_user.id).all()
    badges = [i.badge for i in issued]
    return _serialize_mine(db, badges, current_user.id, issued_map={i.badge_id: i for i in issued})


# Déclaré AVANT /badges/{badge_id} — une route statique après une route
# dynamique de même profondeur serait toujours masquée par elle (bug déjà
# rencontré et corrigé en Épic 4 : Starlette matche par ordre de
# déclaration, pas par spécificité).
@router.get("/badges/{badge_id}", response_model=BadgeDetailOut)
def get_badge(
    badge_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    badge = _get_badge_or_404(db, badge_id)
    if badge.course_id:
        if get_enrollment_or_none(db, badge.course_id, current_user.id) is None and current_user.system_role != SystemRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return _to_detail_out(badge)


def _assert_can_manage_badge(db: Session, current_user: User, badge: Badge):
    if badge.course_id is None:
        if current_user.system_role != SystemRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Réservé à un administrateur")
    else:
        assert_course_role(db, current_user, badge.course_id, _TEACHING_ROLES)


@router.patch("/badges/{badge_id}", response_model=BadgeOut)
def update_badge(
    badge_id: str, data: BadgeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    badge = _get_badge_or_404(db, badge_id)
    _assert_can_manage_badge(db, current_user, badge)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(badge, field, value)
    db.commit()
    db.refresh(badge)
    return badge


@router.delete("/badges/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_badge(
    badge_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    badge = _get_badge_or_404(db, badge_id)
    _assert_can_manage_badge(db, current_user, badge)
    if db.query(BadgeIssued).filter(BadgeIssued.badge_id == badge_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Ce badge a déjà été émis — suppression bloquée pour préserver l'historique")
    db.delete(badge)
    db.commit()


@router.put("/badges/{badge_id}/criteria", response_model=BadgeDetailOut)
def replace_criteria(
    badge_id: str, data: BadgeCriteriaUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    badge = _get_badge_or_404(db, badge_id)
    _assert_can_manage_badge(db, current_user, badge)

    if db.query(BadgeIssued).filter(BadgeIssued.badge_id == badge_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Ce badge a déjà été émis — les critères ne peuvent plus être modifiés")

    if badge.course_id is None:
        for c in data.criteria:
            if c.criteria_type in _COURSE_SCOPED_TYPES:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                     detail="Un badge site ne peut pas avoir de critère de cours ou de note")

    for existing in list(badge.criteria):
        db.delete(existing)
    db.flush()
    for c in data.criteria:
        db.add(BadgeCriterion(badge_id=badge_id, logic=badge.criteria_logic, **c.model_dump()))
    db.commit()
    db.refresh(badge)
    return _to_detail_out(badge)


@router.post("/badges/{badge_id}/award", response_model=BadgeIssuedOut, status_code=status.HTTP_201_CREATED)
def award_badge_manually(
    badge_id: str, data: BadgeAwardIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    import secrets

    badge = _get_badge_or_404(db, badge_id)
    _assert_can_manage_badge(db, current_user, badge)

    existing = db.query(BadgeIssued).filter(BadgeIssued.badge_id == badge_id, BadgeIssued.user_id == data.user_id).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce badge a déjà été émis à cet utilisateur")

    issued = BadgeIssued(badge_id=badge_id, user_id=data.user_id, unique_hash=secrets.token_hex(32), awarded_manually=True)
    db.add(issued)
    db.commit()
    db.refresh(issued)
    return issued


@router.post("/courses/{course_id}/badges/reevaluate")
def reevaluate_course_badges(
    course_id: str,
    student_id: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Filet de sécurité sans tâche planifiée (voir plan Épic 12) — un
    professeur peut réévaluer pour un étudiant précis (`student_id`) ou
    tous les inscrits ; un étudiant ne peut réévaluer que pour lui-même."""
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    is_teaching = enrollment is not None and enrollment.role_in_course in _TEACHING_ROLES or current_user.system_role == SystemRole.admin

    if student_id and not is_teaching and student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez réévaluer que vos propres badges")

    if student_id:
        targets = [student_id]
    elif is_teaching:
        from app.Models.MEnrollment import Enrollment, EnrollmentStatus
        targets = [
            e.user_id for e in db.query(Enrollment).filter(
                Enrollment.course_id == course_id, Enrollment.role_in_course == CourseRole.student,
                Enrollment.status == EnrollmentStatus.active,
            ).all()
        ]
    else:
        if enrollment is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
        targets = [current_user.id]

    for uid in targets:
        evaluate_badges_for_student(db, uid, course_id)
    return {"reevaluated": len(targets)}


@router.get("/courses/{course_id}/badges/mine", response_model=list[BadgeMineOut])
def my_course_badges(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    badges = db.query(Badge).filter(or_(Badge.course_id == course_id, Badge.course_id.is_(None))).all()
    return _serialize_mine(db, badges, current_user.id)


def _serialize_mine(db: Session, badges: list[Badge], student_id: str, issued_map: dict | None = None) -> list[BadgeMineOut]:
    if issued_map is None:
        rows = db.query(BadgeIssued).filter(
            BadgeIssued.badge_id.in_([b.id for b in badges]), BadgeIssued.user_id == student_id,
        ).all() if badges else []
        issued_map = {r.badge_id: r for r in rows}

    out = []
    for badge in badges:
        issued = issued_map.get(badge.id)
        progress = [
            BadgeProgressCriterionOut(criteria_type=c.criteria_type, met=evaluate_criterion(db, c, student_id, badge.course_id))
            for c in badge.criteria
        ] if issued is None else []
        out.append(BadgeMineOut(
            id=badge.id, name=badge.name, description=badge.description, image_emoji=badge.image_emoji,
            course_id=badge.course_id, is_earned=issued is not None,
            issued_at=issued.issued_at if issued else None, criteria_progress=progress,
        ))
    return out
