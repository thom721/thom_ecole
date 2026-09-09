import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.Models.MUser import User
from app.Models.MCourse import Course
from app.Models.MEnrollment import Enrollment, EnrollmentStatus
from app.Models.MAccessLog import AccessLog
from app.Models.MBadge import BadgeIssued
from app.Models.MBlock import UserBlockInstance, BlockType
from app.Models.MMessaging import ConversationMember, MessageUserAction, MessageActionType

_ONLINE_WINDOW_MINUTES = 5


def _enrolled_course_ids(db: Session, user_id: str) -> list[str]:
    return [
        e.course_id for e in
        db.query(Enrollment).filter(Enrollment.user_id == user_id, Enrollment.status == EnrollmentStatus.active).all()
    ]


def compute_block_data(db: Session, block: UserBlockInstance, current_user: User) -> dict:
    """Dispatch par type — réutilise directement les fonctions/requêtes
    déjà existantes de chaque sous-système (voir plan Épic 15), aucune
    nouvelle logique métier ici, seulement de l'agrégation d'affichage."""

    if block.block_type == BlockType.html:
        try:
            return json.loads(block.config_json) if block.config_json else {"title": "", "content": ""}
        except json.JSONDecodeError:
            return {"title": "", "content": ""}

    if block.block_type == BlockType.my_courses:
        courses = (
            db.query(Course)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .filter(Enrollment.user_id == current_user.id)
            .order_by(Course.full_name)
            .limit(10)
            .all()
        )
        return {"courses": [{"id": c.id, "full_name": c.full_name, "short_name": c.short_name} for c in courses]}

    if block.block_type == BlockType.calendar:
        from app.Routes.RCalendar import _virtual_events_for_course
        from app.Models.MCalendar import CalendarEvent

        # `_virtual_events_for_course` compare en Python contre des
        # colonnes DATETIME MySQL (naïves) — lui passer des datetimes
        # naïves ici, cohérent avec ce que `GET /calendar` lui transmet
        # déjà (des query params sans fuseau explicite).
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        end = now + timedelta(days=7)
        course_ids = _enrolled_course_ids(db, current_user.id)
        manual = (
            db.query(CalendarEvent)
            .filter(CalendarEvent.start_at >= now, CalendarEvent.start_at <= end,
                    (CalendarEvent.course_id.in_(course_ids)) | (CalendarEvent.course_id.is_(None)))
            .all()
            if course_ids else []
        )
        events = [{"title": e.title, "start_at": e.start_at.isoformat()} for e in manual]
        for cid in course_ids:
            events += [{"title": e.title, "start_at": e.start_at.isoformat()} for e in _virtual_events_for_course(db, cid, now, end)]
        events.sort(key=lambda e: e["start_at"])
        return {"events": events[:10]}

    if block.block_type == BlockType.recent_activity:
        logs = (
            db.query(AccessLog)
            .filter(AccessLog.user_id == current_user.id)
            .order_by(AccessLog.accessed_at.desc())
            .limit(10)
            .all()
        )
        return {"items": [{"item_type": l.item_type.value, "item_id": l.item_id, "course_id": l.course_id, "accessed_at": l.accessed_at.isoformat()} for l in logs]}

    if block.block_type == BlockType.grades_overview:
        from app.Routes.RGrades import _build_report

        rows = []
        for course_id in _enrolled_course_ids(db, current_user.id):
            report = _build_report(db, course_id, only_student_id=current_user.id)
            if report.rows:
                course = db.query(Course).filter(Course.id == course_id).first()
                rows.append({
                    "course_id": course_id, "course_name": course.full_name if course else "?",
                    "final_percent": float(report.rows[0].final_percent) if report.rows[0].final_percent is not None else None,
                    "final_letter": report.rows[0].final_letter,
                })
        return {"courses": rows}

    if block.block_type == BlockType.badges:
        issued = (
            db.query(BadgeIssued)
            .filter(BadgeIssued.user_id == current_user.id)
            .order_by(BadgeIssued.issued_at.desc())
            .limit(5)
            .all()
        )
        return {"badges": [{"badge_id": i.badge_id, "name": i.badge.name, "image_emoji": i.badge.image_emoji, "issued_at": i.issued_at.isoformat()} for i in issued]}

    if block.block_type == BlockType.messages:
        memberships = db.query(ConversationMember).filter(ConversationMember.user_id == current_user.id).all()
        unread_total = 0
        previews = []
        for m in memberships:
            messages = m.conversation.messages
            deleted_ids = {
                a.message_id for a in db.query(MessageUserAction).filter(
                    MessageUserAction.user_id == current_user.id, MessageUserAction.action == MessageActionType.deleted,
                ).all()
            }
            read_ids = {
                a.message_id for a in db.query(MessageUserAction).filter(
                    MessageUserAction.user_id == current_user.id, MessageUserAction.action == MessageActionType.read,
                ).all()
            }
            unread_total += sum(1 for msg in messages if msg.sender_id != current_user.id and msg.id not in read_ids and msg.id not in deleted_ids)
            last = messages[-1] if messages else None
            if last:
                previews.append({"conversation_id": m.conversation_id, "last_message": last.content[:80], "at": last.created_at.isoformat()})
        previews.sort(key=lambda p: p["at"], reverse=True)
        return {"unread_count": unread_total, "conversations": previews[:5]}

    if block.block_type == BlockType.online_users:
        course_ids = _enrolled_course_ids(db, current_user.id)
        if not course_ids:
            return {"users": []}
        peer_ids = {
            e.user_id for e in db.query(Enrollment).filter(Enrollment.course_id.in_(course_ids)).all()
            if e.user_id != current_user.id
        }
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=_ONLINE_WINDOW_MINUTES)
        candidates = db.query(User).filter(User.id.in_(peer_ids), User.last_login_at.isnot(None)).all() if peer_ids else []
        # Comparaison en Python (même convention que partout ailleurs dans
        # ce projet, ex. WorkshopSubmission.submission_end) — les colonnes
        # DATETIME MySQL sont naïves, `.replace(tzinfo=utc)` les rend
        # comparables à `datetime.now(timezone.utc)`.
        online = [u for u in candidates if u.last_login_at.replace(tzinfo=timezone.utc) >= cutoff]
        return {"users": [{"id": u.id, "first_name": u.first_name, "last_name": u.last_name} for u in online]}

    return {}
