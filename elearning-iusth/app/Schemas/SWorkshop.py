from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.Models.MWorkshop import WorkshopPhase, WorkshopStrategy


class WorkshopBase(BaseModel):
    title: str
    description: str | None = None
    is_visible: bool = True
    grade: Decimal = Decimal("80")
    gradinggrade: Decimal = Decimal("20")
    strategy: WorkshopStrategy = WorkshopStrategy.accumulative
    use_peer_assessment: bool = True
    use_self_assessment: bool = False
    submission_start: datetime | None = None
    submission_end: datetime | None = None
    assessment_start: datetime | None = None
    assessment_end: datetime | None = None
    comparison: int = 5
    conclusion: str | None = None


class WorkshopCreate(WorkshopBase):
    pass


class WorkshopUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_visible: bool | None = None
    grade: Decimal | None = None
    gradinggrade: Decimal | None = None
    use_peer_assessment: bool | None = None
    use_self_assessment: bool | None = None
    submission_start: datetime | None = None
    submission_end: datetime | None = None
    assessment_start: datetime | None = None
    assessment_end: datetime | None = None
    comparison: int | None = None
    conclusion: str | None = None


class WorkshopPhaseIn(BaseModel):
    phase: WorkshopPhase


class WorkshopOut(WorkshopBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    course_id: str
    phase: WorkshopPhase


class WorkshopRubricLevelIn(BaseModel):
    grade: Decimal
    definition: str
    sort_order: int = 0


class WorkshopRubricLevelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    grade: Decimal
    definition: str
    sort_order: int


class WorkshopDimensionIn(BaseModel):
    description: str
    sort_order: int = 0
    grade: Decimal | None = None  # accumulative
    weight: int = 1  # accumulative/numerrors
    label_no: str | None = None  # numerrors
    label_yes: str | None = None  # numerrors
    levels: list[WorkshopRubricLevelIn] = []  # rubric


class WorkshopDimensionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workshop_id: str
    sort_order: int
    description: str
    grade: Decimal | None = None
    weight: int
    label_no: str | None = None
    label_yes: str | None = None
    levels: list[WorkshopRubricLevelOut] = []


class WorkshopDimensionsUpdate(BaseModel):
    dimensions: list[WorkshopDimensionIn]


class WorkshopNumerrorsMapRow(BaseModel):
    error_count: int
    grade_percent: Decimal


class WorkshopNumerrorsMapUpdate(BaseModel):
    rows: list[WorkshopNumerrorsMapRow]


class WorkshopSubmissionOverrideIn(BaseModel):
    grade_override: Decimal | None = None
    feedback_author: str | None = None
    published: bool | None = None


class WorkshopSubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workshop_id: str
    author_id: str
    title: str
    content: str | None = None
    file_path: str | None = None
    grade_override: Decimal | None = None
    feedback_author: str | None = None
    graded_at: datetime | None = None
    published: bool
    late: bool
    created_at: datetime | None = None
    final_grade: Decimal | None = None
    grade_percent: Decimal | None = None
    assessments: list["WorkshopAssessmentOut"] = []


class WorkshopGradeIn(BaseModel):
    dimension_id: str
    grade: Decimal | None = None
    peer_comment: str | None = None


class WorkshopAssessmentGradesUpdate(BaseModel):
    grades: list[WorkshopGradeIn]
    feedback_author: str | None = None


class WorkshopGradeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    dimension_id: str
    grade: Decimal | None = None
    peer_comment: str | None = None


class WorkshopAssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    submission_id: str
    reviewer_id: str
    weight: int
    gradinggrade_override: Decimal | None = None
    feedback_author: str | None = None
    feedback_reviewer: str | None = None
    grades: list[WorkshopGradeOut] = []
    grade_percent: Decimal | None = None
    gradinggrade_percent: Decimal | None = None


class WorkshopAllocateManualIn(BaseModel):
    submission_id: str
    reviewer_id: str
    weight: int = 1


class WorkshopAllocateRandomIn(BaseModel):
    reviews_per_submission: int = 2


class WorkshopFeedbackReviewerIn(BaseModel):
    feedback_reviewer: str | None = None
    gradinggrade_override: Decimal | None = None


WorkshopSubmissionOut.model_rebuild()
