from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MEnrollment import Enrollment, CourseRole
from app.Models.MUser import User
from app.Schemas.SEnrollment import EnrollmentCreate, EnrollmentOut
from app.dependencies.auth import get_current_active_user, require_course_role, assert_course_role

router = APIRouter(tags=["enrollments"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


@router.post("/courses/{course_id}/enrollments", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def enroll_user(
    course_id: str, data: EnrollmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course_id, Enrollment.user_id == data.user_id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà inscrit à ce cours")

    enrollment = Enrollment(
        course_id=course_id, user_id=data.user_id,
        role_in_course=data.role_in_course, enrolled_by=current_user.id, method="manual",
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/courses/{course_id}/enrollments", response_model=list[EnrollmentOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def list_enrollments(course_id: str, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    users_by_id = {
        u.id: u
        for u in db.query(User).filter(User.id.in_([e.user_id for e in enrollments])).all()
    } if enrollments else {}
    return [
        EnrollmentOut.model_validate(e).model_copy(update={
            "user_name": f"{users_by_id[e.user_id].first_name} {users_by_id[e.user_id].last_name}" if e.user_id in users_by_id else None,
            "user_email": users_by_id[e.user_id].email if e.user_id in users_by_id else None,
        })
        for e in enrollments
    ]


@router.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll(
    enrollment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscription introuvable")
    assert_course_role(db, current_user, enrollment.course_id, _TEACHING_ROLES)
    db.delete(enrollment)
    db.commit()
