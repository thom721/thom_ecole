# app/models/financial.py
from sqlalchemy import Column, String, Date, Boolean, DateTime, Integer, Numeric, Text, JSON, Enum as SQLEnum, ForeignKey , UniqueConstraint 
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.dialects.mysql import DATETIME as MySQLDateTime
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

class AnnulationArriere(Base, ObservableMixin):
    """Dérogation manuelle (réversible) au blocage d'arriéré de l'année
    précédente (voir RSavePaiement.py:_check_arrears_previous_year) — ne
    modifie jamais Paiement.paiement_details, l'historique réel des
    versements reste intact ; seule l'existence d'une ligne active ici
    lève le blocage pour ce couple étudiant/année."""
    __tablename__ = "annulations_arriere"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    etudiant_id = Column(CHAR(36), ForeignKey("etudiants.id"), nullable=False)
    annee_academique_id = Column(CHAR(36), ForeignKey("annee_academiques.id"), nullable=False)
    annee_academique = Column(String(255), nullable=False)
    type_annulation = Column(String(20), nullable=False)  # 'partiel' | 'total'
    montant_annule = Column(Numeric(10, 2), nullable=False)
    ordonne_par = Column(String(255), nullable=False)
    ordonne_par_fonction = Column(String(255), nullable=False)
    executant_user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    executant_nom = Column(String(255), nullable=False)
    executant_role = Column(String(255), nullable=True)
    raison = Column(String(255), nullable=False)
    contrat_accepte = Column(Boolean, nullable=False, default=False)
    statut = Column(String(20), nullable=False, default="actif")  # 'actif' | 'annule'
    annule_le = Column(DateTime, nullable=True)
    annule_par_user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    annule_raison = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    etudiant = relationship("Etudiant")
    annee_academique_ref = relationship("AnneeAcademique")
    executant = relationship("User", foreign_keys=[executant_user_id])
    annule_par = relationship("User", foreign_keys=[annule_par_user_id])

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

class ParametrePayroll(Base, ObservableMixin):
    """Taux horaire par cours et par année académique pour les professeurs
    payés à l'heure (Professeur.type_paiement == 'horaire') — table séparée
    (plutôt qu'un taux unique sur Professeur) pour garder l'historique
    quand le taux d'un cours change d'une année à l'autre."""
    __tablename__ = "parametre_payrolls"
    __table_args__ = (
        UniqueConstraint('cours_id', 'annee_academique', name='uq_parametre_payroll_cours_annee'),
        {
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_charset': 'utf8mb4',
            'mysql_engine': 'InnoDB'
        }
    )

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    cours_id = Column(CHAR(36), ForeignKey("cours.id"), nullable=False)
    taux_horaire = Column(Numeric(10, 2), nullable=False)
    annee_academique = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    cours = relationship("Cours")

class SalaireHistorique(Base):
    """Journal des changements de salaire_fixe (Professeur ou Personnel) —
    table dédiée plutôt que l'audit générique (ObservableMixin/Log) : ce
    dernier n'est pas branché pour Personnel et loggerait tous les champs
    (nom, email...), pas seulement le salaire, ce qui compliquerait un
    rapport "état des augmentations" pour une période. Une ligne par
    changement effectif de valeur (pas de ligne si la valeur ne change pas)."""
    __tablename__ = "salaire_historiques"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    employe_type = Column(String(20), nullable=False)  # 'professeur' | 'personnel'
    employe_id = Column(CHAR(36), nullable=False)  # Professeur.id ou Personnel.id
    ancien_montant = Column(Numeric(10, 2), nullable=True)
    nouveau_montant = Column(Numeric(10, 2), nullable=False)
    modifie_par = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    # Précision microseconde : deux changements faits dans la même seconde
    # doivent rester triables de façon fiable pour le rapport chronologique.
    created_at = Column(MySQLDateTime(fsp=6), default=datetime.utcnow)

class Payroll(Base, ObservableMixin):
    """Versements de salaire à un Professeur/Personnel — pas de référence
    bureau/web, fonctionnalité absente des deux, ajoutée sur demande
    explicite. Deux modes (`type_calcul`) :
    - 'fixe' : montant_du saisi/pré-rempli depuis Professeur.salaire_fixe.
    - 'horaire' : montant_du = Σ heures × taux (ParametrePayroll), détail
      figé dans `details_horaires` pour garder l'historique même si le
      taux change ensuite.
    Chaque ligne représente une PÉRIODE (mois/année) à payer, pas un
    versement — les versements réels sont dans PayrollVersement (mirror de
    Loan/LoanRepayment) ; `montant`/`remaining_balance` sont le total dû et
    le solde restant, `statut` bascule En attente → Partiel → Payé au fil
    des versements."""
    __tablename__ = "payrolls"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    montant = Column(Numeric(10, 2), nullable=False)
    mois = Column(String(20), nullable=False)
    annee = Column(String(4), nullable=False)
    methode_paiement = Column(String(20), nullable=False, default="Espèce")
    statut = Column(String(20), nullable=False, default="En attente")
    date_versement = Column(DateTime, nullable=True)
    type_calcul = Column(String(20), nullable=False, default="fixe")
    montant_du = Column(Numeric(10, 2), nullable=True)
    remaining_balance = Column(Numeric(10, 2), nullable=True)
    details_horaires = Column(JSON, nullable=True)
    heures_pointees_ref = Column(Numeric(8, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="payrolls")
    versements = relationship("PayrollVersement", back_populates="payroll")

class PayrollVersement(Base, ObservableMixin):
    """Versement partiel ou intégral contre un Payroll — mirror exact de
    LoanRepayment, mêmes garanties de précision Decimal côté route."""
    __tablename__ = "payroll_versements"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    payroll_id = Column(CHAR(36), ForeignKey("payrolls.id"), nullable=False)
    montant = Column(Numeric(10, 2), nullable=False)
    date_versement = Column(Date, nullable=False)
    methode_paiement = Column(String(255))
    note = Column(Text)
    collected_by = Column(CHAR(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    payroll = relationship("Payroll", back_populates="versements")

class CategorieProduit(Base, ObservableMixin):
    """Catégories de produits gérées par l'utilisateur — distinctes de
    `categories` (app/Models/MRelations.py:Category), qui sert au domaine
    Communauté (news/events) et n'a aucun rapport avec les produits."""
    __tablename__ = "categories_produits"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Produit(Base, ObservableMixin):
    __tablename__ = "produits"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    prix = Column(Numeric(8, 2), nullable=False)
    quantite_stock = Column(Numeric(10, 2), nullable=False, default=0)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    order_items = relationship("OrderItem", back_populates="produit")

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
    produit_id = Column(CHAR(36), ForeignKey("produits.id"), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="order_items")
    vente = relationship("Vente", back_populates="order_items")
    produit = relationship("Produit", back_populates="order_items")

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