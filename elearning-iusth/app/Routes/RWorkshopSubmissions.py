from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MWorkshop import Workshop, WorkshopSubmission, WorkshopPhase
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Models.MCompletion import CompletionItemType
from app.Models.MAccessLog import AccessItemType
from app.Schemas.SWorkshop import WorkshopSubmissionOut, WorkshopSubmissionOverrideIn, WorkshopAssessmentOut
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.files import save_upload
from app.Helper.access_conditions import is_item_accessible
from app.Helper.access_log import log_access
from app.Helper.workshop_grading import (
    submission_grade_percent, submission_final_grade,
    assessment_grade_percent, assessment_final_gradinggrade_percent,
)

router = APIRouter(tags=["workshop-submissions"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_workshop_and_course(db: Session, workshop_id: str) -> tuple[Workshop, str]:
    workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
    if workshop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atelier introuvable")
    section = db.query(Section).filter(Section.id == workshop.section_id).first()
    return workshop, section.course_id


def _get_submission_and_course(db: Session, submission_id: str) -> tuple[WorkshopSubmission, str]:
    submission = db.query(WorkshopSubmission).filter(WorkshopSubmission.id == submission_id).first()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soumission introuvable")
    _workshop, course_id = _get_workshop_and_course(db, submission.workshop_id)
    return submission, course_id


def _to_out(submission: WorkshopSubmission) -> WorkshopSubmissionOut:
    out = WorkshopSubmissionOut.model_validate(submission)
    out.grade_percent = submission_grade_percent(submission)
    out.final_grade = submission_final_grade(submission)
    assessments_out = []
    for a in submission.assessments:
        a_out = WorkshopAssessmentOut.model_validate(a)
        a_out.grade_percent = assessment_grade_percent(a)
        a_out.gradinggrade_percent = assessment_final_gradinggrade_percent(a)
        assessments_out.append(a_out)
    out.assessments = assessments_out
    return out


@router.post("/workshops/{workshop_id}/submissions", response_model=WorkshopSubmissionOut, status_code=status.HTTP_201_CREATED)
async def submit_workshop(
    workshop_id: str,
    title: str = Form(...),
    content: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    accessible, reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.workshop, workshop_id)
    if not accessible:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="; ".join(reasons) or "Accès restreint")

    if workshop.phase != WorkshopPhase.submission:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La phase de soumission n'est pas ouverte")

    submission = (
        db.query(WorkshopSubmission)
        .filter(WorkshopSubmission.workshop_id == workshop_id, WorkshopSubmission.author_id == current_user.id)
        .first()
    )
    is_new = submission is None
    if submission is None:
        submission = WorkshopSubmission(workshop_id=workshop_id, author_id=current_user.id, title=title)
        db.add(submission)

    submission.title = title
    submission.content = content
    if file is not None:
        stored_path, _size = save_upload(file, subdir=f"workshops/{workshop_id}/{current_user.id}")
        submission.file_path = stored_path

    if is_new:
        now = datetime.now(timezone.utc)
        submission.late = bool(workshop.submission_end and now > workshop.submission_end.replace(tzinfo=timezone.utc))

    db.commit()
    db.refresh(submission)
    return _to_out(submission)


@router.get("/workshops/{workshop_id}/submissions/mine", response_model=WorkshopSubmissionOut | None)
def get_my_submission(
    workshop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    submission = (
        db.query(WorkshopSubmission)
        .filter(WorkshopSubmission.workshop_id == workshop_id, WorkshopSubmission.author_id == current_user.id)
        .first()
    )
    return _to_out(submission) if submission is not None else None


@router.get("/workshops/{workshop_id}/submissions", response_model=list[WorkshopSubmissionOut])
def list_submissions(
    workshop_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    workshop, course_id = _get_workshop_and_course(db, workshop_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return [_to_out(s) for s in workshop.submissions]


@router.get("/workshop-submissions/{submission_id}", response_model=WorkshopSubmissionOut)
def get_submission(
    submission_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    submission, course_id = _get_submission_and_course(db, submission_id)
    is_author = submission.author_id == current_user.id
    is_reviewer = any(a.reviewer_id == current_user.id for a in submission.assessments)
    if not is_author and not is_reviewer:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    log_access(db, current_user, course_id, AccessItemType.workshop, submission.workshop_id)
    return _to_out(submission)


@router.patch("/workshop-submissions/{submission_id}/override", response_model=WorkshopSubmissionOut)
def override_submission(
    submission_id: str, data: WorkshopSubmissionOverrideIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    submission, course_id = _get_submission_and_course(db, submission_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(submission, field, value)
    submission.graded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(submission)
    return _to_out(submission)
