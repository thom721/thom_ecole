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
    # Type de mise en page pour les sections génériques ajoutées via l'admin
    # (voir GenericSection.vue) : 'text_center', 'image_left', 'image_right',
    # 'image_banner', 'cards_grid', 'stats_row'. NULL pour les 6 sections
    # historiques de la page d'accueil (stats/cycles/features/activities/
    # testimonials/values), qui gardent leur propre rendu sur mesure.
    layout      = Column(String(50),  nullable=True)
    # Image unique de section (text_left/text_right/image_banner) — distincte
    # des images par item dans `items` (ex: cards_grid, activities).
    image_url   = Column(String(500), nullable=True)
    is_visible  = Column(Boolean,     default=True)
    ordre       = Column(Integer,     default=0)
    items       = Column(JSON,        default=list)                 # contenu de la section
    created_at  = Column(DateTime,    default=datetime.utcnow)
    updated_at  = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)
