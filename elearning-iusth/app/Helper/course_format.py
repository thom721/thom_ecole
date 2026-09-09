from datetime import datetime, timedelta, time, timezone

from app.Models.MCourse import Course, Section, CourseFormat


def section_week_dates(course: Course, section: Section) -> tuple[datetime, datetime] | None:
    """Semaine N = `course.start_date + (sort_order-1)×7j` à `+7j` de
    plus — calculé en direct, jamais stocké (voir plan Épic 14). `None`
    si le format n'est pas `weeks` ou si le cours n'a pas de date de
    début : rien à afficher plutôt qu'une date fausse."""
    if course.format != CourseFormat.weeks or course.start_date is None:
        return None
    start = datetime.combine(course.start_date, time.min, tzinfo=timezone.utc)
    week_start = start + timedelta(weeks=section.sort_order - 1)
    week_end = week_start + timedelta(weeks=1)
    return week_start, week_end
