import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MAssignment import Assignment, Submission, SubmissionStatus
from app.Models.MEnrollment import CourseRole
from app.Models.MGroup import Group, GroupMember
from app.Models.MUser import User
from app.Models.MNotification import NotificationKind
from app.Models.MCompletion import CompletionItemType
from app.Models.MScale import Scale
from app.Schemas.SAssignment import SubmissionGrade, SubmissionOut
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.files import save_upload, resolve_download
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


def _display_filename(file_path: str) -> str:
    """save_upload() (Helper/files.py) stocke sous <uuid>_<nom original> —
    retire le préfixe uuid pour retrouver un nom présentable."""
    basename = os.path.basename(file_path)
    return basename.split("_", 1)[1] if "_" in basename else basename


@router.get("/assignments/{assignment_id}/submissions", response_model=list[SubmissionOut])
def list_submissions(
    assignment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _assignment, course_id = _get_assignment_and_course(db, assignment_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    users_by_id = {
        u.id: u
        for u in db.query(User).filter(User.id.in_([s.student_id for s in submissions])).all()
    } if submissions else {}
    return [
        SubmissionOut.model_validate(s).model_copy(update={
            "student_name": f"{users_by_id[s.student_id].first_name} {users_by_id[s.student_id].last_name}" if s.student_id in users_by_id else None,
            "file_name": _display_filename(s.file_path) if s.file_path else None,
            "file_download_url": f"/submissions/{s.id}/download" if s.file_path else None,
        })
        for s in submissions
    ]


@router.get("/submissions/{submission_id}/download")
def download_submission(
    submission_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Sert le fichier joint d'une soumission — jusqu'ici aucune route ne
    l'exposait, le chemin serveur brut (Submission.file_path) était juste
    affiché en texte côté professeur, jamais réellement téléchargeable."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if submission is None or not submission.file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable")

    assignment, course_id = _get_assignment_and_course(db, submission.assignment_id)
    is_owner = current_user.id == submission.student_id
    if not is_owner:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    return resolve_download(submission.file_path, _display_filename(submission.file_path), None)


def _validate_and_apply_grade(db: Session, submission: Submission, assignment: Assignment,
                               data: SubmissionGrade, grader_id: str) -> None:
    if assignment.scale_id:
        scale = db.query(Scale).filter(Scale.id == assignment.scale_id).first()
        valid_ranks = {level.rank for level in scale.levels}
        if int(data.grade) != data.grade or int(data.grade) not in valid_ranks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail=f"Ce devoir est noté par échelle — rang attendu parmi {sorted(valid_ranks)}")

    submission.grade = data.grade
    submission.feedback = data.feedback
    submission.status = SubmissionStatus.graded
    submission.graded_by = grader_id
    submission.graded_at = datetime.now(timezone.utc)


def _notify_graded(db: Session, submission: Submission, assignment: Assignment) -> None:
    mark_complete_if_absent(db, submission.student_id, CompletionItemType.assignment, assignment.id)
    notify(db, submission.student_id, NotificationKind.new_grade,
           title=f"Devoir noté : {assignment.title}", body=f"Note : {submission.grade}",
           link_url=f"/student/assignments/{assignment.id}")


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

    _validate_and_apply_grade(db, submission, assignment, data, current_user.id)

    db.commit()
    db.refresh(submission)
    _notify_graded(db, submission, assignment)

    return submission


@router.patch("/assignments/{assignment_id}/groups/{group_id}/grade", response_model=list[SubmissionOut])
def grade_group(
    assignment_id: str, group_id: str, data: SubmissionGrade,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Note un devoir de groupe en une fois (voir plan Épic 24) : une seule
    note/feedback saisie par le professeur, recopiée sur une Submission par
    membre du groupe — le calcul du carnet de notes (_build_report,
    RGrades.py) continue de lire des Submission par student_id, donc rien
    à changer côté agrégation."""
    assignment, course_id = _get_assignment_and_course(db, assignment_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if not assignment.group_mode:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Ce devoir n'est pas configuré en mode groupe")

    group = db.query(Group).filter(Group.id == group_id, Group.course_id == course_id).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable pour ce cours")

    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    if not members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce groupe n'a aucun membre")

    submissions = []
    for member in members:
        submission = (
            db.query(Submission)
            .filter(Submission.assignment_id == assignment_id, Submission.student_id == member.user_id)
            .first()
        )
        if submission is None:
            submission = Submission(assignment_id=assignment_id, student_id=member.user_id)
            db.add(submission)
        submission.group_id = group_id
        _validate_and_apply_grade(db, submission, assignment, data, current_user.id)
        submissions.append(submission)

    db.commit()
    for submission in submissions:
        db.refresh(submission)
        _notify_graded(db, submission, assignment)

    return submissions
