from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MWorkshop import (
    Workshop, WorkshopDimension, WorkshopRubricLevel, WorkshopNumerrorsMap,
    WorkshopSubmission, WorkshopPhase, WorkshopStrategy,
)
from app.Models.MGrade import GradeItem, GradeItemKind
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Models.MCompletion import CompletionItemType
from app.Schemas.SWorkshop import (
    WorkshopCreate, WorkshopUpdate, WorkshopOut, WorkshopPhaseIn,
    WorkshopDimensionOut, WorkshopDimensionsUpdate, WorkshopNumerrorsMapUpdate,
)
from app.dependencies.auth import get_current_active_user, assert_course_role
from app.Helper.completion import mark_complete_if_absent

router = APIRouter(tags=["workshops"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_workshop_and_course(db: Session, workshop_id: str) -> tuple[Workshop, str]:
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if workshop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atelier introuvable")
    section = db.query(Section).filter(Section.id == workshop.section_id).first()
    return workshop, section.course_id


@router.post("/sections/{section_id}/workshops", response_model=WorkshopOut, status_code=status.HTTP_201_CREATED)
def create_workshop(
    section_id: str, data: WorkshopCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    workshop = Workshop(section_id=section_id, **data.model_dump())
    db.add(workshop)
    db.flush()

    # Un atelier produit DEUX GradeItem (soumission + qualité d'évaluation),
    # partageant le même workshop_id, discriminés par kind (voir plan Épic 10).
    db.add(GradeItem(course_id=section.course_id, workshop_id=workshop.id, kind=GradeItemKind.workshop_submission))
    db.add(GradeItem(course_id=section.course_id, workshop_id=workshop.id, kind=GradeItemKind.workshop_grading))

    db.commit()
    db.refresh(workshop)
    return workshop


@router.get("/workshops/{workshop_id}", response_model=WorkshopOut)
def get_workshop(
    workshop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, _course_id = _get_workshop_and_course(db, workshop_id)
    return workshop


@router.get("/workshops/{workshop_id}/dimensions", response_model=list[WorkshopDimensionOut])
def get_dimensions(
    workshop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, _course_id = _get_workshop_and_course(db, workshop_id)
    return workshop.dimensions


@router.patch("/workshops/{workshop_id}", response_model=WorkshopOut)
def update_workshop(
    workshop_id: str, data: WorkshopUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(workshop, field, value)
    db.commit()
    db.refresh(workshop)
    return workshop


@router.post("/workshops/{workshop_id}/switch-phase", response_model=WorkshopOut)
def switch_phase(
    workshop_id: str, data: WorkshopPhaseIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    workshop.phase = data.phase
    db.commit()
    db.refresh(workshop)

    if data.phase == WorkshopPhase.closed:
        # Déclencheur unique de l'achèvement automatique (voir plan Épic 10,
        # même règle "un seul jalon" que l'Épic 7) : la fermeture de
        # l'atelier marque complet tout étudiant ayant une soumission.
        submissions = db.query(WorkshopSubmission).filter(WorkshopSubmission.workshop_id == workshop_id).all()
        for submission in submissions:
            mark_complete_if_absent(db, submission.author_id, CompletionItemType.workshop, workshop_id)

    return workshop


@router.delete("/workshops/{workshop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workshop(
    workshop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if db.query(WorkshopSubmission).filter(WorkshopSubmission.workshop_id == workshop_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Cet atelier a déjà des soumissions — suppression bloquée pour préserver l'historique des notes")

    db.delete(workshop)
    db.commit()


@router.put("/workshops/{workshop_id}/dimensions", response_model=list[WorkshopDimensionOut])
def replace_dimensions(
    workshop_id: str, data: WorkshopDimensionsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    for existing in list(workshop.dimensions):
        db.delete(existing)
    db.flush()

    for d in data.dimensions:
        dimension = WorkshopDimension(
            workshop_id=workshop_id, sort_order=d.sort_order, description=d.description,
            grade=d.grade if workshop.strategy == WorkshopStrategy.accumulative else None,
            weight=d.weight if workshop.strategy in (WorkshopStrategy.accumulative, WorkshopStrategy.numerrors) else 1,
            label_no=d.label_no if workshop.strategy == WorkshopStrategy.numerrors else None,
            label_yes=d.label_yes if workshop.strategy == WorkshopStrategy.numerrors else None,
        )
        db.add(dimension)
        if workshop.strategy == WorkshopStrategy.rubric:
            db.flush()
            for lvl in d.levels:
                db.add(WorkshopRubricLevel(dimension_id=dimension.id, grade=lvl.grade, definition=lvl.definition, sort_order=lvl.sort_order))

    db.commit()
    db.refresh(workshop)
    return workshop.dimensions


@router.get("/workshops/{workshop_id}/numerrors-map")
def get_numerrors_map(
    workshop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, _course_id = _get_workshop_and_course(db, workshop_id)
    return [{"error_count": r.error_count, "grade_percent": r.grade_percent} for r in workshop.numerrors_map]


@router.put("/workshops/{workshop_id}/numerrors-map")
def replace_numerrors_map(
    workshop_id: str, data: WorkshopNumerrorsMapUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    if workshop.strategy != WorkshopStrategy.numerrors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette table ne s'applique qu'à la stratégie 'nombre d'erreurs'")

    for existing in list(workshop.numerrors_map):
        db.delete(existing)
    db.flush()
    for row in data.rows:
        db.add(WorkshopNumerrorsMap(workshop_id=workshop_id, error_count=row.error_count, grade_percent=row.grade_percent))
    db.commit()
    db.refresh(workshop)
    return [{"error_count": r.error_count, "grade_percent": r.grade_percent} for r in workshop.numerrors_map]
