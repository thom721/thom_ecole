from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GlossaryBase(BaseModel):
    title: str
    description: str | None = None
    is_main: bool = False
    allow_student_entries: bool = False
    require_approval: bool = False
    allow_duplicates: bool = False


class GlossaryCreate(GlossaryBase):
    pass


class GlossaryUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_visible: bool | None = None
    is_main: bool | None = None
    allow_student_entries: bool | None = None
    require_approval: bool | None = None
    allow_duplicates: bool | None = None


class GlossaryOut(GlossaryBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    is_visible: bool


class GlossaryEntryCreate(BaseModel):
    concept: str
    definition: str


class GlossaryEntryUpdate(BaseModel):
    concept: str | None = None
    definition: str | None = None


class GlossaryEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    glossary_id: str
    concept: str
    definition: str
    created_by: str | None = None
    is_approved: bool
    created_at: datetime


class GlossaryDetailOut(GlossaryOut):
    entries: list[GlossaryEntryOut] = []


class GlossaryConceptOut(BaseModel):
    entry_id: str
    concept: str
