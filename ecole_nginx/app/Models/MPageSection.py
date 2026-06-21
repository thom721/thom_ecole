from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from datetime import datetime
from app.database import Base

class PageSection(Base):
    __tablename__ = "page_sections"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
        'mysql_engine':  'InnoDB'
    }

    id          = Column(Integer,     primary_key=True, index=True)
    page        = Column(String(50),  nullable=False, index=True)   # 'home'
    section_key = Column(String(50),  nullable=False)               # 'stats','cycles'…
    titre       = Column(String(255), nullable=True)
    sous_titre  = Column(String(255), nullable=True)
    description = Column(Text,        nullable=True)
    is_visible  = Column(Boolean,     default=True)
    ordre       = Column(Integer,     default=0)
    items       = Column(JSON,        default=list)                 # contenu de la section
    created_at  = Column(DateTime,    default=datetime.utcnow)
    updated_at  = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)
