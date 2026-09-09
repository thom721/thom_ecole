from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MScale import Scale, ScaleLevel
from app.Models.MAssignment import Assignment
from app.Models.MGrade import GradeItem
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SScale import ScaleCreate, ScaleOut
from app.dependencies.auth import get_current_active_user, assert_course_role, require_role

router = APIRouter(tags=["scales"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


@router.get("/courses/{course_id}/scales", response_model=list[ScaleOut])
def list_scales(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return db.query(Scale).filter(or_(Scale.course_id == course_id, Scale.course_id.is_(None))).all()


@router.post("/courses/{course_id}/scales", response_model=ScaleOut, status_code=status.HTTP_201_CREATED)
def create_scale(
    course_id: str, data: ScaleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    if not data.levels:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une échelle nécessite au moins un niveau")

    scale = Scale(course_id=course_id, name=data.name, description=data.description, created_by=current_user.id)
    db.add(scale)
    db.flush()
    for level in data.levels:
        db.add(ScaleLevel(scale_id=scale.id, **level.model_dump()))
    db.commit()
    db.refresh(scale)
    return scale


@router.post("/scales/site", response_model=ScaleOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role([SystemRole.admin]))])
def create_site_scale(
    data: ScaleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Échelle réutilisable par n'importe quel cours (course_id=null) —
    admin uniquement, voir plan Épic 8."""
    if not data.levels:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une échelle nécessite au moins un niveau")

    scale = Scale(course_id=None, name=data.name, description=data.description, created_by=current_user.id)
    db.add(scale)
    db.flush()
    for level in data.levels:
        db.add(ScaleLevel(scale_id=scale.id, **level.model_dump()))
    db.commit()
    db.refresh(scale)
    return scale


def _get_scale_or_404(db: Session, scale_id: str) -> Scale:
    scale = db.query(Scale).filter(Scale.id == scale_id).first()
    if scale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Échelle introuvable")
    return scale


@router.delete("/scales/{scale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scale(
    scale_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    scale = _get_scale_or_404(db, scale_id)
    if scale.course_id is None:
        if current_user.system_role != SystemRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle insuffisant")
    else:
        assert_course_role(db, current_user, scale.course_id, _TEACHING_ROLES)

    referenced = (
        db.query(Assignment).filter(Assignment.scale_id == scale_id).first() is not None
        or db.query(GradeItem).filter(GradeItem.scale_id == scale_id).first() is not None
    )
    if referenced:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Cette échelle est utilisée par un devoir ou un item de notes — suppression bloquée")

    db.delete(scale)
    db.commit()
