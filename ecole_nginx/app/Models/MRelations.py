# app/models/relations.py
from sqlalchemy import Column, String, Date, Boolean, DateTime, Integer, Numeric, Text, JSON, ForeignKey,Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
import enum
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# ============= TABLES DE RELATIONS ET ASSOCIATIONS =============

class ClasseFaculte(Base):
    __tablename__ = "classe_facultes"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    classes_id = Column(CHAR(36), ForeignKey("classes.id"), nullable=False)
    faculte_id = Column(CHAR(36), ForeignKey("facultes.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    classe = relationship("Classe", back_populates="classe_facultes")
    faculte = relationship("Faculte", back_populates="classe_facultes")

class ClasseEtudiant(Base):
    __tablename__ = "classes_etudiants"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    classes_id = Column(CHAR(36), ForeignKey("classes.id"), nullable=False)
    annee_academique_id = Column(CHAR(36), ForeignKey("annee_academiques.id"), nullable=False)
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"))
    status = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="classes_etudiant")
    classes = relationship("Classe", back_populates="classes_etudiants")
    annee_academiques = relationship("AnneeAcademique", back_populates="classes_etudiants")
    niveaux = relationship("Niveau", back_populates="classes_etudiants")

class EtudiantFaculte(Base):
    __tablename__ = "etudiant_facultes"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    faculte_id = Column(CHAR(36), ForeignKey("facultes.id"), nullable=False)
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False)
    classes_id = Column(CHAR(36), ForeignKey("classes.id"), nullable=False)
    annee_academique_id = Column(CHAR(36), ForeignKey("annee_academiques.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="etudiant_facultes")
    faculte = relationship("Faculte", back_populates="etudiant_facultes")
    niveaux = relationship("Niveau", back_populates="etudiant_facultes")
    classes = relationship("Classe", back_populates="etudiant_facultes")
    annee_academiques = relationship("AnneeAcademique", back_populates="etudiant_facultes")

class CoursEtudiant(Base):
    __tablename__ = "cours_etudiants"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }   
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    identifiant = Column(String(255))
    annee_academique = Column(String(255), nullable=False)
    niveau = Column(String(255), nullable=False)
    faculte = Column(String(255))
    classe = Column(String(255), nullable=False)
    data_etudiant = Column(JSON, nullable=False)
    code = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="cours_etudiants")

class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    annee_academique = Column(String(255), nullable=False)
    annee_detude = Column(String(255), nullable=False)
    niveau_detude = Column(String(255), nullable=False)
    matiere = Column(String(255), nullable=False)
    note = Column(Numeric(10, 2), nullable=False)
    section = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    cours_id = Column(CHAR(36), ForeignKey("cours.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="notes")
    cours = relationship("Cours", back_populates="notes")

class Presence(Base):
    __tablename__ = "presences"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    classes_id = Column(CHAR(36), ForeignKey("classes.id"), nullable=False)
    annee_academique_id = Column(CHAR(36), ForeignKey("annee_academiques.id"), nullable=False)
    date_daujourdhui = Column(DateTime, nullable=False)
    valeur = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="presences")
    classe = relationship("Classe", back_populates="presences")
    annee_academique = relationship("AnneeAcademique", back_populates="presences")

class Pointage(Base):
    """Pointage (heure d'arrivée/départ) du personnel (Professeur ou
    Personnel, via User) — une ligne par personne par jour, saisie par
    l'admin/réception (pas de self-service), sert de source d'heures
    fiable pour le payroll horaire (voir MFinancials.py:Payroll)."""
    __tablename__ = "pointages"
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_pointage_user_date'),
        {
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB'
        }
    )

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    heure_arrivee = Column(DateTime, nullable=True)
    heure_depart = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user = relationship("User")

class Programme(Base):
    __tablename__ = "programmes"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    professeur_id = Column(CHAR(36), ForeignKey("professeurs.id"), nullable=False)
    Cours_id = Column(CHAR(36), ForeignKey("cours.id"), nullable=False)
    Faculte_id = Column(CHAR(36), ForeignKey("facultes.id"))
    class_ = Column("class", String(255))
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False)
    session = Column(String(255))
    heure = Column(String(255))
    annee_academique = Column(String(255), nullable=False)
    jours = Column(String(255))
    coefficients = Column(String(255))
    note_de_passage = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    professeur = relationship("Professeur", back_populates="programmes")
    cours = relationship("Cours", back_populates="programmes")
    faculte = relationship("Faculte", back_populates="programmes")
    niveau = relationship("Niveau", back_populates="programmes")

class Responsable(Base):
    __tablename__ = "responsables"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom_responsable = Column(String(255), nullable=False)
    prenom_responsable = Column(String(255), nullable=False)
    email_responsable = Column(String(255))
    relation_responsable = Column(String(255))
    sexe_responsable = Column(String(255))
    telephone_responsable = Column(String(255))
    metier_responsable = Column(String(255))
    adresse_responsable = Column(String(255), nullable=False)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="responsable")

class PieceSoumise(Base):
    __tablename__ = "pieces_soumises"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    type_de_document = Column(String(255))
    document_numero = Column(String(255), nullable=True)
    document_date_dexpiration = Column(String(255), nullable=True)
    document_status = Column(String(255), nullable=True)
    document_image = Column(String(255), nullable=True)
    document_image_base64 = Column(LONGTEXT, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="pieces_soumises")

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }  

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AudienceType(str, enum.Enum):
    public      = "public"
    classe      = "classe"
    professeurs = "professeurs"

class Event(Base):
    __tablename__ = "events"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }  

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(255), nullable=False)
    description  = Column(Text)
    location     = Column(String(255))
    start_date   = Column(DateTime, nullable=False)
    end_date     = Column(DateTime, nullable=True)
    image_url    = Column(String(500), nullable=True)
    audience     = Column(Enum(AudienceType), default=AudienceType.public)
    is_published = Column(Boolean, default=False)
    category_id  = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category")


class News(Base):
    __tablename__ = "news"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    } 

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(255), nullable=False)
    content      = Column(Text)
    image_url    = Column(String(500), nullable=True)
    audience     = Column(Enum(AudienceType), default=AudienceType.public)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    category_id  = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category")


class Video(Base):
    __tablename__ = "videos"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }

    id           = Column(CHAR(36), primary_key=True, default=generate_uuid)
    titre        = Column(String(255), nullable=False)
    source       = Column(String(255), nullable=True)   # ex: "RTCH NEWS"
    youtube_url  = Column(String(500), nullable=False)
    is_published = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)