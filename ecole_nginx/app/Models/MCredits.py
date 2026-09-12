# app/Models/MCredits.py — système à crédits (niveau "Universitaire" uniquement)
"""Sous-système indépendant du flux "par année" existant (CoursEtudiant, blob
JSON clé par nom de cours) : les prérequis et le cumul de crédits ont besoin
de requêtes indexées fiables (a-t-on déjà validé le cours X ? combien de
crédits obtenus au total ?), ce qu'un blob JSON clé-par-nom ne permet pas de
faire correctement. Ces tables restent donc relationnelles avec de vraies
FK, en parallèle du système existant — ne remplace ni ne migre CoursEtudiant."""

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
from app.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class CoursPrerequis(Base):
    """Prérequis global par Cours (pas par Programme — un prérequis est un
    fait de curriculum, indépendant du professeur/session/année qui
    dispense une offre donnée). Scopé au niveau via Cours.niveau_id, déjà
    existant, sans colonne supplémentaire."""
    __tablename__ = "cours_prerequis"
    __table_args__ = (
        UniqueConstraint('cours_id', 'prerequis_cours_id', name='uq_cours_prerequis'),
        {
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB'
        }
    )
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    cours_id = Column(CHAR(36), ForeignKey("cours.id"), nullable=False)
    prerequis_cours_id = Column(CHAR(36), ForeignKey("cours.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    cours = relationship("Cours", foreign_keys=[cours_id])
    prerequis = relationship("Cours", foreign_keys=[prerequis_cours_id])


class CoursInscription(Base):
    """Inscription/complétion d'un étudiant à un cours du système à crédits
    — un enregistrement relationnel par (étudiant, cours, année académique),
    distinct du blob JSON CoursEtudiant du système par année (voir docstring
    du module). `credits` est un instantané pris à l'inscription (même
    principe que le snapshot de coefficients dans RNotes.py::store_note),
    pas une valeur recalculée depuis Cours/Programme à chaque lecture."""
    __tablename__ = "cours_inscriptions"
    __table_args__ = (
        UniqueConstraint('etudiant_id', 'cours_id', 'annee_academique_id', name='uq_cours_inscription'),
        {
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB'
        }
    )
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    cours_id = Column(CHAR(36), ForeignKey("cours.id"), nullable=False)
    # Offre spécifique (professeur/session/classe) suivie — traçabilité
    # seulement, jamais utilisé pour la logique de prérequis/crédits
    # (celle-ci ne regarde que cours_id + statut).
    programme_id = Column(CHAR(36), ForeignKey("programmes.id"), nullable=True)
    annee_academique_id = Column(CHAR(36), ForeignKey("annee_academiques.id"), nullable=False)
    # Snapshot pour le gating (voir require_universitaire_actif) sans avoir
    # à rejoindre Cours→Niveau à chaque lecture.
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False)
    credits = Column(Numeric(4, 1), nullable=False)
    # Note de la phase Intra (manuel + contribution devoirs déjà additionnés
    # côté frontend, voir NoteForm.vue::totalNote côté système bloc, même
    # principe ici) — voir RCredits.py::saisir_note_credits.
    note_intra = Column(Numeric(5, 2), nullable=True)
    # Note de la phase Final (même principe que note_intra). Final exige
    # que note_intra existe déjà (voir saisir_note_credits), comme
    # RNotes.py::store_note CAS 2 pour le système bloc.
    note_finale = Column(Numeric(5, 2), nullable=True)
    # Note combinée (note_intra pondérée par Cours.poids_intra_percent +
    # note_finale) — c'est CE champ qui pilote statut/credits_obtenus/GPA,
    # pas note_finale seule (qui n'est que la note de la phase Final).
    note_globale = Column(Numeric(5, 2), nullable=True)
    credits_obtenus = Column(Numeric(4, 1), nullable=True)
    # en_cours / valide / echoue / abandonne
    statut = Column(String(20), nullable=False, default="en_cours")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    etudiant = relationship("Etudiant", back_populates="cours_inscriptions")
    cours = relationship("Cours")
    programme = relationship("Programme")
    annee_academique = relationship("AnneeAcademique")
    niveau = relationship("Niveau")
