from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MScale import GradeLetter
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SScale import GradeLetterOut, GradeLettersUpdate
from app.dependencies.auth import get_current_active_user, assert_course_role

router = APIRouter(tags=["grade-letters"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


@router.get("/courses/{course_id}/grade-letters", response_model=list[GradeLetterOut])
def list_grade_letters(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return db.query(GradeLetter).filter(GradeLetter.course_id == course_id).order_by(GradeLetter.lower_boundary.desc()).all()


@router.put("/courses/{course_id}/grade-letters", response_model=list[GradeLetterOut])
def replace_grade_letters(
    course_id: str, data: GradeLettersUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remplacement intégral (pas de diff) — même convention que les
    options de question (voir plan Épic 1/8)."""
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    for existing in db.query(GradeLetter).filter(GradeLetter.course_id == course_id).all():
        db.delete(existing)
    db.flush()
    for item in data.letters:
        db.add(GradeLetter(course_id=course_id, **item.model_dump()))
    db.commit()

    return db.query(GradeLetter).filter(GradeLetter.course_id == course_id).order_by(GradeLetter.lower_boundary.desc()).all()
