from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MGrade import GradeCategory, GradeItem
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SGrade import GradeCategoryCreate, GradeCategoryUpdate, GradeCategoryOut
from app.dependencies.auth import require_course_role, assert_course_role, get_current_active_user

router = APIRouter(tags=["grade-categories"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


@router.get("/courses/{course_id}/grade-categories", response_model=list[GradeCategoryOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def list_categories(course_id: str, db: Session = Depends(get_db)):
    return db.query(GradeCategory).filter(GradeCategory.course_id == course_id).order_by(GradeCategory.sort_order).all()


@router.post("/courses/{course_id}/grade-categories", response_model=GradeCategoryOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def create_category(course_id: str, data: GradeCategoryCreate, db: Session = Depends(get_db)):
    category = GradeCategory(course_id=course_id, **data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def _get_category_or_404(db: Session, category_id: str) -> GradeCategory:
    category = db.query(GradeCategory).filter(GradeCategory.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    return category


@router.patch("/grade-categories/{category_id}", response_model=GradeCategoryOut)
def update_category(
    category_id: str, data: GradeCategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    category = _get_category_or_404(db, category_id)
    assert_course_role(db, current_user, category.course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/grade-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    category = _get_category_or_404(db, category_id)
    assert_course_role(db, current_user, category.course_id, _TEACHING_ROLES)
    if db.query(GradeItem).filter(GradeItem.grade_category_id == category_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Catégorie utilisée par des items de note — réassignez-les d'abord")
    db.delete(category)
    db.commit()
