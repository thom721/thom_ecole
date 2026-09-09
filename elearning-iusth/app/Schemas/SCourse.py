from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.Models.MCourse import CourseFormat, CourseDisplay


class CourseCategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: str | None = None
    sort_order: int = 0


class CourseCategoryCreate(CourseCategoryBase):
    pass


class CourseCategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    parent_id: str | None = None
    sort_order: int | None = None


class CourseCategoryOut(CourseCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class CourseBase(BaseModel):
    category_id: str | None = None
    short_name: str
    full_name: str
    summary: str | None = None
    is_visible: bool = True
    start_date: date | None = None
    end_date: date | None = None
    format: CourseFormat = CourseFormat.topics
    course_display: CourseDisplay = CourseDisplay.single_page
    social_forum_id: str | None = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    category_id: str | None = None
    short_name: str | None = None
    full_name: str | None = None
    summary: str | None = None
    is_visible: bool | None = None
    start_date: date | None = None
    end_date: date | None = None
    format: CourseFormat | None = None
    course_display: CourseDisplay | None = None
    social_forum_id: str | None = None


class CourseOut(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_by: str | None = None
    created_at: datetime


class CoursePageOut(BaseModel):
    items: list[CourseOut]
    total: int
    page: int
    page_size: int


class SectionBase(BaseModel):
    title: str | None = None
    summary: str | None = None
    sort_order: int = 0
    is_visible: bool = True


class SectionCreate(SectionBase):
    pass


class SectionUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    sort_order: int | None = None
    is_visible: bool | None = None


class SectionOut(SectionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str
    week_start: datetime | None = None
    week_end: datetime | None = None


class CourseDetailOut(CourseOut):
    """Utilisé par GET /courses/{id} : structure imbriquée complète."""
    sections: list["SectionWithContentOut"] = []
    social_forum: "ForumOut | None" = None  # pertinent seulement si format == social


class SectionWithContentOut(SectionOut):
    resources: list["ResourceOut"] = []
    assignments: list["AssignmentOut"] = []
    quizzes: list["QuizOut"] = []
    forums: list["ForumOut"] = []
    choices: list["ChoiceOut"] = []
    glossaries: list["GlossaryOut"] = []
    wikis: list["WikiOut"] = []
    lessons: list["LessonOut"] = []
    workshops: list["WorkshopOut"] = []
    live_sessions: list["LiveSessionOut"] = []
    interactive_videos: list["InteractiveVideoOut"] = []


# Imports en fin de fichier pour éviter un cycle (Resource/Assignment/Quiz/
# Forum/Choice/Glossary/Wiki/Lesson/Workshop/LiveSession/InteractiveVideo
# référencent aussi ce module indirectement via Section).
from app.Schemas.SResource import ResourceOut  # noqa: E402
from app.Schemas.SAssignment import AssignmentOut  # noqa: E402
from app.Schemas.SQuiz import QuizOut  # noqa: E402
from app.Schemas.SForum import ForumOut  # noqa: E402
from app.Schemas.SChoice import ChoiceOut  # noqa: E402
from app.Schemas.SGlossary import GlossaryOut  # noqa: E402
from app.Schemas.SWiki import WikiOut  # noqa: E402
from app.Schemas.SLesson import LessonOut  # noqa: E402
from app.Schemas.SWorkshop import WorkshopOut  # noqa: E402
from app.Schemas.SLiveSession import LiveSessionOut  # noqa: E402
from app.Schemas.SInteractiveVideo import InteractiveVideoOut  # noqa: E402

CourseDetailOut.model_rebuild()
SectionWithContentOut.model_rebuild()
