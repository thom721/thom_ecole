from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MChoice import ChoiceResultsDisplay
from app.Models.MGroup import GroupMode


class ChoiceOptionIn(BaseModel):
    option_text: str
    max_answers: int | None = None
    sort_order: int = 0


class ChoiceOptionOut(ChoiceOptionIn):
    model_config = ConfigDict(from_attributes=True)
    id: str


class ChoiceBase(BaseModel):
    title: str
    description: str | None = None
    allow_multiple: bool = False
    allow_update: bool = False
    limit_answers: bool = False
    results_display: ChoiceResultsDisplay = ChoiceResultsDisplay.never
    anonymous_results: bool = True
    show_unanswered: bool = False
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    group_mode: GroupMode = GroupMode.no_groups
    grouping_id: str | None = None


class ChoiceCreate(ChoiceBase):
    options: list[ChoiceOptionIn] = []


class ChoiceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_visible: bool | None = None
    allow_multiple: bool | None = None
    allow_update: bool | None = None
    limit_answers: bool | None = None
    results_display: ChoiceResultsDisplay | None = None
    anonymous_results: bool | None = None
    show_unanswered: bool | None = None
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    group_mode: GroupMode | None = None
    grouping_id: str | None = None
    options: list[ChoiceOptionIn] | None = None


class ChoiceOut(ChoiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    is_visible: bool


class ChoiceOptionResultOut(BaseModel):
    """Construit à la main dans la route : vote_count/respondents ne sont
    pas des colonnes du modèle, et leur visibilité dépend du viewer."""
    id: str
    option_text: str
    max_answers: int | None = None
    sort_order: int
    vote_count: int | None = None  # null si résultats non visibles pour ce viewer
    respondents: list[str] | None = None  # noms, seulement si non anonyme ET visible


class ChoiceDetailOut(ChoiceOut):
    options: list[ChoiceOptionResultOut] = []
    my_answer_option_ids: list[str] = []
    results_visible: bool = False
    access_restricted: bool = False
    access_reasons: list[str] = []


class ChoiceRespondIn(BaseModel):
    option_ids: list[str]
