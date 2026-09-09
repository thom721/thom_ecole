from decimal import Decimal

from sqlalchemy.orm import Session

from app.Models.MScale import GradeLetter

# Barème par défaut appliqué quand un cours n'a configuré aucune lettre —
# jamais semé en base (voir plan Épic 8), juste calculé à la volée.
_DEFAULT_BOUNDARIES = [
    ("A", Decimal("90")),
    ("B", Decimal("80")),
    ("C", Decimal("70")),
    ("D", Decimal("60")),
    ("F", Decimal("0")),
]


def resolve_letter(db: Session, course_id: str, percent: Decimal | None) -> str | None:
    if percent is None:
        return None

    rows = (
        db.query(GradeLetter)
        .filter(GradeLetter.course_id == course_id)
        .order_by(GradeLetter.lower_boundary.desc())
        .all()
    )
    boundaries = [(r.letter, r.lower_boundary) for r in rows] if rows else _DEFAULT_BOUNDARIES

    for letter, lower_boundary in boundaries:
        if percent >= lower_boundary:
            return letter
    return None
