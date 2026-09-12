from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MAssignment import Assignment, Submission
from app.Models.MGrade import GradeItem, GradeItemKind
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Models.MAccessLog import AccessItemType
from app.Schemas.SAssignment import AssignmentCreate, AssignmentUpdate, AssignmentOut
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.access_log import log_access

router = APIRouter(tags=["assignments"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


@router.post("/sections/{section_id}/assignments", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
def create_assignment(
    section_id: str, data: AssignmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    assignment = Assignment(section_id=section_id, **data.model_dump())
    db.add(assignment)
    db.flush()

    # Auto-enregistrement au carnet de notes (voir plan Phase 3) — non
    # catégorisé par défaut, le professeur l'assigne ensuite via PATCH.
    db.add(GradeItem(course_id=section.course_id, assignment_id=assignment.id, kind=GradeItemKind.assignment))

    db.commit()
    db.refresh(assignment)
    return assignment


def _get_assignment_or_404(db: Session, assignment_id: str) -> Assignment:
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devoir introuvable")
    return assignment


@router.get("/assignments/{assignment_id}", response_model=AssignmentOut)
def get_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assignment = _get_assignment_or_404(db, assignment_id)
    section = db.query(Section).filter(Section.id == assignment.section_id).first()
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, section.course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    log_access(db, current_user, section.course_id, AccessItemType.assignment, assignment_id)
    return AssignmentOut.model_validate(assignment).model_copy(update={"course_id": section.course_id})


@router.patch("/assignments/{assignment_id}", response_model=AssignmentOut)
def update_assignment(
    assignment_id: str, data: AssignmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assignment = _get_assignment_or_404(db, assignment_id)
    section = db.query(Section).filter(Section.id == assignment.section_id).first()
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(assignment, field, value)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assignment = _get_assignment_or_404(db, assignment_id)
    section = db.query(Section).filter(Section.id == assignment.section_id).first()
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    if db.query(Submission).filter(Submission.assignment_id == assignment_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Ce devoir a déjà des soumissions — suppression bloquée pour préserver l'historique des notes")

    db.delete(assignment)
    db.commit()
