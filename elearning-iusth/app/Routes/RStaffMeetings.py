import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MStaffMeeting import StaffMeeting, StaffMeetingInvitee
from app.Models.MUser import User, SystemRole
from app.Schemas.SStaffMeeting import StaffMeetingCreate, StaffMeetingUpdate, StaffMeetingOut, EligibleUserOut, StaffMeetingJoinOut
from app.dependencies.auth import get_current_active_user
from app.Helper.permissions import require_permission
from app.Helper.live_sessions import build_jitsi_jwt
from app.Helper.email import send_staff_meeting_email
from app.config.Config import settings

router = APIRouter(prefix="/staff-meetings", tags=["staff-meetings"])


def _is_invited_or_creator(db: Session, meeting: StaffMeeting, user: User) -> bool:
    if user.system_role == SystemRole.admin or meeting.created_by == user.id:
        return True
    return (
        db.query(StaffMeetingInvitee)
        .filter(StaffMeetingInvitee.meeting_id == meeting.id, StaffMeetingInvitee.user_id == user.id)
        .first()
        is not None
    )


def _is_meeting_joinable(meeting: StaffMeeting, user: User) -> tuple[bool, str | None]:
    """Le créateur/un admin peut toujours rejoindre (même règle déjà
    établie pour les sessions en direct, Épic 17) ; un simple invité ne
    peut plus rejoindre une fois scheduled_end dépassée."""
    if meeting.created_by == user.id or user.system_role == SystemRole.admin:
        return True, None
    if meeting.scheduled_end is not None:
        now = datetime.now(timezone.utc)
        window_end = meeting.scheduled_end.replace(tzinfo=timezone.utc)
        if now > window_end:
            return False, "La réunion est terminée"
    return True, None


@router.get("/eligible-users", response_model=list[EligibleUserOut],
            dependencies=[Depends(require_permission("start_staff_meetings"))])
def list_eligible_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.system_role.in_([SystemRole.teacher, SystemRole.admin, SystemRole.staff])).order_by(User.last_name).all()
    return [
        EligibleUserOut(id=u.id, first_name=u.first_name, last_name=u.last_name, email=u.email, system_role=u.system_role.value)
        for u in users
    ]


