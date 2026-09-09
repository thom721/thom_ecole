from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MQuestion import QuestionCategory, Question
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SQuestion import QuestionCategoryCreate, QuestionCategoryUpdate, QuestionCategoryOut
from app.dependencies.auth import require_course_role, assert_course_role, get_current_active_user

router = APIRouter(tags=["question-categories"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


@router.get("/courses/{course_id}/question-categories", response_model=list[QuestionCategoryOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def list_categories(course_id: str, db: Session = Depends(get_db)):
    return db.query(QuestionCategory).filter(QuestionCategory.course_id == course_id).order_by(QuestionCategory.name).all()


@router.post("/courses/{course_id}/question-categories", response_model=QuestionCategoryOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def create_category(course_id: str, data: QuestionCategoryCreate, db: Session = Depends(get_db)):
    category = QuestionCategory(course_id=course_id, name=data.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def _get_category_or_404(db: Session, category_id: str) -> QuestionCategory:
    category = db.query(QuestionCategory).filter(QuestionCategory.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    return category


@router.patch("/question-categories/{category_id}", response_model=QuestionCategoryOut)
def update_category(
    category_id: str, data: QuestionCategoryUpdate,
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


@router.delete("/question-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    category = _get_category_or_404(db, category_id)
    assert_course_role(db, current_user, category.course_id, _TEACHING_ROLES)
    if db.query(Question).filter(Question.category_id == category_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Catégorie utilisée par des questions — réassignez-les d'abord")
    db.delete(category)
    db.commit()
