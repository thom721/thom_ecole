from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.Models.MQuestion import QuestionType
from app.Models.MQuiz import QuizAttemptStatus


class QuizBase(BaseModel):
    title: str
    description: str | None = None
    time_limit_minutes: int | None = None
    max_attempts: int | None = None
    shuffle_questions: bool = False
    is_visible: bool = True
    opens_at: datetime | None = None
    closes_at: datetime | None = None


class QuizCreate(QuizBase):
    pass


class QuizUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    time_limit_minutes: int | None = None
    max_attempts: int | None = None
    shuffle_questions: bool | None = None
    is_visible: bool | None = None
    opens_at: datetime | None = None
    closes_at: datetime | None = None


class QuizOut(QuizBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    course_id: str


class QuizQuestionCreate(BaseModel):
    question_id: str
    points: Decimal | None = None
    sort_order: int = 0


class QuizQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    quiz_id: str
    question_id: str
    points: Decimal | None = None
    sort_order: int


class QuizDrawRuleCreate(BaseModel):
    category_id: str
    question_type: QuestionType | None = None
    count: int
    points: Decimal | None = None
    sort_order: int = 0


class QuizDrawRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    quiz_id: str
    category_id: str
    question_type: QuestionType | None = None
    count: int
    points: Decimal | None = None
    sort_order: int


class QuizConfigOut(QuizOut):
    """Vue professeur complète — bonnes réponses incluses via QuestionOut
    imbriqué. Jamais renvoyée à un étudiant (voir RQuizzes.py)."""
    quiz_questions: list[dict[str, Any]] = []
    draw_rules: list[QuizDrawRuleOut] = []


# --- Tentatives ---

class QuizAttemptQuestionStudentOut(BaseModel):
    """Question telle que vue par l'étudiant pendant `in_progress` — sans
    is_correct, sans match_text, sans réponses acceptées."""
    question_id: str
    question_type: QuestionType
    question_text: str
    points: Decimal
    sort_order: int
    options: list[dict[str, Any]] = []  # [{id, option_text, sort_order}]


class QuizResponseAnswerIn(BaseModel):
    answer_data: dict[str, Any]


class QuizResponseGrade(BaseModel):
    points_awarded: Decimal
    feedback: str | None = None


class QuizResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    question_id: str
    sort_order: int
    points: Decimal
    answer_data: dict[str, Any] | None = None
    is_correct: bool | None = None
    points_awarded: Decimal | None = None
    feedback: str | None = None
    answered_at: datetime | None = None


class QuizAttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    quiz_id: str
    student_id: str
    status: QuizAttemptStatus
    started_at: datetime
    deadline_at: datetime | None = None
    submitted_at: datetime | None = None
    score: Decimal | None = None
    max_score: Decimal | None = None
    graded_at: datetime | None = None


class QuizAttemptSummaryOut(QuizAttemptOut):
    """Utilisé par la file de correction professeur (liste, pas de détail
    des réponses)."""
    pass
