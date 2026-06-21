from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.database import Base

class Formation(Base):
    __tablename__ = "formations"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
        'mysql_engine': 'InnoDB'
    }

    id              = Column(Integer, primary_key=True, index=True)
    niveau          = Column(String(100), nullable=False)         # Préscolaire, Primaire…
    titre           = Column(String(255), nullable=False)
    duree           = Column(String(50),  nullable=True)          # "3 ans"
    couleur         = Column(String(20),  default='#3b82f6')      # hex color
    image_url       = Column(String(500), nullable=True)
    description     = Column(Text,        nullable=True)
    matieres        = Column(JSON,        default=list)           # ["Français", "Maths",…]
    nb_eleves_classe= Column(String(20),  nullable=True)          # "25"
    taux_reussite   = Column(String(20),  nullable=True)          # "98%"
    nb_debouches    = Column(String(20),  nullable=True)          # "15+"
    debouches       = Column(JSON,        default=list)           # ["…", "…"]
    niveau_id       = Column(String(36),  nullable=True)            # FK logique vers niveaux.id
    faculte_id      = Column(String(36),  nullable=True)            # renseigné si Universitaire
    ordre           = Column(Integer,     default=0)
    is_published    = Column(Boolean,     default=True)
    created_at      = Column(DateTime,    default=datetime.utcnow)
    updated_at      = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)
