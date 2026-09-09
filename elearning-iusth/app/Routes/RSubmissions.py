from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MAssignment import Assignment, Submission, SubmissionStatus
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User
from app.Models.MNotification import NotificationKind
from app.Models.MCompletion import CompletionItemType
from app.Models.MScale import Scale
from app.Schemas.SAssignment import SubmissionGrade, SubmissionOut
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.files import save_upload
from app.Helper.notifications import notify
from app.Helper.completion import mark_complete_if_absent

router = APIRouter(tags=["submissions"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_assignment_and_course(db: Session, assignment_id: str) -> tuple[Assignment, str]:
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devoir introuvable")
    section = db.query(Section).filter(Section.id == assignment.section_id).first()
    return assignment, section.course_id


@router.post("/assignments/{assignment_id}/submissions", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
async def submit_assignment(
    assignment_id: str,
    submitted_text: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assignment, course_id = _get_assignment_and_course(db, assignment_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    if not assignment.allow_late_submissions and assignment.due_date:
        if datetime.now(timezone.utc) > assignment.due_date.replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Date limite dépassée")

    submission = (
        db.query(Submission)
        .filter(Submission.assignment_id == assignment_id, Submission.student_id == current_user.id)
        .first()
    )
    if submission is None:
        submission = Submission(assignment_id=assignment_id, student_id=current_user.id)
        db.add(submission)

    if submitted_text is not None:
        submission.submitted_text = submitted_text
    if file is not None:
        stored_path, _size = save_upload(file, subdir=f"submissions/{assignment_id}/{current_user.id}")
        submission.file_path = stored_path

    submission.status = SubmissionStatus.submitted
    submission.submitted_at = datetime.now(timezone.utc)
    # Une nouvelle soumission après correction rouvre l'évaluation.
    submission.grade = None
    submission.feedback = None
    submission.graded_by = None
    submission.graded_at = None

    db.commit()
    db.refresh(submission)
    return submission


@router.get("/assignments/{assignment_id}/submissions/me", response_model=SubmissionOut)
def get_my_submission(
    assignment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    submission = (
        db.query(Submission)
        .filter(Submission.assignment_id == assignment_id, Submission.student_id == current_user.id)
        .first()
    )
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucune soumission")
    return submission


@router.get("/assignments/{assignment_id}/submissions", response_model=list[SubmissionOut])
def list_submissions(
    assignment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _assignment, course_id = _get_assignment_and_course(db, assignment_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    return db.query(Submission).filter(Submission.assignment_id == assignment_id).all()


@router.patch("/submissions/{submission_id}/grade", response_model=SubmissionOut)
def grade_submission(
    submission_id: str, data: SubmissionGrade,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soumission introuvable")

    assignment, course_id = _get_assignment_and_course(db, submission.assignment_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if assignment.scale_id:
        scale = db.query(Scale).filter(Scale.id == assignment.scale_id).first()
        valid_ranks = {level.rank for level in scale.levels}
        if int(data.grade) != data.grade or int(data.grade) not in valid_ranks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail=f"Ce devoir est noté par échelle — rang attendu parmi {sorted(valid_ranks)}")

    submission.grade = data.grade
    submission.feedback = data.feedback
    submission.status = SubmissionStatus.graded
    submission.graded_by = current_user.id
    submission.graded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(submission)

    mark_complete_if_absent(db, submission.student_id, CompletionItemType.assignment, assignment.id)

    notify(db, submission.student_id, NotificationKind.new_grade,
           title=f"Devoir noté : {assignment.title}", body=f"Note : {submission.grade}",
           link_url=f"/student/assignments/{assignment.id}")

    return submission
