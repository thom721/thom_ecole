from datetime import datetime

from pydantic import BaseModel


class CalendarEventCreate(BaseModel):
    course_id: str | None = None  # null = site (admin uniquement, validé en route)
    title: str
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None


class CalendarEventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None


class CalendarEventOut(BaseModel):
    """Construit à la main : les événements virtuels (devoir/quiz) n'ont
    pas de ligne réelle en base (voir plan Phase 4)."""
    id: str  # UUID réel pour les manuels, "assignment:<id>"/"quiz:<id>" pour les virtuels
    course_id: str | None = None
    title: str
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None
    event_type: str  # manual | assignment_due | quiz_window
    source_id: str | None = None  # id réel de l'assignment/quiz sous-jacent, pour le lien frontend
