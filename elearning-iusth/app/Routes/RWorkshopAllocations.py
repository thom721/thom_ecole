import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MWorkshop import Workshop, WorkshopSubmission, WorkshopAssessment
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Schemas.SWorkshop import WorkshopAllocateManualIn, WorkshopAllocateRandomIn, WorkshopAssessmentOut
from app.dependencies.auth import get_current_active_user, assert_course_role

router = APIRouter(tags=["workshop-allocations"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_workshop_and_course(db: Session, workshop_id: str) -> tuple[Workshop, str]:
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if workshop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atelier introuvable")
    section = db.query(Section).filter(Section.id == workshop.section_id).first()
    return workshop, section.course_id


def _validate_reviewer(workshop: Workshop, submission: WorkshopSubmission, reviewer_id: str):
    is_self = reviewer_id == submission.author_id
    if is_self and not workshop.use_self_assessment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auto-évaluation désactivée pour cet atelier")
    if not is_self and not workshop.use_peer_assessment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Évaluation par les pairs désactivée pour cet atelier")


@router.post("/workshops/{workshop_id}/allocate/manual", response_model=WorkshopAssessmentOut, status_code=status.HTTP_201_CREATED)
def allocate_manual(
    workshop_id: str, data: WorkshopAllocateManualIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    submission = db.query(WorkshopSubmission).filter(WorkshopSubmission.id == data.submission_id, WorkshopSubmission.workshop_id == workshop_id).first()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soumission introuvable")

    _validate_reviewer(workshop, submission, data.reviewer_id)

    existing = db.query(WorkshopAssessment).filter(
        WorkshopAssessment.submission_id == data.submission_id, WorkshopAssessment.reviewer_id == data.reviewer_id,
    ).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette évaluation existe déjà")

    assessment = WorkshopAssessment(submission_id=data.submission_id, reviewer_id=data.reviewer_id, weight=data.weight)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.delete("/workshop-assessments/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assessment = db.query(WorkshopAssessment).filter(WorkshopAssessment.id == assessment_id).first()
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Évaluation introuvable")
    _workshop, course_id = _get_workshop_and_course(db, assessment.submission.workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    db.delete(assessment)
    db.commit()


@router.post("/workshops/{workshop_id}/allocate/random", response_model=list[WorkshopAssessmentOut])
def allocate_random(
    workshop_id: str, data: WorkshopAllocateRandomIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Répartition aléatoire déclenchée explicitement par le professeur
    (pas de tâche planifiée/cron dans ce projet, voir plan Épic 10) :
    mélange les auteurs, attribue à chaque soumission N évaluateurs
    distincts par décalage circulaire — charge à peu près équilibrée,
    jamais l'auteur lui-même sauf si `use_self_assessment`."""
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    submissions = list(workshop.submissions)
    if len(submissions) < 2 and not workshop.use_self_assessment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pas assez de soumissions pour une répartition croisée")

    authors = [s.author_id for s in submissions]
    n = data.reviews_per_submission
    created = []

    for submission in submissions:
        eligible = [a for a in authors if a != submission.author_id]
        if workshop.use_self_assessment:
            eligible.append(submission.author_id)
        random.shuffle(eligible)

        existing_reviewer_ids = {a.reviewer_id for a in submission.assessments}
        candidates = [r for r in eligible if r not in existing_reviewer_ids]
        chosen = candidates[:n]

        for reviewer_id in chosen:
            assessment = WorkshopAssessment(submission_id=submission.id, reviewer_id=reviewer_id, weight=1)
            db.add(assessment)
            created.append(assessment)

    db.commit()
    for a in created:
        db.refresh(a)
    return created
