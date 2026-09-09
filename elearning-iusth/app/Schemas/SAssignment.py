from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.Models.MAssignment import SubmissionType, SubmissionStatus


class AssignmentBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    allow_late_submissions: bool = True
    submission_type: SubmissionType = SubmissionType.both
    max_points: Decimal = Decimal("100")
    is_visible: bool = True
    # Si renseigné, la notation utilise les niveaux de cette échelle au
    # lieu de max_points en points libres (voir plan Épic 8).
    scale_id: str | None = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    allow_late_submissions: bool | None = None
    submission_type: SubmissionType | None = None
    max_points: Decimal | None = None
    is_visible: bool | None = None
    scale_id: str | None = None


class AssignmentOut(AssignmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str


class SubmissionCreate(BaseModel):
    submitted_text: str | None = None


class SubmissionGrade(BaseModel):
    grade: Decimal
    feedback: str | None = None


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assignment_id: str
    student_id: str
    submitted_text: str | None = None
    file_path: str | None = None
    status: SubmissionStatus
    submitted_at: datetime | None = None
    grade: Decimal | None = None
    feedback: str | None = None
    graded_by: str | None = None
    graded_at: datetime | None = None
