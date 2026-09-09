from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.Models.MQuestion import QuestionType


class QuestionCategoryCreate(BaseModel):
    name: str


class QuestionCategoryUpdate(BaseModel):
    name: str | None = None


class QuestionCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str
    name: str


class QuestionOptionIn(BaseModel):
    option_text: str
    match_text: str | None = None
    is_correct: bool = False
    sort_order: int = 0


class QuestionOptionOut(QuestionOptionIn):
    model_config = ConfigDict(from_attributes=True)
    id: str


class NumericalAcceptedAnswerIn(BaseModel):
    """numerical uniquement — une valeur acceptée avec sa propre tolérance
    (plusieurs valeurs possibles, ex. 3.14±0.01 OU 22/7±0.01)."""
    value: Decimal
    tolerance: Decimal = Decimal("0")


class NumericalAcceptedAnswerOut(NumericalAcceptedAnswerIn):
    model_config = ConfigDict(from_attributes=True)
    id: str


class QuestionCalculatedDatasetIn(BaseModel):
    variable_name: str
    values: list[Decimal]


class QuestionCalculatedDatasetOut(QuestionCalculatedDatasetIn):
    model_config = ConfigDict(from_attributes=True)
    id: str


class QuestionClozePartIn(BaseModel):
    position: int
    sub_type: QuestionType
    correct_answers: dict
    points: Decimal = Decimal("1")


class QuestionClozePartOut(QuestionClozePartIn):
    model_config = ConfigDict(from_attributes=True)
    id: str


class QuestionBase(BaseModel):
    category_id: str | None = None
    question_type: QuestionType
    question_text: str
    default_points: Decimal = Decimal("1")
    is_active: bool = True
    calculated_formula: str | None = None
    calculated_tolerance: Decimal | None = None


class QuestionCreate(QuestionBase):
    options: list[QuestionOptionIn] = []
    accepted_answers: list[str] = []
    numerical_answers: list[NumericalAcceptedAnswerIn] = []
    calculated_datasets: list[QuestionCalculatedDatasetIn] = []
    cloze_parts: list[QuestionClozePartIn] = []


class QuestionUpdate(BaseModel):
    category_id: str | None = None
    question_text: str | None = None
    default_points: Decimal | None = None
    is_active: bool | None = None
    calculated_formula: str | None = None
    calculated_tolerance: Decimal | None = None
    # Remplacement intégral (pas de diff) si fournis — pas de précédent de
    # PATCH imbriqué en Phase 1 (voir plan Phase 2).
    options: list[QuestionOptionIn] | None = None
    accepted_answers: list[str] | None = None
    numerical_answers: list[NumericalAcceptedAnswerIn] | None = None
    calculated_datasets: list[QuestionCalculatedDatasetIn] | None = None
    cloze_parts: list[QuestionClozePartIn] | None = None


class QuestionOut(BaseModel):
    """Construit explicitement dans les routes (pas via model_validate) :
    `accepted_answers` est une liste d'objets ORM côté modèle mais une
    liste de chaînes ici — pas de mapping automatique possible."""

    id: str
    course_id: str
    category_id: str | None = None
    question_type: QuestionType
    question_text: str
    default_points: Decimal
    is_active: bool
    calculated_formula: str | None = None
    calculated_tolerance: Decimal | None = None
    options: list[QuestionOptionOut] = []
    accepted_answers: list[str] = []
    numerical_answers: list[NumericalAcceptedAnswerOut] = []
    calculated_datasets: list[QuestionCalculatedDatasetOut] = []
    cloze_parts: list[QuestionClozePartOut] = []
