import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SAEnum, BigInteger
from sqlalchemy.orm import relationship

from app.database import Base, generate_uuid

_TABLE_ARGS = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class ResourceType(str, enum.Enum):
    file = "file"
    page = "page"
    url = "url"
    folder = "folder"


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    section_id = Column(String(36), ForeignKey("sections.id"), nullable=False)
    resource_type = Column(SAEnum(ResourceType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    external_url = Column(String(1000), nullable=True)
    page_content = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_visible = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    section = relationship("Section", back_populates="resources")
    files = relationship("ResourceFile", back_populates="resource", cascade="all, delete-orphan")


class ResourceFile(Base):
    """Couvre `file` (1 ligne) et `folder` (N lignes) uniformément."""

    __tablename__ = "resource_files"
    __table_args__ = _TABLE_ARGS

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False)
    original_filename = Column(String(500), nullable=False)
    stored_path = Column(String(1000), nullable=False)
    mime_type = Column(String(150), nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resource = relationship("Resource", back_populates="files")
