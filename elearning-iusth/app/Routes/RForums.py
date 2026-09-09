from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MForum import Forum, ForumDiscussion, ForumPost, ForumSubscription, ForumReadState
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Models.MNotification import NotificationKind
from app.Schemas.SForum import (
    ForumCreate, ForumUpdate, ForumOut, ForumDetailOut, DiscussionSummaryOut,
    DiscussionCreate, PostCreate, PostUpdate, PostOut, DiscussionDetailOut,
)
from app.Models.MGroup import GroupMode
from app.Models.MAccessLog import AccessItemType
from app.Models.MCompletion import CompletionItemType, CompletionMode
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role
from app.Helper.notifications import notify
from app.Helper.groups import users_share_a_group
from app.Helper.access_log import log_access
from app.Helper.access_conditions import is_item_accessible
from app.Helper.completion_config import get_completion_mode
from app.Helper.completion import mark_complete_if_absent

router = APIRouter(tags=["forums"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _is_teaching(db: Session, current_user: User, course_id: str) -> bool:
    if current_user.system_role == SystemRole.admin:
        return True
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    return enrollment is not None and enrollment.role_in_course in _TEACHING_ROLES


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_forum_and_course(db: Session, forum_id: str) -> tuple[Forum, str]:
    forum = db.query(Forum).filter(Forum.id == forum_id).first()
    if forum is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forum introuvable")
    section = db.query(Section).filter(Section.id == forum.section_id).first()
    return forum, section.course_id


def _get_discussion_and_course(db: Session, discussion_id: str) -> tuple[ForumDiscussion, str]:
    discussion = db.query(ForumDiscussion).filter(ForumDiscussion.id == discussion_id).first()
    if discussion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion introuvable")
    _forum, course_id = _get_forum_and_course(db, discussion.forum_id)
    return discussion, course_id


def _subscribe(db: Session, discussion_id: str, user_id: str) -> None:
    existing = (
        db.query(ForumSubscription)
        .filter(ForumSubscription.discussion_id == discussion_id, ForumSubscription.user_id == user_id)
        .first()
    )
    if existing is None:
        db.add(ForumSubscription(discussion_id=discussion_id, user_id=user_id))


@router.post("/sections/{section_id}/forums", response_model=ForumOut, status_code=status.HTTP_201_CREATED)
def create_forum(
    section_id: str, data: ForumCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)
    forum = Forum(section_id=section_id, **data.model_dump())
    db.add(forum)
    db.commit()
    db.refresh(forum)
    return forum


@router.get("/forums/{forum_id}", response_model=ForumDetailOut)
def get_forum(
    forum_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    forum, course_id = _get_forum_and_course(db, forum_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    accessible, reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.forum, forum_id)
    if not accessible:
        return ForumDetailOut(
            id=forum.id, section_id=forum.section_id, title=forum.title, description=forum.description,
            is_visible=forum.is_visible, group_mode=forum.group_mode, grouping_id=forum.grouping_id,
            discussions=[], access_restricted=True, access_reasons=reasons,
        )

    log_access(db, current_user, course_id, AccessItemType.forum, forum_id)
    if get_completion_mode(db, CompletionItemType.forum, forum_id) == CompletionMode.automatic:
        mark_complete_if_absent(db, current_user.id, CompletionItemType.forum, forum_id)

    visible_discussions = forum.discussions
    if forum.group_mode == GroupMode.separate_groups and not _is_teaching(db, current_user, course_id):
        # Filtré à la lecture par appartenance de groupe de l'auteur —
        # jamais un tag figé sur la discussion (voir plan Épic 5).
        visible_discussions = [
            d for d in forum.discussions
            if d.created_by and users_share_a_group(db, current_user.id, d.created_by, course_id, forum.grouping_id)
        ]

    discussions_out = []
    for discussion in visible_discussions:
        post_count = len(discussion.posts)
        last_post_at = max((p.created_at for p in discussion.posts), default=None)
        is_subscribed = any(s.user_id == current_user.id for s in discussion.subscriptions)
        read_state = next((r for r in discussion.read_states if r.user_id == current_user.id), None)
        is_unread = last_post_at is not None and (read_state is None or read_state.last_read_at < last_post_at)
        discussions_out.append(DiscussionSummaryOut(
            id=discussion.id, title=discussion.title, created_by=discussion.created_by,
            created_at=discussion.created_at, post_count=post_count, last_post_at=last_post_at,
            is_subscribed=is_subscribed, is_unread=is_unread,
        ))

    return ForumDetailOut(
        id=forum.id, section_id=forum.section_id, title=forum.title,
        description=forum.description, is_visible=forum.is_visible,
        group_mode=forum.group_mode, grouping_id=forum.grouping_id, discussions=discussions_out,
    )


@router.patch("/forums/{forum_id}", response_model=ForumOut)
def update_forum(
    forum_id: str, data: ForumUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    forum, course_id = _get_forum_and_course(db, forum_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(forum, field, value)
    db.commit()
    db.refresh(forum)
    return forum


@router.delete("/forums/{forum_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_forum(
    forum_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    forum, course_id = _get_forum_and_course(db, forum_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    if db.query(ForumDiscussion).filter(ForumDiscussion.forum_id == forum_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Ce forum a déjà des discussions — suppression bloquée")
    db.delete(forum)
    db.commit()


@router.post("/forums/{forum_id}/discussions", response_model=DiscussionDetailOut, status_code=status.HTTP_201_CREATED)
def create_discussion(
    forum_id: str, data: DiscussionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _forum, course_id = _get_forum_and_course(db, forum_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    accessible, reasons = is_item_accessible(db, current_user, course_id, CompletionItemType.forum, forum_id)
    if not accessible:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="; ".join(reasons) or "Accès restreint")

    discussion = ForumDiscussion(forum_id=forum_id, title=data.title, created_by=current_user.id)
    db.add(discussion)
    db.flush()
    post = ForumPost(discussion_id=discussion.id, author_id=current_user.id, body=data.body)
    db.add(post)
    _subscribe(db, discussion.id, current_user.id)
    db.commit()
    db.refresh(discussion)

    return DiscussionDetailOut(
        id=discussion.id, forum_id=discussion.forum_id, course_id=course_id, title=discussion.title,
        created_by=discussion.created_by, created_at=discussion.created_at,
        is_subscribed=True, posts=[PostOut.model_validate(post)],
    )


@router.get("/forum-discussions/{discussion_id}", response_model=DiscussionDetailOut)
def get_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    discussion, course_id = _get_discussion_and_course(db, discussion_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    read_state = (
        db.query(ForumReadState)
        .filter(ForumReadState.discussion_id == discussion_id, ForumReadState.user_id == current_user.id)
        .first()
    )
    if read_state is None:
        db.add(ForumReadState(discussion_id=discussion_id, user_id=current_user.id))
    else:
        read_state.last_read_at = datetime.now(timezone.utc)
    db.commit()

    is_subscribed = (
        db.query(ForumSubscription)
        .filter(ForumSubscription.discussion_id == discussion_id, ForumSubscription.user_id == current_user.id)
        .first() is not None
    )
    posts = db.query(ForumPost).filter(ForumPost.discussion_id == discussion_id).order_by(ForumPost.created_at).all()

    return DiscussionDetailOut(
        id=discussion.id, forum_id=discussion.forum_id, course_id=course_id, title=discussion.title,
        created_by=discussion.created_by, created_at=discussion.created_at,
        is_subscribed=is_subscribed, posts=[PostOut.model_validate(p) for p in posts],
    )


@router.post("/forum-discussions/{discussion_id}/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    discussion_id: str, data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    discussion, course_id = _get_discussion_and_course(db, discussion_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    if data.parent_post_id is not None:
        parent = db.query(ForumPost).filter(ForumPost.id == data.parent_post_id).first()
        if parent is None or parent.discussion_id != discussion_id or parent.parent_post_id is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="On ne peut répondre qu'à un post racine de cette discussion")

    post = ForumPost(discussion_id=discussion_id, parent_post_id=data.parent_post_id,
                      author_id=current_user.id, body=data.body)
    db.add(post)
    _subscribe(db, discussion_id, current_user.id)
    db.commit()
    db.refresh(post)

    subscribers = db.query(ForumSubscription).filter(
        ForumSubscription.discussion_id == discussion_id, ForumSubscription.user_id != current_user.id,
    ).all()
    for sub in subscribers:
        notify(db, sub.user_id, NotificationKind.new_forum_post,
               title=f"Nouvelle réponse dans « {discussion.title} »", body=data.body[:200],
               link_url=f"/forum-discussions/{discussion_id}")

    return post


@router.patch("/forum-posts/{post_id}", response_model=PostOut)
def update_post(
    post_id: str, data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post introuvable")
    _discussion, course_id = _get_discussion_and_course(db, post.discussion_id)
    if post.author_id != current_user.id:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    post.body = data.body
    db.commit()
    db.refresh(post)
    return post


@router.delete("/forum-posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post introuvable")
    _discussion, course_id = _get_discussion_and_course(db, post.discussion_id)
    if post.author_id != current_user.id:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    if db.query(ForumPost).filter(ForumPost.parent_post_id == post_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce post a des réponses — supprimez-les d'abord")

    db.delete(post)
    db.commit()


@router.post("/forum-discussions/{discussion_id}/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def subscribe_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    _discussion, course_id = _get_discussion_and_course(db, discussion_id)
    if get_enrollment_or_none(db, course_id, current_user.id) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    _subscribe(db, discussion_id, current_user.id)
    db.commit()


@router.delete("/forum-discussions/{discussion_id}/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    sub = (
        db.query(ForumSubscription)
        .filter(ForumSubscription.discussion_id == discussion_id, ForumSubscription.user_id == current_user.id)
        .first()
    )
    if sub is not None:
        db.delete(sub)
        db.commit()


@router.delete("/forum-discussions/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discussion(
    discussion_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    discussion, course_id = _get_discussion_and_course(db, discussion_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    db.delete(discussion)
    db.commit()
