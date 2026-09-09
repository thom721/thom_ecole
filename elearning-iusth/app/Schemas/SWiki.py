from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MWiki import WikiMode


class WikiCreate(BaseModel):
    title: str
    description: str | None = None
    mode: WikiMode = WikiMode.collaborative
    first_page_title: str = "Accueil"


class WikiUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_visible: bool | None = None


class WikiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    title: str
    description: str | None = None
    is_visible: bool
    mode: WikiMode
    first_page_title: str


class WikiPageSummaryOut(BaseModel):
    id: str
    title: str


class SubwikiOut(BaseModel):
    id: str
    wiki_id: str
    owner_id: str | None = None
    owner_name: str | None = None
    root_page_id: str | None = None
    pages: list[WikiPageSummaryOut] = []


class WikiPageCreate(BaseModel):
    title: str
    content: str = ""


class WikiPageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    subwiki_id: str
    title: str
    cached_content: str
    is_readonly: bool
    created_by: str | None = None
    updated_at: datetime
    current_version: int


class WikiVersionCreate(BaseModel):
    content: str


class WikiVersionSummaryOut(BaseModel):
    version: int
    created_by: str | None = None
    created_at: datetime


class WikiDiffOut(BaseModel):
    from_version: int
    to_version: int
    lines: list[str]