@router.post("", response_model=StaffMeetingOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_permission("start_staff_meetings"))])
def create_staff_meeting(
    data: StaffMeetingCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    meeting = StaffMeeting(
        title=data.title, description=data.description, created_by=current_user.id,
        room_name=secrets.token_hex(16), scheduled_start=data.scheduled_start, scheduled_end=data.scheduled_end,
    )
    db.add(meeting)
    db.flush()

    invitees = db.query(User).filter(User.id.in_(data.invitee_user_ids)).all()
    # Le lien doit être construit par invité : la route frontend est préfixée
    # par portail (/teacher/staff-meetings/:id, /admin/..., /staff/... —
    # même convention que la messagerie, aucune route sans préfixe de rôle),
    # or un même invité peut être teacher, admin ou staff (Épic 23) selon
    # son compte réel.
    _PORTAL_BY_ROLE = {SystemRole.admin: "admin", SystemRole.staff: "staff"}
    invitee_contacts = [
        (u.email, u.first_name, _PORTAL_BY_ROLE.get(u.system_role, "teacher"))
        for u in invitees
    ]
    for invitee in invitees:
        db.add(StaffMeetingInvitee(meeting_id=meeting.id, user_id=invitee.id))

    meeting_id, meeting_title, scheduled_start = meeting.id, meeting.title, meeting.scheduled_start

    db.commit()
    db.refresh(meeting)

    background_tasks.add_task(_send_staff_meeting_emails, invitee_contacts, meeting_title, scheduled_start, meeting_id)

    return StaffMeetingOut(id=meeting.id, title=meeting.title, description=meeting.description,
                            scheduled_start=meeting.scheduled_start, scheduled_end=meeting.scheduled_end,
                            created_by=meeting.created_by, is_creator=True)


def _send_staff_meeting_emails(invitee_contacts: list[tuple[str, str, str]], meeting_title: str, scheduled_start, meeting_id: str) -> None:
    for email, first_name, portal in invitee_contacts:
        link_url = f"{settings.FRONTEND_BASE_URL}/{portal}/staff-meetings/{meeting_id}"
        try:
            send_staff_meeting_email(email, first_name, meeting_title, scheduled_start, link_url)
        except Exception as exc:
            print(f"[staff_meetings] échec d'envoi d'email à {email} : {exc}")


@router.get("/mine", response_model=list[StaffMeetingOut])
def list_my_staff_meetings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    created = db.query(StaffMeeting).filter(StaffMeeting.created_by == current_user.id).all()
    invited_ids = [
        row.meeting_id for row in
        db.query(StaffMeetingInvitee).filter(StaffMeetingInvitee.user_id == current_user.id).all()
    ]
    invited = db.query(StaffMeeting).filter(StaffMeeting.id.in_(invited_ids)).all() if invited_ids else []

    seen = {}
    for m in created + invited:
        seen[m.id] = m
    result = []
    for m in seen.values():
        is_joinable, join_error = _is_meeting_joinable(m, current_user)
        result.append(StaffMeetingOut(id=m.id, title=m.title, description=m.description, scheduled_start=m.scheduled_start,
                         scheduled_end=m.scheduled_end, created_by=m.created_by, is_creator=(m.created_by == current_user.id),
                         is_joinable=is_joinable, join_error=join_error))
    return result


@router.get("/{meeting_id}", response_model=StaffMeetingOut)
def get_staff_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    meeting = db.query(StaffMeeting).filter(StaffMeeting.id == meeting_id).first()
    # 404, jamais 403 — un non-invité ne doit jamais pouvoir confirmer
    # l'existence de la réunion (même principe que /messaging/lookup, Épic 11).
    if meeting is None or not _is_invited_or_creator(db, meeting, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réunion introuvable")
    is_joinable, join_error = _is_meeting_joinable(meeting, current_user)
    return StaffMeetingOut(id=meeting.id, title=meeting.title, description=meeting.description,
                            scheduled_start=meeting.scheduled_start, scheduled_end=meeting.scheduled_end,
                            created_by=meeting.created_by, is_creator=(meeting.created_by == current_user.id),
                            is_joinable=is_joinable, join_error=join_error)


@router.post("/{meeting_id}/join", response_model=StaffMeetingJoinOut)
def join_staff_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    meeting = db.query(StaffMeeting).filter(StaffMeeting.id == meeting_id).first()
    if meeting is None or not _is_invited_or_creator(db, meeting, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réunion introuvable")

    is_joinable, join_error = _is_meeting_joinable(meeting, current_user)
    if not is_joinable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=join_error)

    is_moderator = meeting.created_by == current_user.id or current_user.system_role == SystemRole.admin
    jwt_token = build_jitsi_jwt(meeting, current_user, is_moderator=is_moderator)
    return StaffMeetingJoinOut(jitsi_base_url=settings.JITSI_BASE_URL, room_name=meeting.room_name, jwt=jwt_token)


@router.patch("/{meeting_id}", response_model=StaffMeetingOut)
def update_staff_meeting(
    meeting_id: str,
    data: StaffMeetingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    meeting = db.query(StaffMeeting).filter(StaffMeeting.id == meeting_id).first()
    if meeting is None or not _is_invited_or_creator(db, meeting, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réunion introuvable")
    if meeting.created_by != current_user.id and current_user.system_role != SystemRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seul le créateur ou un admin peut modifier cette réunion")

    if data.title is not None:
        meeting.title = data.title
    if data.description is not None:
        meeting.description = data.description
    if data.scheduled_start is not None:
        meeting.scheduled_start = data.scheduled_start
    if data.scheduled_end is not None:
        meeting.scheduled_end = data.scheduled_end

    db.commit()
    db.refresh(meeting)
    return StaffMeetingOut(id=meeting.id, title=meeting.title, description=meeting.description,
                            scheduled_start=meeting.scheduled_start, scheduled_end=meeting.scheduled_end,
                            created_by=meeting.created_by, is_creator=(meeting.created_by == current_user.id))


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    meeting = db.query(StaffMeeting).filter(StaffMeeting.id == meeting_id).first()
    if meeting is None or not _is_invited_or_creator(db, meeting, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réunion introuvable")
    if meeting.created_by != current_user.id and current_user.system_role != SystemRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seul le créateur ou un admin peut supprimer cette réunion")
    db.delete(meeting)
    db.commit()
