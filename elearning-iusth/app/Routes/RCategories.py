from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import CourseCategory
from app.Models.MUser import SystemRole
from app.Schemas.SCourse import CourseCategoryCreate, CourseCategoryUpdate, CourseCategoryOut
from app.dependencies.auth import get_current_active_user, require_role

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CourseCategoryOut], dependencies=[Depends(get_current_active_user)])
def list_categories(db: Session = Depends(get_db)):
    return db.query(CourseCategory).order_by(CourseCategory.sort_order, CourseCategory.name).all()


@router.post("", response_model=CourseCategoryOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role([SystemRole.admin]))])
def create_category(data: CourseCategoryCreate, db: Session = Depends(get_db)):
    if db.query(CourseCategory).filter(CourseCategory.slug == data.slug).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce slug est déjà utilisé")
    category = CourseCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CourseCategoryOut,
              dependencies=[Depends(require_role([SystemRole.admin]))])
def update_category(category_id: str, data: CourseCategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(CourseCategory).filter(CourseCategory.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_role([SystemRole.admin]))])
def delete_category(category_id: str, db: Session = Depends(get_db)):
    category = db.query(CourseCategory).filter(CourseCategory.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    db.delete(category)
    db.commit()
