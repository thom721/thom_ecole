from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.Models.MQuestion import QuestionType
from app.Models.MAssignment import SubmissionType
from app.Models.MGroup import GroupMode
from app.Models.MChoice import ChoiceResultsDisplay
from app.Models.MWiki import WikiMode
from app.Models.MLesson import LessonPageType, LessonJumpType, LessonAttemptStatus
from app.Models.MWorkshop import WorkshopStrategy
from app.Models.MQuiz import QuizAttemptStatus
from app.Models.MAssignment import SubmissionStatus
from app.Models.MCompletion import CompletionItemType

EXPORT_VERSION = 2


# --- Éléments imbriqués ---

class ExportResourceFileMeta(BaseModel):
    original_filename: str
    mime_type: str | None = None
    size_bytes: int | None = None


class ExportResource(BaseModel):
    resource_type: str
    title: str
    description: str | None = None
    external_url: str | None = None
    page_content: str | None = None
    sort_order: int = 0
    is_visible: bool = True
    files_meta: list[ExportResourceFileMeta] = []


class ExportQuizQuestion(BaseModel):
    question_ref: str
    points: Decimal | None = None
    sort_order: int = 0


class ExportDrawRule(BaseModel):
    category_ref: str
    question_type: QuestionType | None = None
    count: int
    points: Decimal | None = None
    sort_order: int = 0


class ExportAssignment(BaseModel):
    local_id: str
    title: str
    description: str | None = None
    due_date: datetime | None = None
    allow_late_submissions: bool = True
    submission_type: SubmissionType = SubmissionType.both
    max_points: Decimal = Decimal("100")
    is_visible: bool = True


class ExportQuiz(BaseModel):
    local_id: str
    title: str
    description: str | None = None
    time_limit_minutes: int | None = None
    max_attempts: int | None = None
    shuffle_questions: bool = False
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    is_visible: bool = True
    quiz_questions: list[ExportQuizQuestion] = []
    draw_rules: list[ExportDrawRule] = []


class ExportForum(BaseModel):
    title: str
    description: str | None = None
    is_visible: bool = True
    group_mode: GroupMode = GroupMode.no_groups


class ExportChoiceOption(BaseModel):
    option_text: str
    max_answers: int | None = None
    sort_order: int = 0


class ExportChoice(BaseModel):
    title: str
    description: str | None = None
    is_visible: bool = True
    allow_multiple: bool = False
    allow_update: bool = False
    limit_answers: bool = False
    results_display: ChoiceResultsDisplay = ChoiceResultsDisplay.never
    anonymous_results: bool = True
    show_unanswered: bool = False
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    group_mode: GroupMode = GroupMode.no_groups
    options: list[ExportChoiceOption] = []


class ExportGlossary(BaseModel):
    title: str
    description: str | None = None
    is_visible: bool = True
    is_main: bool = False
    allow_student_entries: bool = False
    require_approval: bool = False
    allow_duplicates: bool = False


class ExportWiki(BaseModel):
    title: str
    description: str | None = None
    is_visible: bool = True
    mode: WikiMode = WikiMode.collaborative
    first_page_title: str = "Accueil"


class ExportLessonAnswer(BaseModel):
    answer_text: str | None = None
    is_correct: bool = False
    tolerance: Decimal | None = None
    jump_type: LessonJumpType = LessonJumpType.next_page
    jump_to_page_ref: str | None = None
    sort_order: int = 0


class ExportLessonPage(BaseModel):
    local_id: str
    page_type: LessonPageType
    title: str
    content: str | None = None
    points: Decimal = Decimal("1")
    sort_order: int = 0
    answers: list[ExportLessonAnswer] = []


class ExportLesson(BaseModel):
    local_id: str
    title: str
    description: str | None = None
    is_visible: bool = True
    password: str | None = None
    max_attempts_per_question: int | None = None
    time_limit_minutes: int | None = None
    allow_retake: bool = True
    pages: list[ExportLessonPage] = []


class ExportWorkshopRubricLevel(BaseModel):
    grade: Decimal
    definition: str
    sort_order: int = 0


class ExportWorkshopDimension(BaseModel):
    local_id: str
    sort_order: int = 0
    description: str
    grade: Decimal | None = None
    weight: int = 1
    label_no: str | None = None
    label_yes: str | None = None
    levels: list[ExportWorkshopRubricLevel] = []


class ExportWorkshopNumerrorsMapRow(BaseModel):
    error_count: int
    grade_percent: Decimal


class ExportWorkshop(BaseModel):
    local_id: str
    title: str
    description: str | None = None
    is_visible: bool = True
    grade: Decimal = Decimal("80")
    gradinggrade: Decimal = Decimal("20")
    strategy: WorkshopStrategy = WorkshopStrategy.accumulative
    use_peer_assessment: bool = True
    use_self_assessment: bool = False
    comparison: int = 5
    dimensions: list[ExportWorkshopDimension] = []
    numerrors_map: list[ExportWorkshopNumerrorsMapRow] = []


