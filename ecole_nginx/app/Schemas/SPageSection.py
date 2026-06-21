from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class PageSectionBase(BaseModel):
    page:        str
    section_key: str
    titre:       Optional[str]  = None
    sous_titre:  Optional[str]  = None
    description: Optional[str]  = None
    is_visible:  Optional[bool] = True
    ordre:       Optional[int]  = 0
    items:       Optional[List[Any]] = []

class PageSectionCreate(PageSectionBase):
    pass

class PageSectionUpdate(BaseModel):
    titre:       Optional[str]       = None
    sous_titre:  Optional[str]       = None
    description: Optional[str]       = None
    is_visible:  Optional[bool]      = None
    ordre:       Optional[int]       = None
    items:       Optional[List[Any]] = None

class PageSectionResponse(PageSectionBase):
    id:         int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
