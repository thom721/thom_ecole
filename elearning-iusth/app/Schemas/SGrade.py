from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.Models.MGrade import GradeItemKind


class GradeCategoryCreate(BaseModel):
    name: str
    weight_percent: Decimal
    sort_order: int = 0
    # 'intra' | 'finale' | None — voir MGrade.py::GradeCategory.evaluation_phase
    evaluation_phase: str | None = None


class GradeCategoryUpdate(BaseModel):
    name: str | None = None
    weight_percent: Decimal | None = None
    sort_order: int | None = None
    evaluation_phase: str | None = None


class GradeCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str
    name: str
    weight_percent: Decimal
    sort_order: int
    evaluation_phase: str | None = None


class GradeItemCreate(BaseModel):
    """Crée toujours un item manuel — kind est forcé côté route."""
    title: str
    max_points: Decimal
    grade_category_id: str | None = None
    sort_order: int = 0
    scale_id: str | None = None


class GradeItemUpdate(BaseModel):
    grade_category_id: str | None = None
    sort_order: int | None = None
    is_visible: bool | None = None
    # title/max_points : uniquement acceptés si kind=manual (validé dans la route)
    title: str | None = None
    max_points: Decimal | None = None
    scale_id: str | None = None


class GradeItemOut(BaseModel):
    """Construit explicitement dans les routes : title/max_points sont
    dérivés en direct depuis assignment/quiz plutôt que lus tels quels sur
    le modèle (voir plan Phase 3)."""
    id: str
    course_id: str
    grade_category_id: str | None = None
    kind: GradeItemKind
    assignment_id: str | None = None
    quiz_id: str | None = None
    lesson_id: str | None = None
    workshop_id: str | None = None
    title: str
    max_points: Decimal | None = None  # null pour kind=quiz/lesson (pas de valeur canonique)
    scale_id: str | None = None
    is_visible: bool
    sort_order: int


class ManualGradeSet(BaseModel):
    points: Decimal
    feedback: str | None = None


class ManualGradeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    grade_item_id: str
    student_id: str
    points: Decimal | None = None
    feedback: str | None = None
    graded_by: str | None = None
    graded_at: datetime | None = None


# --- Rapport de notes ---

class GradeReportCategoryOut(BaseModel):
    id: str
    name: str
    weight_percent: Decimal
    sort_order: int
    evaluation_phase: str | None = None


class GradeReportItemOut(BaseModel):
    id: str
    grade_category_id: str | None = None
    kind: GradeItemKind
    assignment_id: str | None = None
    quiz_id: str | None = None
    lesson_id: str | None = None
    workshop_id: str | None = None
    title: str
    max_points: Decimal | None = None
    scale_id: str | None = None
    sort_order: int


class GradeEntryOut(BaseModel):
    earned: Decimal | None = None
    possible: Decimal | None = None
    is_graded: bool
    # Résolu uniquement pour un item à échelle (voir plan Épic 8) — le
    # libellé du niveau correspondant au rang stocké dans `earned`.
    label: str | None = None


class CategorySubtotalOut(BaseModel):
    earned: Decimal
    possible: Decimal
    percent: Decimal


class StudentGradeRowOut(BaseModel):
    student_id: str
    student_name: str
    entries: dict[str, GradeEntryOut]
    category_subtotals: dict[str, CategorySubtotalOut]
    uncategorized_subtotal: CategorySubtotalOut | None = None
    final_percent: Decimal | None = None
    final_letter: str | None = None
    # Totaux pondérés calculés uniquement sur les catégories tagguées
    # evaluation_phase='intra'/'finale' (voir plan Épic 24) — indépendants
    # de final_percent, qui continue de mélanger toutes les catégories.
    intra_percent: Decimal | None = None
    finale_percent: Decimal | None = None


class GradeReportOut(BaseModel):
    course_id: str
    categories: list[GradeReportCategoryOut]
    items: list[GradeReportItemOut]
    rows: list[StudentGradeRowOut]
