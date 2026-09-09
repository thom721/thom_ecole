from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid
from app.Models.MGroup import GroupMode

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class Forum(Base):
    __tablename__ = "forums"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    # Défaut no_groups — rétrocompatible par construction, tout forum
    # existant continue d'afficher toutes les discussions (voir plan Épic 5).
    group_mode = Column(SAEnum(GroupMode), nullable=False, default=GroupMode.no_groups)
    grouping_id = Column(String(36), ForeignKey("groupings.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="forums")
    discussions = relationship("ForumDiscussion", back_populates="forum", cascade="all, delete-orphan")


class ForumDiscussion(Base):
    __tablename__ = "forum_discussions"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    forum_id = Column(String(36), ForeignKey("forums.id"), nullable=False)
    title = Column(String(255), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    forum = relationship("Forum", back_populates="discussions")
    posts = relationship("ForumPost", back_populates="discussion", cascade="all, delete-orphan")
    subscriptions = relationship("ForumSubscription", back_populates="discussion", cascade="all, delete-orphan")
    read_states = relationship("ForumReadState", back_populates="discussion", cascade="all, delete-orphan")


class ForumPost(Base):
    """`parent_post_id` supporte une profondeur arbitraire en base (même
    forme que CourseCategory.parent_id), mais la route n'autorise qu'un
    seul niveau de réponse (voir plan Phase 4)."""

    __tablename__ = "forum_posts"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    discussion_id = Column(String(36), ForeignKey("forum_discussions.id"), nullable=False)
    parent_post_id = Column(String(36), ForeignKey("forum_posts.id"), nullable=True)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    body = Column(Text, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    discussion = relationship("ForumDiscussion", back_populates="posts")
    parent = relationship("ForumPost", remote_side=[id], back_populates="replies")
    replies = relationship("ForumPost", back_populates="parent", cascade="all, delete-orphan")


class ForumSubscription(Base):
    __tablename__ = "forum_subscriptions"
    __table_args__ = (
        UniqueConstraint("discussion_id", "user_id", name="uq_forum_subscriptions_discussion_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    discussion_id = Column(String(36), ForeignKey("forum_discussions.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subscribed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    discussion = relationship("ForumDiscussion", back_populates="subscriptions")


class ForumReadState(Base):
    """Suivi de lecture PAR DISCUSSION, pas par message (voir plan Phase 4)
    — "non lu" comparé en direct à MAX(ForumPost.created_at), jamais
    stocké/dupliqué ici."""

    __tablename__ = "forum_read_state"
    __table_args__ = (
        UniqueConstraint("discussion_id", "user_id", name="uq_forum_read_state_discussion_user"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    discussion_id = Column(String(36), ForeignKey("forum_discussions.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    last_read_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    discussion = relationship("ForumDiscussion", back_populates="read_states")
