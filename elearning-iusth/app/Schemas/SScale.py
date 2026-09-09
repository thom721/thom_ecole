from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ScaleLevelIn(BaseModel):
    label: str
    rank: int
    sort_order: int = 0


class ScaleLevelOut(ScaleLevelIn):
    model_config = ConfigDict(from_attributes=True)
    id: str


class ScaleCreate(BaseModel):
    name: str
    description: str | None = None
    levels: list[ScaleLevelIn] = []


class ScaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str | None = None
    name: str
    description: str | None = None
    levels: list[ScaleLevelOut] = []


class GradeLetterIn(BaseModel):
    letter: str
    lower_boundary: Decimal


class GradeLetterOut(GradeLetterIn):
    model_config = ConfigDict(from_attributes=True)
    id: str


class GradeLettersUpdate(BaseModel):
    letters: list[GradeLetterIn]
