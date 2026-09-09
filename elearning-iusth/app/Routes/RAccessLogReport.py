from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.Models.MAccessLog import AccessLog, AccessItemType
from app.Models.MResource import Resource
from app.Models.MAssignment import Assignment
from app.Models.MQuiz import Quiz
from app.Models.MCourse import Course
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SAccessLog import AccessLogSummaryOut, AccessLogStudentOut
from app.dependencies.auth import require_course_role

router = APIRouter(tags=["access-log"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _item_title(db: Session, item_type: AccessItemType, item_id: str | None, course_id: str) -> str:
    if item_type == AccessItemType.course:
        course = db.query(Course).filter(Course.id == course_id).first()
        return course.full_name if course else "Cours"
    if item_type == AccessItemType.resource:
        r = db.query(Resource).filter(Resource.id == item_id).first()
        return r.title if r else "Ressource supprimée"
    if item_type == AccessItemType.assignment:
        a = db.query(Assignment).filter(Assignment.id == item_id).first()
        return a.title if a else "Devoir supprimé"
    if item_type == AccessItemType.quiz:
        q = db.query(Quiz).filter(Quiz.id == item_id).first()
        return q.title if q else "Quiz supprimé"
    return "?"


@router.get("/courses/{course_id}/access-log/summary", response_model=list[AccessLogSummaryOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def get_summary(course_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(
            AccessLog.item_type, AccessLog.item_id,
            func.count(AccessLog.id).label("view_count"),
            func.count(func.distinct(AccessLog.user_id)).label("unique_student_count"),
            func.max(AccessLog.accessed_at).label("last_accessed_at"),
        )
        .filter(AccessLog.course_id == course_id)
        .group_by(AccessLog.item_type, AccessLog.item_id)
        .order_by(func.count(AccessLog.id).desc())
        .all()
    )
    return [
        AccessLogSummaryOut(
            item_type=r.item_type, item_id=r.item_id,
            title=_item_title(db, r.item_type, r.item_id, course_id),
            view_count=r.view_count, unique_student_count=r.unique_student_count,
            last_accessed_at=r.last_accessed_at,
        )
        for r in rows
    ]


@router.get("/courses/{course_id}/access-log/students", response_model=list[AccessLogStudentOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def get_student_summary(course_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(
            AccessLog.user_id,
            func.count(AccessLog.id).label("total_views"),
            func.max(AccessLog.accessed_at).label("last_accessed_at"),
        )
        .filter(AccessLog.course_id == course_id)
        .group_by(AccessLog.user_id)
        .order_by(func.count(AccessLog.id).desc())
        .all()
    )
    result = []
    for r in rows:
        student = db.query(User).filter(User.id == r.user_id).first()
        result.append(AccessLogStudentOut(
            student_id=r.user_id, student_name=f"{student.first_name} {student.last_name}" if student else "?",
            total_views=r.total_views, last_accessed_at=r.last_accessed_at,
        ))
    return result