class ExportSection(BaseModel):
    local_id: str
    title: str | None = None
    summary: str | None = None
    sort_order: int = 0
    is_visible: bool = True
    resources: list[ExportResource] = []
    assignments: list[ExportAssignment] = []
    quizzes: list[ExportQuiz] = []
    forums: list[ExportForum] = []
    choices: list[ExportChoice] = []
    glossaries: list[ExportGlossary] = []
    wikis: list[ExportWiki] = []
    lessons: list[ExportLesson] = []
    workshops: list[ExportWorkshop] = []


class ExportQuestionOption(BaseModel):
    option_text: str
    match_text: str | None = None
    is_correct: bool = False
    sort_order: int = 0


class ExportQuestionCategory(BaseModel):
    local_id: str
    name: str


class ExportQuestion(BaseModel):
    local_id: str
    category_ref: str | None = None
    question_type: QuestionType
    question_text: str
    default_points: Decimal = Decimal("1")
    is_active: bool = True
    options: list[ExportQuestionOption] = []
    accepted_answers: list[str] = []


class ExportGradeCategory(BaseModel):
    local_id: str
    name: str
    weight_percent: Decimal
    sort_order: int = 0


class ExportGradeItemManual(BaseModel):
    local_id: str
    title: str
    max_points: Decimal
    grade_category_ref: str | None = None
    sort_order: int = 0


class ExportCourse(BaseModel):
    short_name: str
    full_name: str
    summary: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_visible: bool = True


# --- Données étudiantes (optionnelles, voir plan Épic 16) ---

class ExportSubmission(BaseModel):
    assignment_ref: str
    student_email: str
    submitted_text: str | None = None
    has_file: bool = False
    status: SubmissionStatus
    grade: Decimal | None = None
    feedback: str | None = None
    submitted_at: datetime | None = None
    graded_at: datetime | None = None


class ExportQuizResponse(BaseModel):
    question_ref: str
    points: Decimal
    answer_data: dict | None = None
    is_correct: bool | None = None
    points_awarded: Decimal | None = None
    feedback: str | None = None


class ExportQuizAttempt(BaseModel):
    quiz_ref: str
    student_email: str
    status: QuizAttemptStatus
    score: Decimal | None = None
    max_score: Decimal | None = None
    started_at: datetime | None = None
    submitted_at: datetime | None = None
    graded_at: datetime | None = None
    responses: list[ExportQuizResponse] = []


class ExportManualGradeValue(BaseModel):
    grade_item_ref: str
    student_email: str
    points: Decimal | None = None
    feedback: str | None = None


class ExportActivityCompletion(BaseModel):
    item_type: CompletionItemType  # limité à assignment/quiz/workshop dans ce périmètre
    item_ref: str
    student_email: str
    completed_at: datetime | None = None


class ExportWorkshopGrade(BaseModel):
    dimension_ref: str
    grade: Decimal | None = None
    peer_comment: str | None = None


class ExportWorkshopAssessment(BaseModel):
    reviewer_email: str
    weight: int = 1
    gradinggrade_override: Decimal | None = None
    feedback_author: str | None = None
    feedback_reviewer: str | None = None
    grades: list[ExportWorkshopGrade] = []


class ExportWorkshopSubmission(BaseModel):
    workshop_ref: str
    author_email: str
    title: str
    has_file: bool = False
    content: str | None = None
    grade_override: Decimal | None = None
    feedback_author: str | None = None
    published: bool = False
    late: bool = False
    assessments: list[ExportWorkshopAssessment] = []


class StudentData(BaseModel):
    submissions: list[ExportSubmission] = []
    quiz_attempts: list[ExportQuizAttempt] = []
    manual_grades: list[ExportManualGradeValue] = []
    completions: list[ExportActivityCompletion] = []
    workshop_submissions: list[ExportWorkshopSubmission] = []


class CourseExportDocument(BaseModel):
    export_version: int = EXPORT_VERSION
    exported_at: datetime
    course: ExportCourse
    sections: list[ExportSection] = []
    question_categories: list[ExportQuestionCategory] = []
    questions: list[ExportQuestion] = []
    grade_categories: list[ExportGradeCategory] = []
    grade_items_manual: list[ExportGradeItemManual] = []
    student_data: StudentData | None = None


class CourseImportRequest(BaseModel):
    short_name: str | None = None
    full_name: str | None = None
    target_course_id: str | None = None
    export: CourseExportDocument


class CourseImportResult(BaseModel):
    course: dict  # CourseOut sérialisé (évite un import circulaire avec SCourse)
    warnings: list[str] = []
