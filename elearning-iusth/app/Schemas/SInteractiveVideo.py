from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.Models.MInteractiveVideo import InteractiveVideoSourceType, InteractiveVideoAttemptStatus
from app.Models.MQuestion import QuestionType


class QuestionOptionForStudentOut(BaseModel):
    id: str
    option_text: str
    sort_order: int


class InteractiveVideoBase(BaseModel):
    title: str
    description: str | None = None
    is_visible: bool = True
    source_type: InteractiveVideoSourceType
    video_url: str | None = None


class InteractiveVideoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_visible: bool | None = None
    video_url: str | None = None
    duration_seconds: Decimal | None = None


class InteractiveVideoOut(InteractiveVideoBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    course_id: str
    original_filename: str | None = None
    mime_type: str | None = None
    duration_seconds: Decimal | None = None


class CheckpointCreate(BaseModel):
    timestamp_seconds: Decimal
    question_id: str
    points: Decimal | None = None
    sort_order: int = 0


class CheckpointUpdate(BaseModel):
    timestamp_seconds: Decimal | None = None
    points: Decimal | None = None
    sort_order: int | None = None


class CheckpointOut(BaseModel):
    id: str
    video_id: str
    timestamp_seconds: Decimal
    question_id: str
    points: Decimal
    sort_order: int
    # Vue étudiante sans réponses correctes (même garde que Quiz tant que
    # l'attempt n'est pas terminé) — absents quand non pertinents.
    question_type: QuestionType | None = None
    question_text: str | None = None
    options: list[QuestionOptionForStudentOut] | None = None


class AttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    video_id: str
    student_id: str
    status: InteractiveVideoAttemptStatus
    last_position_seconds: Decimal
    started_at: datetime
    completed_at: datetime | None = None
    score: Decimal | None = None
    max_score: Decimal | None = None


class InteractiveVideoDetailOut(InteractiveVideoOut):
    checkpoints: list[CheckpointOut] = []
    my_attempt: AttemptOut | None = None
    access_restricted: bool = False
    access_reasons: list[str] = []


class PositionUpdate(BaseModel):
    position_seconds: Decimal


class AnswerIn(BaseModel):
    answer_data: dict


class AnswerOut(BaseModel):
    is_correct: bool | None = None
    points_awarded: Decimal | None = None


class EssayGradeIn(BaseModel):
    points_awarded: Decimal
    feedback: str | None = None
