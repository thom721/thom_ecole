import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class CourseFormat(str, enum.Enum):
    topics = "topics"
    weeks = "weeks"
    social = "social"


class CourseDisplay(str, enum.Enum):
    single_page = "single_page"
    paginated = "paginated"


class CourseCategory(Base):
    __tablename__ = "course_categories"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    parent_id = Column(String(36), ForeignKey("course_categories.id"), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    parent = relationship("CourseCategory", remote_side=[id], back_populates="children")
    children = relationship("CourseCategory", back_populates="parent")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("external_source", "external_ref_id", name="uq_courses_external_ref"),
        _TABLE_ARGS,
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    category_id = Column(String(36), ForeignKey("course_categories.id"), nullable=True)
    short_name = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)

    format = Column(SAEnum(CourseFormat), nullable=False, default=CourseFormat.topics)
    course_display = Column(SAEnum(CourseDisplay), nullable=False, default=CourseDisplay.single_page)
    # Pertinent seulement si format == social (voir plan Épic 14) — le
    # forum affiché en pleine page à la place de la grille de sections.
    social_forum_id = Column(String(36), ForeignKey("forums.id"), nullable=True)

    # Intégration ecole_nginx (voir plan) — nullable, seulement renseigné
    # pour un cours importé depuis un Programme externe. La contrainte
    # unique rend un ré-import idempotent (upsert plutôt que doublon) ;
    # MySQL autorise plusieurs paires NULL/NULL, donc les cours créés à la
    # main ne sont pas affectés.
    external_source = Column(String(50), nullable=True)
    external_ref_id = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    category = relationship("CourseCategory")
    sections = relationship("Section", back_populates="course", order_by="Section.sort_order", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_visible = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    course = relationship("Course", back_populates="sections")
    resources = relationship("Resource", back_populates="section", order_by="Resource.sort_order", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="section", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="section", cascade="all, delete-orphan")
    forums = relationship("Forum", back_populates="section", cascade="all, delete-orphan")
    choices = relationship("Choice", back_populates="section", cascade="all, delete-orphan")
    glossaries = relationship("Glossary", back_populates="section", cascade="all, delete-orphan")
    wikis = relationship("Wiki", back_populates="section", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="section", cascade="all, delete-orphan")
    workshops = relationship("Workshop", back_populates="section", cascade="all, delete-orphan")
    live_sessions = relationship("LiveSession", back_populates="section", cascade="all, delete-orphan")
    interactive_videos = relationship("InteractiveVideo", back_populates="section", cascade="all, delete-orphan")
