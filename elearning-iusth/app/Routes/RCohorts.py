from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MEnrollmentMethod import Cohort, CohortMember
from app.Models.MUser import User, SystemRole
from app.Schemas.SEnrollmentMethod import (
    CohortCreate, CohortUpdate, CohortOut, CohortDetailOut, CohortMemberOut, AddCohortMemberIn,
)
from app.dependencies.auth import require_role, get_current_active_user
from app.Helper.cohort_sync import sync_member_added, sync_member_removed
from app.Helper.badges import evaluate_badges_for_cohort_member

router = APIRouter(prefix="/cohorts", tags=["cohorts"])


def _get_cohort_or_404(db: Session, cohort_id: str) -> Cohort:
    cohort = db.query(Cohort).filter(Cohort.id == cohort_id).first()
    if cohort is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohorte introuvable")
    return cohort


def _cohort_detail(db: Session, cohort: Cohort) -> CohortDetailOut:
    members = []
    for m in cohort.members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            members.append(CohortMemberOut(user_id=user.id, name=f"{user.first_name} {user.last_name}", email=user.email))
    return CohortDetailOut(id=cohort.id, name=cohort.name, description=cohort.description, members=members)


@router.get("", response_model=list[CohortDetailOut])
def list_cohorts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Lecture ouverte à tout enseignant/admin — un enseignant doit pouvoir
    # choisir une cohorte à synchroniser avec son cours (voir
    # REnrollmentMethods.py::create_cohort_sync) sans pouvoir gérer les
    # cohortes elles-mêmes (création/membres restent admin uniquement).
    if current_user.system_role not in (SystemRole.teacher, SystemRole.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle insuffisant")
    return [_cohort_detail(db, c) for c in db.query(Cohort).all()]


@router.post("", response_model=CohortOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role([SystemRole.admin]))])
def create_cohort(data: CohortCreate, db: Session = Depends(get_db)):
    cohort = Cohort(**data.model_dump())
    db.add(cohort)
    db.commit()
    db.refresh(cohort)
    return cohort


@router.patch("/{cohort_id}", response_model=CohortOut, dependencies=[Depends(require_role([SystemRole.admin]))])
def update_cohort(cohort_id: str, data: CohortUpdate, db: Session = Depends(get_db)):
    cohort = _get_cohort_or_404(db, cohort_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cohort, field, value)
    db.commit()
    db.refresh(cohort)
    return cohort


@router.delete("/{cohort_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role([SystemRole.admin]))])
def delete_cohort(cohort_id: str, db: Session = Depends(get_db)):
    cohort = _get_cohort_or_404(db, cohort_id)
    db.delete(cohort)
    db.commit()


@router.post("/{cohort_id}/members", response_model=CohortDetailOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role([SystemRole.admin]))])
def add_cohort_member(cohort_id: str, data: AddCohortMemberIn, db: Session = Depends(get_db)):
    cohort = _get_cohort_or_404(db, cohort_id)
    if db.query(CohortMember).filter(CohortMember.cohort_id == cohort_id, CohortMember.user_id == data.user_id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà membre de cette cohorte")

    db.add(CohortMember(cohort_id=cohort_id, user_id=data.user_id))
    db.commit()
    sync_member_added(db, cohort_id, data.user_id)
    evaluate_badges_for_cohort_member(db, cohort_id, data.user_id)
    db.refresh(cohort)
    return _cohort_detail(db, cohort)


@router.delete("/{cohort_id}/members/{user_id}", response_model=CohortDetailOut,
               dependencies=[Depends(require_role([SystemRole.admin]))])
def remove_cohort_member(cohort_id: str, user_id: str, db: Session = Depends(get_db)):
    cohort = _get_cohort_or_404(db, cohort_id)
    member = db.query(CohortMember).filter(CohortMember.cohort_id == cohort_id, CohortMember.user_id == user_id).first()
    if member:
        db.delete(member)
        db.commit()
        sync_member_removed(db, cohort_id, user_id)
    db.refresh(cohort)
    return _cohort_detail(db, cohort)
