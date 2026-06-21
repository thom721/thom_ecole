# app/models/financial.py
from sqlalchemy import Column, String, Date, Boolean, DateTime, Integer, Numeric, Text, JSON, Enum as SQLEnum, ForeignKey , UniqueConstraint 
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
# from app.database import Base
from app.database import Base
import uuid
import enum
from app.Models.observable import ObservableMixin

def generate_uuid():
    return str(uuid.uuid4())

# ============= MODELS FINANCIERS =============

class PaiementStatut(Base):
    __tablename__ = "paiement_statuts"
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id        = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    annee_id           = Column(CHAR(36), nullable=False)
    montant_mensuel    = Column(Numeric(10, 2), default=0)
    montant_verse      = Column(Numeric(10, 2), default=0)
    date_limite        = Column(Date, nullable=True)
    mois_accessibles   = Column(JSON, default=list)   # ["Septembre", "Octobre", ...]
    mois_bloques       = Column(JSON, default=list)   # ["Mars", "Avril", ...]
    created_at         = Column(DateTime, default=datetime.utcnow)
    updated_at         = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("etudiant_id", "annee_id", name="unique_etudiant_annee"),
        {
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB',
        },
    )

    # Relations
    etudiant = relationship("Etudiant", back_populates="paiement_statuts")

class OtherTransaction(Base,ObservableMixin):
    __tablename__ = 'other_transactions'
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    montant = Column(Numeric(8, 2), nullable=False)
    description = Column(String(500), nullable=False)
    description_supplementaire = Column(String(255), nullable=True)
    # identifiant = Column(String(100), nullable=True)
    identifiant = Column(String(100), ForeignKey("etudiants.id"), nullable=True)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    delete_by = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    delete_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # user = relationship("User", back_populates="other_transaction")
    user = relationship(
        "User", 
        back_populates="other_transactions", 
        foreign_keys=[user_id]
    )
    etudiant = relationship("Etudiant", backref="transactions_autres")
    # Relation pour celui qui a supprimé : on précise foreign_keys=[delete_by]
    deleter = relationship(
        "User", 
        foreign_keys=[delete_by]
    )

class Paiement(Base, ObservableMixin):
    __tablename__ = "paiements"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    annee_academique = Column(String(255), nullable=False)
    # classe = Column(CHAR(36), ForeignKey("classes.id"), nullable=False)
    classe = Column(
        CHAR(36),
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=True
    )
    faculte_id = Column(String(255))
    cours = Column(String(255))
    niveau_id =Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False) #Column(String(255), nullable=False)
    mois = Column(JSON, nullable=False)
    paiement_details = Column(JSON, nullable=False)

    # from sqlalchemy.ext.mutable import MutableDict
    # from sqlalchemy import JSON

    # paiement_details = Column(MutableDict.as_mutable(JSON))
    # mois = Column(MutableDict.as_mutable(JSON))

    last_paiement_key = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="paiements")
    niveau_ref = relationship("Niveau", back_populates="paiement")
    classe_ref = relationship("Classe", back_populates="paiement")

class ParametrePaiement(Base, ObservableMixin):
    __tablename__ = "parametre_paiements"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False)
    faculte_id = Column(CHAR(36), ForeignKey("facultes.id"))
    classe = Column(String(255), nullable=False)
    montant = Column(Numeric(10, 2))
    devise = Column(String(255), nullable=False)
    nb_echeance = Column(String(255), nullable=False)
    anneeAcademique = Column(String(255))
    echeance = Column(String(255), nullable=False)
    montant_par = Column(JSON, nullable=False)
    accessoires = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    niveau = relationship("Niveau", back_populates="parametre_paiements")
    faculte = relationship("Faculte", back_populates="parametre_paiements")

class FraisInscription(Base, ObservableMixin):
    __tablename__ = "frais_dinscriptions"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    prix = Column(Numeric(8, 2), nullable=False)
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False)
    anneeAc = Column(CHAR(36), ForeignKey("annee_academiques.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    niveau = relationship("Niveau", back_populates="frais_inscriptions")
    annee_academique = relationship("AnneeAcademique", back_populates="frais_inscriptions")

class FraisDivers(Base,ObservableMixin):
    __tablename__ = "frais_divers"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    anneeAc = Column(CHAR(36), ForeignKey("annee_academiques.id"), nullable=False)
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=True)
    description = Column(String(255), nullable=False)
    prix = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    annee_academique = relationship("AnneeAcademique", back_populates="frais_divers")
    niveau = relationship("Niveau", back_populates="frais_divers")

class Depense(Base, ObservableMixin):
    __tablename__ = "depenses"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    description = Column(String(255), nullable=False)
    prix = Column(Numeric(8, 2), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="depenses")

class LoanStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
    disbursed = "disbursed"
    paid = "paid"
    default = "default"

class Loan(Base, ObservableMixin):
    __tablename__ = "loans"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    term_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False, default=0.00)
    monthly_payment = Column(Numeric(12, 2))
    remaining_balance = Column(Numeric(12, 2))
    status = Column(SQLEnum(LoanStatus), nullable=False, default=LoanStatus.pending)
    approved_by = Column(CHAR(36), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    disbursed_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="loans", foreign_keys=[user_id])
    approver = relationship("User", back_populates="loans_approved", foreign_keys=[approved_by])
    repayments = relationship("LoanRepayment", back_populates="loan")

class LoanRepayment(Base):
    __tablename__ = "loan_repayments"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    loans_id = Column(CHAR(36), ForeignKey("loans.id"), nullable=False)
    paid_amount = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(255))
    note = Column(Text)
    collected_by = Column(CHAR(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    loan = relationship("Loan", back_populates="repayments")

class Vente(Base, ObservableMixin):
    __tablename__ = "ventes"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom = Column(String(255))
    category = Column(String(255))
    prix = Column(Numeric(8, 2))
    quantite = Column(String(255))
    total = Column(Numeric(8, 2))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    status = Column(String(255), nullable=False, default="En attente")
    order_itemId = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="ventes")
    etudiant = relationship("Etudiant", back_populates="ventes")
    order_items = relationship("OrderItem", back_populates="vente")

class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    prix = Column(Numeric(8, 2), nullable=False)
    quantite = Column(String(255), nullable=False)
    total = Column(Numeric(8, 2), nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    vente_id = Column(CHAR(36), ForeignKey("ventes.id"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="order_items")
    vente = relationship("Vente", back_populates="order_items")

class ParamExam(Base):
    __tablename__ = "params_exams"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False)
    annee_academique_id = Column(CHAR(36), ForeignKey("annee_academiques.id"), nullable=False)
    evaluation_par = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    niveau = relationship("Niveau", back_populates="params_exams")
    annee_academique = relationship("AnneeAcademique", back_populates="params_exams")