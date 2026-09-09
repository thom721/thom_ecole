from sqlalchemy.orm import Session

from app.Models.MUser import User, MessagePrivacy
from app.Models.MEnrollment import Enrollment
from app.Models.MMessaging import Contact, BlockedUser


def are_contacts(db: Session, user_a_id: str, user_b_id: str) -> bool:
    return (
        db.query(Contact)
        .filter(
            ((Contact.user_id == user_a_id) & (Contact.contact_id == user_b_id))
            | ((Contact.user_id == user_b_id) & (Contact.contact_id == user_a_id))
        )
        .first()
        is not None
    )


def is_blocked(db: Session, blocker_id: str, blocked_id: str) -> bool:
    """`blocker_id` a-t-il bloqué `blocked_id` ?"""
    return (
        db.query(BlockedUser)
        .filter(BlockedUser.user_id == blocker_id, BlockedUser.blocked_user_id == blocked_id)
        .first()
        is not None
    )


def _share_a_course(db: Session, user_a_id: str, user_b_id: str) -> bool:
    a_courses = {e.course_id for e in db.query(Enrollment).filter(Enrollment.user_id == user_a_id).all()}
    if not a_courses:
        return False
    b_courses = {e.course_id for e in db.query(Enrollment).filter(Enrollment.user_id == user_b_id).all()}
    return bool(a_courses & b_courses)


def can_start_conversation(db: Session, sender: User, recipient: User) -> tuple[bool, str]:
    """Ne s'applique qu'au DÉMARRAGE d'une nouvelle conversation
    individuelle — n'affecte jamais une conversation déjà existante (voir
    plan Épic 11)."""
    if is_blocked(db, recipient.id, sender.id):
        return False, "Cet utilisateur ne vous accepte pas comme contact"

    if recipient.message_privacy == MessagePrivacy.site:
        return True, ""
    if recipient.message_privacy == MessagePrivacy.only_contacts:
        if are_contacts(db, sender.id, recipient.id):
            return True, ""
        return False, "Cet utilisateur n'accepte les messages que de ses contacts"
    # course_member (défaut)
    if are_contacts(db, sender.id, recipient.id) or _share_a_course(db, sender.id, recipient.id):
        return True, ""
    return False, "Vous devez partager un cours avec cet utilisateur pour lui écrire"
