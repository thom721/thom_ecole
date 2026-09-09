from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MResource import ResourceType


class ResourceFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    stored_path: str
    mime_type: str | None = None
    size_bytes: int | None = None
    uploaded_at: datetime


class ResourceBase(BaseModel):
    resource_type: ResourceType
    title: str
    description: str | None = None
    external_url: str | None = None
    page_content: str | None = None
    sort_order: int = 0
    is_visible: bool = True


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    external_url: str | None = None
    page_content: str | None = None
    sort_order: int | None = None
    is_visible: bool | None = None


class ResourceOut(ResourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    files: list[ResourceFileOut] = []
    # Calculés en direct (voir Helper/access_conditions.py), jamais stockés.
    access_restricted: bool = False
    access_reasons: list[str] = []
