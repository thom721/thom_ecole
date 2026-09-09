from sqlalchemy.orm import Session

from app.Models.MCompletion import ActivityCompletion, CompletionItemType


def mark_complete_if_absent(db: Session, student_id: str, item_type: CompletionItemType, item_id: str) -> None:
    """Insère seulement si absent, pour ne jamais réinitialiser
    completed_at (voir plan Phase 5 : l'achèvement est marqué la première
    fois qu'un item est noté, pas à chaque nouvelle tentative/note)."""
    existing = (
        db.query(ActivityCompletion)
        .filter(ActivityCompletion.student_id == student_id, ActivityCompletion.item_type == item_type,
                ActivityCompletion.item_id == item_id)
        .first()
    )
    if existing is None:
        db.add(ActivityCompletion(student_id=student_id, item_type=item_type, item_id=item_id))
        db.commit()

    # Point de déclenchement unique pour la réévaluation des badges (Épic
    # 12) ET des compétences (Épic 13) — partagé par TOUTE activité
    # (présente et future) sans avoir à toucher aux 8+ endroits qui
    # appellent cette fonction. Résout course_id via le même dispatch déjà
    # établi dans RAccessConditions.py::_resolve_course_id (import différé
    # pour éviter un cycle : ce module de route importe des modèles, pas
    # ce helper).
    from fastapi import HTTPException
    from app.Routes.RAccessConditions import _resolve_course_id
    from app.Helper.badges import evaluate_badges_for_student
    from app.Helper.competencies import evaluate_competencies_for_activity_completion

    try:
        course_id = _resolve_course_id(db, item_type, item_id)
    except HTTPException:
        course_id = None
    evaluate_badges_for_student(db, student_id, course_id)
    evaluate_competencies_for_activity_completion(db, student_id, course_id, item_type, item_id)
