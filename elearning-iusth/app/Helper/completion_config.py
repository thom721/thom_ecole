from sqlalchemy.orm import Session

from app.Models.MCompletion import ActivityCompletionConfig, CompletionItemType, CompletionMode

# Comportement Phase 5 préservé quand aucune configuration n'existe —
# Forum/Choice n'étaient pas suivis avant l'Épic 7, démarrent à `none`
# pour ne jamais apparaître soudainement dans un pourcentage existant.
_DEFAULT_MODE = {
    CompletionItemType.resource: CompletionMode.manual,
    CompletionItemType.assignment: CompletionMode.automatic,
    CompletionItemType.quiz: CompletionMode.automatic,
    CompletionItemType.forum: CompletionMode.none,
    CompletionItemType.choice: CompletionMode.none,
    CompletionItemType.lesson: CompletionMode.none,
    CompletionItemType.workshop: CompletionMode.none,
    CompletionItemType.live_session: CompletionMode.none,
    CompletionItemType.interactive_video: CompletionMode.none,
}


def get_completion_mode(db: Session, item_type: CompletionItemType, item_id: str) -> CompletionMode:
    config = (
        db.query(ActivityCompletionConfig)
        .filter(ActivityCompletionConfig.item_type == item_type, ActivityCompletionConfig.item_id == item_id)
        .first()
    )
    if config is not None:
        return config.mode
    return _DEFAULT_MODE[item_type]
