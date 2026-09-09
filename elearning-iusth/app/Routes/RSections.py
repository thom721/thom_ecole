from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Course, Section
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SCourse import SectionCreate, SectionUpdate, SectionOut
from app.dependencies.auth import get_current_active_user, require_course_role, assert_course_role

router = APIRouter(tags=["sections"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


@router.post("/courses/{course_id}/sections", response_model=SectionOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def create_section(course_id: str, data: SectionCreate, db: Session = Depends(get_db)):
    if db.query(Course).filter(Course.id == course_id).first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")
    section = Section(course_id=course_id, **data.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


@router.patch("/sections/{section_id}", response_model=SectionOut)
def update_section(
    section_id: str, data: SectionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    db.commit()
    db.refresh(section)
    return section


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    section_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)
    db.delete(section)
    db.commit()
