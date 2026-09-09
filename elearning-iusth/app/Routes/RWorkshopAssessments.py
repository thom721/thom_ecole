from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MWorkshop import Workshop, WorkshopAssessment, WorkshopGrade, WorkshopPhase, WorkshopStrategy
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Models.MNotification import NotificationKind
from app.Schemas.SWorkshop import WorkshopAssessmentOut, WorkshopAssessmentGradesUpdate, WorkshopFeedbackReviewerIn
from app.dependencies.auth import get_current_active_user, assert_course_role
from app.Helper.notifications import notify
from app.Helper.workshop_grading import assessment_grade_percent, assessment_final_gradinggrade_percent

router = APIRouter(tags=["workshop-assessments"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_workshop_and_course(db: Session, workshop_id: str) -> tuple[Workshop, str]:
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if workshop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atelier introuvable")
    section = db.query(Section).filter(Section.id == workshop.section_id).first()
    return workshop, section.course_id


def _get_assessment_or_404(db: Session, assessment_id: str) -> WorkshopAssessment:
    assessment = db.query(WorkshopAssessment).filter(WorkshopAssessment.id == assessment_id).first()
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Évaluation introuvable")
    return assessment


def _to_out(assessment: WorkshopAssessment) -> WorkshopAssessmentOut:
    out = WorkshopAssessmentOut.model_validate(assessment)
    out.grade_percent = assessment_grade_percent(assessment)
    out.gradinggrade_percent = assessment_final_gradinggrade_percent(assessment)
    return out


@router.get("/workshop-assessments/mine", response_model=list[WorkshopAssessmentOut])
def list_my_assessments(
    workshop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assessments = (
        db.query(WorkshopAssessment)
        .join(WorkshopAssessment.submission)
        .filter(WorkshopAssessment.reviewer_id == current_user.id)
        .all()
    )
    assessments = [a for a in assessments if a.submission.workshop_id == workshop_id]
    return [_to_out(a) for a in assessments]


@router.get("/workshop-assessments/{assessment_id}", response_model=WorkshopAssessmentOut)
def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment_or_404(db, assessment_id)
    _workshop, course_id = _get_workshop_and_course(db, assessment.submission.workshop_id)
    is_reviewer = assessment.reviewer_id == current_user.id
    is_author = assessment.submission.author_id == current_user.id
    if not is_reviewer and not is_author:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return _to_out(assessment)


@router.put("/workshop-assessments/{assessment_id}/grades", response_model=WorkshopAssessmentOut)
def save_grades(
    assessment_id: str, data: WorkshopAssessmentGradesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment_or_404(db, assessment_id)
    workshop, course_id = _get_workshop_and_course(db, assessment.submission.workshop_id)
    if assessment.reviewer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette évaluation ne vous a pas été assignée")
    if workshop.phase != WorkshopPhase.assessment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La phase d'évaluation n'est pas ouverte")

    dims_by_id = {d.id: d for d in workshop.dimensions}
    for row in data.grades:
        dimension = dims_by_id.get(row.dimension_id)
        if dimension is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dimension invalide pour cet atelier")

        grade = row.grade
        if workshop.strategy == WorkshopStrategy.comments:
            grade = Decimal("100")  # comportement réel : toujours 100%, voir plan Épic 10
        elif workshop.strategy == WorkshopStrategy.accumulative:
            if grade is None or grade < 0 or (dimension.grade is not None and grade > dimension.grade):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Note hors plage pour la dimension « {dimension.description} »")
        elif workshop.strategy == WorkshopStrategy.numerrors:
            if grade not in (Decimal("0"), Decimal("1")):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Réponse invalide pour la dimension « {dimension.description} »")
        elif workshop.strategy == WorkshopStrategy.rubric:
            valid_grades = {lvl.grade for lvl in dimension.levels}
            if grade not in valid_grades:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Niveau invalide pour la dimension « {dimension.description} »")

        existing = db.query(WorkshopGrade).filter(
            WorkshopGrade.assessment_id == assessment_id, WorkshopGrade.dimension_id == row.dimension_id,
        ).first()
        if existing is None:
            db.add(WorkshopGrade(assessment_id=assessment_id, dimension_id=row.dimension_id, grade=grade, peer_comment=row.peer_comment))
        else:
            existing.grade = grade
            existing.peer_comment = row.peer_comment

    if data.feedback_author is not None:
        assessment.feedback_author = data.feedback_author

    db.commit()
    db.refresh(assessment)
    return _to_out(assessment)


@router.patch("/workshop-assessments/{assessment_id}/feedback-reviewer", response_model=WorkshopAssessmentOut)
def set_feedback_reviewer(
    assessment_id: str, data: WorkshopFeedbackReviewerIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment_or_404(db, assessment_id)
    _workshop, course_id = _get_workshop_and_course(db, assessment.submission.workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(assessment, field, value)
    db.commit()
    db.refresh(assessment)

    notify(db, assessment.reviewer_id, NotificationKind.new_grade,
           title="Retour sur votre évaluation par les pairs",
           link_url=f"/student/workshops/{assessment.submission.workshop_id}")

    return _to_out(assessment)
