from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MGroup import GroupMode


class ForumCreate(BaseModel):
    title: str
    description: str | None = None
    group_mode: GroupMode = GroupMode.no_groups
    grouping_id: str | None = None


class ForumUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_visible: bool | None = None
    group_mode: GroupMode | None = None
    grouping_id: str | None = None


class ForumOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    section_id: str
    title: str
    description: str | None = None
    group_mode: GroupMode
    grouping_id: str | None = None
    is_visible: bool


class DiscussionSummaryOut(BaseModel):
    """Construit à la main dans la route : post_count/last_post_at/
    is_subscribed/is_unread n'existent pas comme colonnes sur le modèle."""
    id: str
    title: str
    created_by: str | None = None
    created_at: datetime
    post_count: int
    last_post_at: datetime | None = None
    is_subscribed: bool
    is_unread: bool


class ForumDetailOut(ForumOut):
    discussions: list[DiscussionSummaryOut] = []
    access_restricted: bool = False
    access_reasons: list[str] = []


class DiscussionCreate(BaseModel):
    title: str
    body: str  # contenu du post d'ouverture, créé dans le même appel


class PostCreate(BaseModel):
    body: str
    parent_post_id: str | None = None


class PostUpdate(BaseModel):
    body: str


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    discussion_id: str
    parent_post_id: str | None = None
    author_id: str | None = None
    body: str
    created_at: datetime
    updated_at: datetime


class DiscussionDetailOut(BaseModel):
    id: str
    forum_id: str
    course_id: str
    title: str
    created_by: str | None = None
    created_at: datetime
    is_subscribed: bool
    posts: list[PostOut] = []
