from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.Models.MLesson import LessonPageType, LessonJumpType, LessonAttemptStatus


class LessonBase(BaseModel):
    title: str
    description: str | None = None
    is_visible: bool = True
    max_attempts_per_question: int | None = None
    time_limit_minutes: int | None = None
    allow_retake: bool = True


class LessonCreate(LessonBase):
    password: str | None = None


class LessonUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_visible: bool | None = None
    password: str | None = None
    max_attempts_per_question: int | None = None
    time_limit_minutes: int | None = None
    allow_retake: bool | None = None


class LessonOut(LessonBase):
    """Vue générique (imbriquée dans le cours, étudiant ET professeur) —
    jamais le mot de passe lui-même, seulement `has_password` (voir plan
    Épic 9 : contrairement à `CourseEnrollmentSettingsOut`, cette leçon est
    imbriquée dans la réponse de cours vue par l'étudiant)."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    course_id: str
    has_password: bool = False


class LessonAnswerCreate(BaseModel):
    answer_text: str | None = None
    is_correct: bool = False
    tolerance: Decimal | None = None
    jump_type: LessonJumpType = LessonJumpType.next_page
    jump_to_page_id: str | None = None
    sort_order: int = 0


class LessonAnswerConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    answer_text: str | None = None
    is_correct: bool
    tolerance: Decimal | None = None
    jump_type: LessonJumpType
    jump_to_page_id: str | None = None
    sort_order: int


class LessonPageCreate(BaseModel):
    page_type: LessonPageType
    title: str
    content: str | None = None
    points: Decimal = Decimal("1")
    sort_order: int = 0
    answers: list[LessonAnswerCreate] = []


class LessonPageUpdate(BaseModel):
    """Remplace intégralement les réponses si fournies (même patron que
    `PATCH /questions/{id}`)."""
    title: str | None = None
    content: str | None = None
    points: Decimal | None = None
    sort_order: int | None = None
    answers: list[LessonAnswerCreate] | None = None


class LessonPageConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    lesson_id: str
    page_type: LessonPageType
    title: str
    content: str | None = None
    points: Decimal
    sort_order: int
    answers: list[LessonAnswerConfigOut] = []


class LessonConfigOut(LessonOut):
    """Vue professeur complète — réponses avec is_correct/jump visibles.
    Jamais renvoyée à un étudiant (voir RLessons.py)."""
    pages: list[LessonPageConfigOut] = []


# --- Tentatives ---

class LessonAttemptStartIn(BaseModel):
    password: str | None = None


class LessonAttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    lesson_id: str
    student_id: str
    status: LessonAttemptStatus
    current_page_id: str | None = None
    started_at: datetime
    deadline_at: datetime | None = None
    completed_at: datetime | None = None
    score: Decimal | None = None
    max_score: Decimal | None = None
    graded_at: datetime | None = None


class LessonAnswerIn(BaseModel):
    answer_id: str | None = None
    answer_text: str | None = None


class LessonAnswerResultOut(BaseModel):
    is_correct: bool | None = None
    points_awarded: Decimal | None = None
    next_page_id: str | None = None
    end_of_lesson: bool = False


class LessonPageAttemptGrade(BaseModel):
    points_awarded: Decimal
    feedback: str | None = None
