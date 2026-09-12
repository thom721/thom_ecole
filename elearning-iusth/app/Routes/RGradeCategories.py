from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MGrade import GradeCategory, GradeItem
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SGrade import GradeCategoryCreate, GradeCategoryUpdate, GradeCategoryOut
from app.dependencies.auth import require_course_role, assert_course_role, get_current_active_user

router = APIRouter(tags=["grade-categories"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]

_PHASES = ("intra", "finale")


def _validate_phase_weight(db: Session, course_id: str, phase: str | None,
                            new_weight: Decimal, exclude_category_id: str | None = None) -> None:
    """weight_percent d'une catégorie taguée 'intra'/'finale' représente une
    allocation ABSOLUE du total de la phase côté ecole_nginx (voir
    RGrades.py::_build_report) — la somme des poids des catégories d'une
    même phase ne doit donc jamais dépasser 100% (= la totalité du
    coefficient de l'Intra ou du Final), sinon les devoirs réclameraient
    plus que la note maximale possible."""
    if phase not in _PHASES:
        return
    query = db.query(func.sum(GradeCategory.weight_percent)).filter(
        GradeCategory.course_id == course_id,
        GradeCategory.evaluation_phase == phase,
    )
    if exclude_category_id:
        query = query.filter(GradeCategory.id != exclude_category_id)
    existing_total = query.scalar() or Decimal("0")
    total = existing_total + new_weight
    if total > 100:
        label = "Intra" if phase == "intra" else "Final"
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"La somme des poids des catégories '{label}' dépasserait 100% ({total}%) — "
                f"ce serait plus que le total possible de l'{label}. Réduisez ce poids ou celui "
                f"d'une autre catégorie '{label}' de ce cours."
            ),
        )


@router.get("/courses/{course_id}/grade-categories", response_model=list[GradeCategoryOut],
            dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def list_categories(course_id: str, db: Session = Depends(get_db)):
    return db.query(GradeCategory).filter(GradeCategory.course_id == course_id).order_by(GradeCategory.sort_order).all()


@router.post("/courses/{course_id}/grade-categories", response_model=GradeCategoryOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_course_role(_TEACHING_ROLES))])
def create_category(course_id: str, data: GradeCategoryCreate, db: Session = Depends(get_db)):
    _validate_phase_weight(db, course_id, data.evaluation_phase, data.weight_percent)
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

    updates = data.model_dump(exclude_unset=True)
    resulting_phase = updates.get('evaluation_phase', category.evaluation_phase)
    resulting_weight = updates.get('weight_percent', category.weight_percent)
    _validate_phase_weight(db, category.course_id, resulting_phase, resulting_weight, exclude_category_id=category.id)

    for field, value in updates.items():
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
