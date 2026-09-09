from sqlalchemy.orm import Session

from app.Models.MNotification import Notification, NotificationKind


def notify(db: Session, user_id: str, kind: NotificationKind, title: str,
           body: str | None = None, link_url: str | None = None) -> None:
    """Appelée explicitement après le commit principal de l'action qui
    déclenche la notification (voir plan Phase 4 — pas de middleware)."""
    db.add(Notification(user_id=user_id, kind=kind, title=title, body=body, link_url=link_url))
    db.commit()
