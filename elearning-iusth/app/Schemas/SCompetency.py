from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MCompetency import CompetencyRuleType, CompetencyRuleOutcome, UserCompetencyStatus, PlanStatus, EvidenceAction
from app.Models.MCompletion import CompletionItemType


class CompetencyFrameworkBase(BaseModel):
    name: str
    idnumber: str
    description: str | None = None
    scale_id: str | None = None
    is_visible: bool = True


class CompetencyFrameworkCreate(CompetencyFrameworkBase):
    pass


class CompetencyFrameworkUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    scale_id: str | None = None
    is_visible: bool | None = None


class CompetencyFrameworkOut(CompetencyFrameworkBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class CompetencyBase(BaseModel):
    name: str
    idnumber: str | None = None
    description: str | None = None
    scale_id: str | None = None
    proficient_min_rank: int | None = None
    sort_order: int = 0
    rule_type: CompetencyRuleType = CompetencyRuleType.none
    rule_outcome: CompetencyRuleOutcome = CompetencyRuleOutcome.none
    parent_id: str | None = None


class CompetencyCreate(CompetencyBase):
    pass


class CompetencyUpdate(BaseModel):
    name: str | None = None
    idnumber: str | None = None
    description: str | None = None
    scale_id: str | None = None
    proficient_min_rank: int | None = None
    sort_order: int | None = None
    rule_type: CompetencyRuleType | None = None
    rule_outcome: CompetencyRuleOutcome | None = None


class CompetencyOut(CompetencyBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    framework_id: str


class CourseCompetencyCreate(BaseModel):
    competency_id: str


class CourseCompetencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str
    competency_id: str
    sort_order: int


class ModuleCompetencyCreate(BaseModel):
    competency_id: str


class ModuleCompetencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    item_type: CompletionItemType
    item_id: str
    competency_id: str


class GradeCompetencyIn(BaseModel):
    grade_rank: int
    note: str | None = None


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    action: EvidenceAction
    actor_id: str | None = None
    note: str | None = None
    grade_rank: int | None = None
    created_at: datetime | None = None


class StudentCompetencyStatusOut(BaseModel):
    """État d'une compétence pour UN étudiant précis dans le contexte d'UN
    cours (mélange l'info par-cours et globale — utile pour l'affichage
    professeur/étudiant sans 2 appels)."""
    competency_id: str
    competency_name: str
    course_proficiency: bool | None = None
    course_grade_rank: int | None = None
    global_proficiency: bool | None = None
    global_grade_rank: int | None = None


class MyCompetencyOut(BaseModel):
    competency_id: str
    competency_name: str
    status: UserCompetencyStatus
    proficiency: bool | None = None
    grade_rank: int | None = None
    evidence: list[EvidenceOut] = []


class PlanCreate(BaseModel):
    name: str
    description: str | None = None
    user_id: str | None = None
    competency_ids: list[str] = []


class PlanUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: PlanStatus | None = None
    due_date: datetime | None = None
    reviewer_id: str | None = None


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    name: str
    description: str | None = None
    status: PlanStatus
    due_date: datetime | None = None
    reviewer_id: str | None = None


class PlanCompetencyOut(BaseModel):
    id: str
    competency_id: str
    competency_name: str
    proficiency: bool | None = None
    grade_rank: int | None = None


class PlanDetailOut(PlanOut):
    competencies: list[PlanCompetencyOut] = []
