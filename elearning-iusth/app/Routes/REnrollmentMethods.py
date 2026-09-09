from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Course
from app.Models.MEnrollment import Enrollment, EnrollmentStatus, CourseRole
from app.Models.MEnrollmentMethod import CourseEnrollmentSettings, Cohort, CohortSync
from app.Models.MUser import User
from app.Schemas.SEnrollmentMethod import (
    CourseEnrollmentSettingsUpdate, CourseEnrollmentSettingsOut, SelfEnrollIn,
    CohortSyncCreate, CohortSyncOut,
)
from app.Schemas.SEnrollment import EnrollmentOut
from app.dependencies.auth import get_current_active_user, assert_course_role, get_enrollment_or_none
from app.Helper.cohort_sync import sync_created, sync_removed

router = APIRouter(tags=["enrollment-methods"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_or_create_settings(db: Session, course_id: str) -> CourseEnrollmentSettings:
    settings = db.query(CourseEnrollmentSettings).filter(CourseEnrollmentSettings.course_id == course_id).first()
    if settings is None:
        settings = CourseEnrollmentSettings(course_id=course_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/courses/{course_id}/enrollment-settings", response_model=CourseEnrollmentSettingsOut)
def get_enrollment_settings(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return _get_or_create_settings(db, course_id)


@router.patch("/courses/{course_id}/enrollment-settings", response_model=CourseEnrollmentSettingsOut)
def update_enrollment_settings(
    course_id: str, data: CourseEnrollmentSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    settings = _get_or_create_settings(db, course_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings


def _get_course_or_404(db: Session, course_id: str) -> Course:
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")
    return course


@router.post("/courses/{course_id}/enroll-self", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
def enroll_self(
    course_id: str, data: SelfEnrollIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _get_course_or_404(db, course_id)
    settings = db.query(CourseEnrollmentSettings).filter(CourseEnrollmentSettings.course_id == course_id).first()
    if settings is None or not settings.self_enrollment_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="L'auto-inscription n'est pas activée pour ce cours")
    if settings.self_enrollment_key and settings.self_enrollment_key != data.key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Code d'inscription incorrect")

    if get_enrollment_or_none(db, course_id, current_user.id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà inscrit à ce cours")

    enrollment = Enrollment(course_id=course_id, user_id=current_user.id, role_in_course=CourseRole.student, method="self")
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.post("/courses/{course_id}/enroll-guest", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
def enroll_guest(
    course_id: str, data: SelfEnrollIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Inscrit avec le rôle student habituel — la restriction lecture
    seule d'un vrai accès invité N'EST PAS appliquée (limite documentée,
    voir plan Épic 6 : resserrer l'écriture demanderait d'auditer 11
    fichiers de routes, hors périmètre de cet epic)."""
    _get_course_or_404(db, course_id)
    settings = db.query(CourseEnrollmentSettings).filter(CourseEnrollmentSettings.course_id == course_id).first()
    if settings is None or not settings.guest_access_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="L'accès invité n'est pas activé pour ce cours")
    if settings.guest_access_key and settings.guest_access_key != data.key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Code d'accès incorrect")

    if get_enrollment_or_none(db, course_id, current_user.id) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Déjà inscrit à ce cours")

    enrollment = Enrollment(course_id=course_id, user_id=current_user.id, role_in_course=CourseRole.student, method="guest")
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/courses/{course_id}/cohort-syncs", response_model=list[CohortSyncOut])
def list_cohort_syncs(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    syncs = db.query(CohortSync).filter(CohortSync.course_id == course_id).all()
    return [
        CohortSyncOut(id=s.id, course_id=s.course_id, cohort_id=s.cohort_id, cohort_name=s.cohort.name, role=s.role)
        for s in syncs
    ]


@router.post("/courses/{course_id}/cohort-syncs", response_model=CohortSyncOut, status_code=status.HTTP_201_CREATED)
def create_cohort_sync(
    course_id: str, data: CohortSyncCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    cohort = db.query(Cohort).filter(Cohort.id == data.cohort_id).first()
    if cohort is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohorte introuvable")
    if db.query(CohortSync).filter(CohortSync.course_id == course_id, CohortSync.cohort_id == data.cohort_id).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette cohorte est déjà synchronisée avec ce cours")

    sync = CohortSync(course_id=course_id, cohort_id=data.cohort_id, role=data.role)
    db.add(sync)
    db.commit()
    db.refresh(sync)
    sync_created(db, data.cohort_id, course_id, data.role)
    return CohortSyncOut(id=sync.id, course_id=sync.course_id, cohort_id=sync.cohort_id, cohort_name=cohort.name, role=sync.role)


@router.delete("/cohort-syncs/{sync_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cohort_sync(
    sync_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    sync = db.query(CohortSync).filter(CohortSync.id == sync_id).first()
    if sync is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Synchronisation introuvable")
    assert_course_role(db, current_user, sync.course_id, _TEACHING_ROLES)
    course_id, cohort_id = sync.course_id, sync.cohort_id
    db.delete(sync)
    db.commit()
    sync_removed(db, cohort_id, course_id)
