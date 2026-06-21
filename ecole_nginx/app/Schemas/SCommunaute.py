from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime
import enum

class AudienceType(str, enum.Enum):
    public      = "public"
    classe      = "classe"
    professeurs = "professeurs"

class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id:   int
    name: str

    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    title:       str
    description: Optional[str] = None
    location:    Optional[str] = None
    start_date:  datetime
    end_date:    Optional[datetime] = None
    image_url:   Optional[str] = None
    audience:    AudienceType = AudienceType.public
    is_published: bool = False
    category_id: Optional[int] = None

class EventUpdate(EventCreate):
    pass

class EventResponse(BaseModel):
    id:           int
    title:        str
    description:  Optional[str]
    location:     Optional[str]
    start_date:   datetime
    end_date:     Optional[datetime]
    image_url:    Optional[str]
    audience:     AudienceType
    is_published: bool
    category:     Optional[CategoryResponse]
    created_at:   datetime

    class Config:
        from_attributes = True





        

class NewsCreate(BaseModel):
    title:        str
    content:      Optional[str] = None
    image_url:    Optional[str] = None
    audience:     AudienceType = AudienceType.public
    is_published: bool = False
    published_at: Optional[datetime] = None
    category_id:  Optional[int] = None

class NewsUpdate(NewsCreate):
    pass

class NewsResponse(BaseModel):
    id:           int
    title:        str
    content:      Optional[str]
    image_url:    Optional[str]
    audience:     AudienceType
    is_published: bool
    published_at: Optional[datetime]
    category:     Optional[CategoryResponse]
    created_at:   datetime

    class Config:
        from_attributes = True