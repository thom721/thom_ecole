from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MQuestion import Question, QuestionType
from app.Models.MGrade import GradeItem, GradeItemKind
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Models.MCompletion import CompletionItemType
from app.Models.MInteractiveVideo import (
    InteractiveVideo, InteractiveVideoCheckpoint, InteractiveVideoAttempt, InteractiveVideoResponse,
    InteractiveVideoSourceType, InteractiveVideoAttemptStatus,
)
from app.Schemas.SInteractiveVideo import (
    InteractiveVideoUpdate, InteractiveVideoOut, InteractiveVideoDetailOut,
    CheckpointCreate, CheckpointUpdate, CheckpointOut, QuestionOptionForStudentOut,
    AttemptOut, PositionUpdate, AnswerIn, AnswerOut, EssayGradeIn,
)
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.files import save_upload, resolve_download
from app.Helper.access_conditions import is_item_accessible
from app.Helper.completion import mark_complete_if_absent
from app.Helper.question_grading import auto_grade

router = APIRouter(tags=["interactive-videos"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_video_and_course(db: Session, video_id: str) -> tuple[InteractiveVideo, str]:
    video = db.query(InteractiveVideo).filter(InteractiveVideo.id == video_id).first()
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vidéo interactive introuvable")
    section = db.query(Section).filter(Section.id == video.section_id).first()
    return video, section.course_id


def _is_teaching(db: Session, current_user: User, course_id: str) -> bool:
    if current_user.system_role == SystemRole.admin:
        return True
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    return enrollment is not None and enrollment.role_in_course in _TEACHING_ROLES


def _video_max_points(video: InteractiveVideo) -> Decimal:
    return sum((cp.points if cp.points is not None else cp.question.default_points) for cp in video.checkpoints) or Decimal("0")


@router.post("/sections/{section_id}/interactive-videos", response_model=InteractiveVideoOut, status_code=status.HTTP_201_CREATED)
async def create_interactive_video(
    section_id: str,
    title: str = Form(...),
    description: str | None = Form(None),
    source_type: InteractiveVideoSourceType = Form(...),
    video_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    if source_type == InteractiveVideoSourceType.url and not video_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="video_url requis pour une source externe")
    if source_type == InteractiveVideoSourceType.file and file is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="fichier requis pour une source uploadée")

    video = InteractiveVideo(section_id=section_id, title=title, description=description, source_type=source_type, video_url=video_url)
    db.add(video)
    db.flush()

    if file is not None:
        stored_path, size = save_upload(file, subdir=f"interactive-videos/{video.id}")
        video.stored_path = stored_path
        video.original_filename = file.filename or "media"
        video.mime_type = file.content_type
        video.size_bytes = size

    db.add(GradeItem(course_id=section.course_id, interactive_video_id=video.id, kind=GradeItemKind.interactive_video))

    db.commit()
    db.refresh(video)
    return video


@router.get("/interactive-videos/{video_id}", response_model=InteractiveVideoDetailOut)
def get_interactive_video(
    video_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    video, course_id = _get_video_and_course(db, video_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    is_teaching = _is_teaching(db, current_user, course_id)
    accessible, reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.interactive_video, video_id)

    checkpoints = [
        CheckpointOut(
            id=cp.id, video_id=cp.video_id, timestamp_seconds=cp.timestamp_seconds,
            question_id=cp.question_id, points=(cp.points if cp.points is not None else cp.question.default_points),
            sort_order=cp.sort_order, question_type=cp.question.question_type, question_text=cp.question.question_text,
            options=[QuestionOptionForStudentOut(id=o.id, option_text=o.option_text, sort_order=o.sort_order) for o in cp.question.options],
        )
        for cp in sorted(video.checkpoints, key=lambda c: c.timestamp_seconds)
    ] if accessible else []

    my_attempt = None
    if not is_teaching:
        attempt = (
            db.query(InteractiveVideoAttempt)
            .filter(InteractiveVideoAttempt.video_id == video_id, InteractiveVideoAttempt.student_id == current_user.id)
            .first()
        )
        if attempt:
            my_attempt = AttemptOut.model_validate(attempt)

    return InteractiveVideoDetailOut(
        id=video.id, section_id=video.section_id, course_id=course_id, title=video.title, description=video.description,
        is_visible=video.is_visible, source_type=video.source_type, video_url=video.video_url,
        original_filename=video.original_filename, mime_type=video.mime_type, duration_seconds=video.duration_seconds,
        checkpoints=checkpoints, my_attempt=my_attempt,
        access_restricted=not accessible, access_reasons=reasons,
    )


@router.patch("/interactive-videos/{video_id}", response_model=InteractiveVideoOut)
def update_interactive_video(
    video_id: str, data: InteractiveVideoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    video, course_id = _get_video_and_course(db, video_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(video, field, value)
    db.commit()
    db.refresh(video)
    return video


@router.delete("/interactive-videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interactive_video(
    video_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    video, course_id = _get_video_and_course(db, video_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if db.query(InteractiveVideoAttempt).filter(InteractiveVideoAttempt.video_id == video_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Cette vidéo a déjà des tentatives — suppression bloquée pour préserver l'historique des notes")

    db.delete(video)
    db.commit()


@router.get("/interactive-videos/{video_id}/media")
def get_media(
    video_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    video, course_id = _get_video_and_course(db, video_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    if video.source_type != InteractiveVideoSourceType.file or not video.stored_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette vidéo n'a pas de fichier hébergé (source externe)")
    return resolve_download(video.stored_path, video.original_filename or "media", video.mime_type)


@router.post("/interactive-videos/{video_id}/checkpoints", response_model=CheckpointOut, status_code=status.HTTP_201_CREATED)
def create_checkpoint(
    video_id: str, data: CheckpointCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    video, course_id = _get_video_and_course(db, video_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    question = db.query(Question).filter(Question.id == data.question_id, Question.course_id == course_id).first()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question introuvable dans ce cours")
    if question.question_type == QuestionType.calculated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Le type de question 'calculated' n'est pas pris en charge pour les checkpoints vidéo")

    checkpoint = InteractiveVideoCheckpoint(video_id=video_id, timestamp_seconds=data.timestamp_seconds,
                                             question_id=data.question_id, points=data.points, sort_order=data.sort_order)
    db.add(checkpoint)
    db.commit()
    db.refresh(checkpoint)
    return CheckpointOut(id=checkpoint.id, video_id=checkpoint.video_id, timestamp_seconds=checkpoint.timestamp_seconds,
                          question_id=checkpoint.question_id,
                          points=(checkpoint.points if checkpoint.points is not None else question.default_points),
                          sort_order=checkpoint.sort_order)


def _get_checkpoint_and_course(db: Session, checkpoint_id: str) -> tuple[InteractiveVideoCheckpoint, str]:
    checkpoint = db.query(InteractiveVideoCheckpoint).filter(InteractiveVideoCheckpoint.id == checkpoint_id).first()
    if checkpoint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkpoint introuvable")
    _video, course_id = _get_video_and_course(db, checkpoint.video_id)
    return checkpoint, course_id


@router.patch("/interactive-video-checkpoints/{checkpoint_id}", response_model=CheckpointOut)
def update_checkpoint(
    checkpoint_id: str, data: CheckpointUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    checkpoint, course_id = _get_checkpoint_and_course(db, checkpoint_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(checkpoint, field, value)
    db.commit()
    db.refresh(checkpoint)
    return CheckpointOut(id=checkpoint.id, video_id=checkpoint.video_id, timestamp_seconds=checkpoint.timestamp_seconds,
                          question_id=checkpoint.question_id,
                          points=(checkpoint.points if checkpoint.points is not None else checkpoint.question.default_points),
                          sort_order=checkpoint.sort_order)


@router.delete("/interactive-video-checkpoints/{checkpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checkpoint(
    checkpoint_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    checkpoint, course_id = _get_checkpoint_and_course(db, checkpoint_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if db.query(InteractiveVideoResponse).filter(InteractiveVideoResponse.checkpoint_id == checkpoint_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce checkpoint a déjà des réponses — suppression bloquée")

    db.delete(checkpoint)
    db.commit()


@router.post("/interactive-videos/{video_id}/attempts", response_model=AttemptOut, status_code=status.HTTP_201_CREATED)
def start_attempt(
    video_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    video, course_id = _get_video_and_course(db, video_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None and current_user.system_role != SystemRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    existing = (
        db.query(InteractiveVideoAttempt)
        .filter(InteractiveVideoAttempt.video_id == video_id, InteractiveVideoAttempt.student_id == current_user.id)
        .first()
    )
    if existing is not None:
        return existing

    accessible, reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.interactive_video, video_id)
    if not accessible:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="; ".join(reasons))

    attempt = InteractiveVideoAttempt(video_id=video_id, student_id=current_user.id)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def _get_attempt_or_404(db: Session, attempt_id: str) -> InteractiveVideoAttempt:
    attempt = db.query(InteractiveVideoAttempt).filter(InteractiveVideoAttempt.id == attempt_id).first()
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tentative introuvable")
    return attempt


@router.patch("/interactive-video-attempts/{attempt_id}/position", status_code=status.HTTP_204_NO_CONTENT)
def update_position(
    attempt_id: str, data: PositionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette tentative ne vous appartient pas")
    attempt.last_position_seconds = data.position_seconds
    db.commit()


@router.post("/interactive-video-attempts/{attempt_id}/checkpoints/{checkpoint_id}/answer", response_model=AnswerOut)
def answer_checkpoint(
    attempt_id: str, checkpoint_id: str, data: AnswerIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette tentative ne vous appartient pas")
    if attempt.status != InteractiveVideoAttemptStatus.in_progress:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette tentative n'est plus modifiable")

    checkpoint = db.query(InteractiveVideoCheckpoint).filter(InteractiveVideoCheckpoint.id == checkpoint_id, InteractiveVideoCheckpoint.video_id == attempt.video_id).first()
    if checkpoint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checkpoint hors de cette vidéo")

    existing = (
        db.query(InteractiveVideoResponse)
        .filter(InteractiveVideoResponse.attempt_id == attempt_id, InteractiveVideoResponse.checkpoint_id == checkpoint_id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce checkpoint a déjà reçu une réponse")

    points = checkpoint.points if checkpoint.points is not None else checkpoint.question.default_points
    response = InteractiveVideoResponse(attempt_id=attempt_id, checkpoint_id=checkpoint_id, points=points, answer_data=data.answer_data)
    auto_grade(checkpoint.question, response)
    db.add(response)
    db.commit()
    db.refresh(response)
    return AnswerOut(is_correct=response.is_correct, points_awarded=response.points_awarded)


@router.post("/interactive-video-attempts/{attempt_id}/finish", response_model=AttemptOut)
def finish_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cette tentative ne vous appartient pas")
    if attempt.status != InteractiveVideoAttemptStatus.in_progress:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette tentative est déjà terminée")

    video = db.query(InteractiveVideo).filter(InteractiveVideo.id == attempt.video_id).first()
    answered_checkpoint_ids = {r.checkpoint_id for r in attempt.responses}
    all_checkpoint_ids = {cp.id for cp in video.checkpoints}
    if not all_checkpoint_ids.issubset(answered_checkpoint_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tous les checkpoints doivent être répondus avant de terminer")

    has_pending_essay = any(r.points_awarded is None for r in attempt.responses)
    attempt.max_score = _video_max_points(video)
    attempt.score = sum((r.points_awarded or 0) for r in attempt.responses)
    if has_pending_essay:
        attempt.status = InteractiveVideoAttemptStatus.pending_manual_grading
    else:
        attempt.status = InteractiveVideoAttemptStatus.completed
        attempt.completed_at = datetime.now(timezone.utc)
        db.commit()
        mark_complete_if_absent(db, attempt.student_id, CompletionItemType.interactive_video, video.id)
        db.refresh(attempt)
        return attempt

    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/interactive-videos/{video_id}/essay-grading")
def essay_grading_queue(
    video_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    video, course_id = _get_video_and_course(db, video_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    responses = (
        db.query(InteractiveVideoResponse)
        .join(InteractiveVideoAttempt, InteractiveVideoAttempt.id == InteractiveVideoResponse.attempt_id)
        .filter(InteractiveVideoAttempt.video_id == video_id, InteractiveVideoResponse.points_awarded.is_(None))
        .all()
    )
    return [
        {
            "response_id": r.id, "attempt_id": r.attempt_id, "student_id": r.attempt.student_id,
            "checkpoint_id": r.checkpoint_id, "question_text": r.checkpoint.question.question_text,
            "answer_text": (r.answer_data or {}).get("text"), "max_points": r.points,
        }
        for r in responses
    ]


@router.patch("/interactive-video-responses/{response_id}/grade", response_model=AnswerOut)
def grade_essay_response(
    response_id: str, data: EssayGradeIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    response = db.query(InteractiveVideoResponse).filter(InteractiveVideoResponse.id == response_id).first()
    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réponse introuvable")
    attempt = db.query(InteractiveVideoAttempt).filter(InteractiveVideoAttempt.id == response.attempt_id).first()
    _video, course_id = _get_video_and_course(db, attempt.video_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    response.points_awarded = data.points_awarded
    response.is_correct = data.points_awarded > 0
    response.feedback = data.feedback
    response.graded_by = current_user.id
    response.graded_at = datetime.now(timezone.utc)
    db.commit()

    remaining_pending = any(r.points_awarded is None for r in attempt.responses)
    if not remaining_pending and attempt.status == InteractiveVideoAttemptStatus.pending_manual_grading:
        attempt.score = sum((r.points_awarded or 0) for r in attempt.responses)
        attempt.status = InteractiveVideoAttemptStatus.completed
        attempt.completed_at = datetime.now(timezone.utc)
        attempt.graded_at = datetime.now(timezone.utc)
        db.commit()
        mark_complete_if_absent(db, attempt.student_id, CompletionItemType.interactive_video, attempt.video_id)

    db.refresh(response)
    return AnswerOut(is_correct=response.is_correct, points_awarded=response.points_awarded)
