import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Text, ForeignKey,
    Enum as SAEnum, Numeric, UniqueConstraint, JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class InteractiveVideoSourceType(str, enum.Enum):
    file = "file"
    url = "url"


class InteractiveVideoAttemptStatus(str, enum.Enum):
    in_progress = "in_progress"
    pending_manual_grading = "pending_manual_grading"
    completed = "completed"


class InteractiveVideo(Base):
    __tablename__ = "interactive_videos"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    source_type = Column(SAEnum(InteractiveVideoSourceType), nullable=False)
    video_url = Column(String(1000), nullable=True)
    stored_path = Column(String(1000), nullable=True)
    original_filename = Column(String(500), nullable=True)
    mime_type = Column(String(150), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    # Mesuré côté client (évènement loadedmetadata du lecteur), jamais
    # saisi à la main — voir plan Épic 18.
    duration_seconds = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def course_id(self) -> str:
        """Pratique pour le frontend (SInteractiveVideo.InteractiveVideoOut.course_id),
        même patron que Quiz.course_id — évite un aller-retour supplémentaire."""
        return self.section.course_id

    section = relationship("Section", back_populates="interactive_videos")
    checkpoints = relationship("InteractiveVideoCheckpoint", back_populates="video", cascade="all, delete-orphan", order_by="InteractiveVideoCheckpoint.timestamp_seconds")
    attempts = relationship("InteractiveVideoAttempt", back_populates="video", cascade="all, delete-orphan")
    grade_item = relationship("GradeItem", back_populates="interactive_video", uselist=False, cascade="all, delete-orphan")


class InteractiveVideoCheckpoint(Base):
    __tablename__ = "interactive_video_checkpoints"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    video_id = Column(String(36), ForeignKey("interactive_videos.id"), nullable=False)
    timestamp_seconds = Column(Numeric(10, 2), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    points = Column(Numeric(6, 2), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    video = relationship("InteractiveVideo", back_populates="checkpoints")
    question = relationship("Question")
    responses = relationship("InteractiveVideoResponse", back_populates="checkpoint", cascade="all, delete-orphan")


class InteractiveVideoAttempt(Base):
    __tablename__ = "interactive_video_attempts"
    __table_args__ = (
        UniqueConstraint("video_id", "student_id", name="uq_interactive_video_attempts_video_student"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    video_id = Column(String(36), ForeignKey("interactive_videos.id"), nullable=False)
    student_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(InteractiveVideoAttemptStatus), nullable=False, default=InteractiveVideoAttemptStatus.in_progress)
    last_position_seconds = Column(Numeric(10, 2), nullable=False, default=0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    score = Column(Numeric(6, 2), nullable=True)
    max_score = Column(Numeric(6, 2), nullable=True)
    graded_at = Column(DateTime, nullable=True)

    video = relationship("InteractiveVideo", back_populates="attempts")
    responses = relationship("InteractiveVideoResponse", back_populates="attempt", cascade="all, delete-orphan")


class InteractiveVideoResponse(Base):
    """Colonnes nommées à l'identique de QuizResponse pour réutiliser
    Helper/question_grading.py::auto_grade() sans modification (voir plan
    Épic 18 — duck-typing, aucune dépendance stricte au type QuizResponse)."""

    __tablename__ = "interactive_video_responses"
    __table_args__ = (
        UniqueConstraint("attempt_id", "checkpoint_id", name="uq_interactive_video_responses_attempt_checkpoint"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("interactive_video_attempts.id"), nullable=False)
    checkpoint_id = Column(String(36), ForeignKey("interactive_video_checkpoints.id"), nullable=False)
    points = Column(Numeric(6, 2), nullable=False)
    answer_data = Column(JSON, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    points_awarded = Column(Numeric(6, 2), nullable=True)
    feedback = Column(Text, nullable=True)
    graded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    attempt = relationship("InteractiveVideoAttempt", back_populates="responses")
    checkpoint = relationship("InteractiveVideoCheckpoint", back_populates="responses")
