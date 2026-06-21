# app/models/models.py
from sqlalchemy import Column, String, Date, Boolean, DateTime, Integer, Numeric, Text, JSON, Enum, ForeignKey,desc,asc
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime, date
from app.database import Base 
import uuid
from sqlalchemy.dialects.mysql import LONGTEXT
from app.Models.observable import ObservableMixin

def generate_uuid():
    return str(uuid.uuid4())

# ============= MODELS DE BASE =============

class AnneeAcademique(Base):
    __tablename__ = "annee_academiques"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    niveau_detude = Column(String(255), nullable=False)
    annee_academique = Column(String(255), nullable=False, unique=True)
    status = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    classes_etudiants = relationship("ClasseEtudiant", back_populates="annee_academiques")
    etudiant_facultes = relationship("EtudiantFaculte", back_populates="annee_academiques")
    frais_inscriptions = relationship("FraisInscription", back_populates="annee_academique")
    frais_divers = relationship("FraisDivers", back_populates="annee_academique")
    params_exams = relationship("ParamExam", back_populates="annee_academique")
    presences = relationship("Presence", back_populates="annee_academique")

class Niveau(Base):
    __tablename__ = "niveaux"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    classes = relationship("Classe", back_populates="niveau")
    classes_etudiants = relationship("ClasseEtudiant", back_populates="niveaux")
    cours = relationship("Cours", back_populates="niveau")
    etudiant_facultes = relationship("EtudiantFaculte", back_populates="niveaux")
    frais_inscriptions = relationship("FraisInscription", back_populates="niveau")
    frais_divers = relationship("FraisDivers", back_populates="niveau")
    parametre_paiements = relationship("ParametrePaiement", back_populates="niveau")
    params_exams = relationship("ParamExam", back_populates="niveau")
    programmes = relationship("Programme", back_populates="niveau")
    paiement = relationship("Paiement", back_populates="niveau_ref")
    # paiement = relationship("Paiement", back_populates="niveau")

class Faculte(Base):
    __tablename__ = "facultes"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom = Column(String(255), nullable=False)
    nb_annee = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    etudiant_facultes = relationship("EtudiantFaculte", back_populates="faculte")
    classe_facultes = relationship("ClasseFaculte", back_populates="faculte")
    parametre_paiements = relationship("ParametrePaiement", back_populates="faculte")
    programmes = relationship("Programme", back_populates="faculte")

class Classe(Base, ObservableMixin):
    __tablename__ = "classes"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"), nullable=False)
    nom_classe = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    niveau = relationship("Niveau", back_populates="classes")
    classe_facultes = relationship("ClasseFaculte", back_populates="classe")
    classes_etudiants = relationship("ClasseEtudiant", back_populates="classes")
    etudiant_facultes = relationship("EtudiantFaculte", back_populates="classes")
    presences = relationship("Presence", back_populates="classe")

    paiement = relationship("Paiement", back_populates="classe_ref")

class Etudiant(Base, ObservableMixin):
    __tablename__ = "etudiants"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid, nullable=False)
    identifiant = Column(String(255), nullable=False, unique=True)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    sexe = Column(String(255), nullable=False)
    date_de_naissance = Column(String(255), nullable=False)
    telephone = Column(String(255))
    email = Column(String(255), unique=True, nullable=True)
    adresse = Column(String(255), nullable=False)
    religion = Column(String(255))
    lieu_de_naissance = Column(String(255))
    code = Column(String(255))
    aide_financiere = Column(String(255), nullable=False, default="Aucune")
    nisu = Column(String(255))
    dernier_etablissement = Column(String(255))

    photo_base64 = Column(LONGTEXT, nullable=True) # Pour stocker la chaîne Base64
    photo_path = Column(String(255), nullable=True) # Pour le chemin (ex: /uploads/photo1.jpg)

    delete_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship(
        "User",
        primaryjoin="and_(Etudiant.id==foreign(User.userable_id), User.userable_type=='App\\\\Models\\\\Etudiant')",
        uselist=False,
        viewonly=True  # <-- important, pour éviter conflit de direction
    )
    # classes_etudiant = relationship("ClasseEtudiant", back_populates="etudiant",  lazy="selectin")
    classes_etudiant = relationship(
        "ClasseEtudiant",
        back_populates="etudiant",
        lazy="selectin",
        #order_by=asc("created_at")  # refers to the related table's column
        order_by="ClasseEtudiant.created_at.asc()" 
    )

    # etudiant_facultes = relationship(
    #     "EtudiantFaculte",
    #     back_populates="etudiant",
    #     lazy="selectin",
    #     order_by=asc("created_at")
    #     # order_by=desc("created_at")
    # )
    etudiant_facultes = relationship(
    "EtudiantFaculte",
    back_populates="etudiant",
    lazy="selectin",
    order_by="EtudiantFaculte.created_at.asc()"  # string expression SQLAlchemy evaluates lazily
)
    # order_by=asc(RelatedModel.created_at)
    cours_etudiants = relationship("CoursEtudiant", back_populates="etudiant")
    # etudiant_facultes = relationship("EtudiantFaculte", back_populates="etudiant", lazy="selectin")
    notes = relationship("Note", back_populates="etudiant")
    paiements = relationship("Paiement", back_populates="etudiant")
    pieces_soumises = relationship("PieceSoumise", back_populates="etudiant")
    presences = relationship("Presence", back_populates="etudiant")
    responsable = relationship("Responsable", back_populates="etudiant", uselist=False)
    ventes = relationship("Vente", back_populates="etudiant")
    paiement_statuts = relationship("PaiementStatut", back_populates="etudiant")

class Cours(Base, ObservableMixin):
    __tablename__ = "cours"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    cours_nom = Column(String(255), nullable=False)
    note_de_passage = Column(String(255))
    coefficients = Column(String(255))
    niveau_id = Column(CHAR(36), ForeignKey("niveaux.id"))
    type_matiere = Column(String(255), nullable=False, default="base")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    niveau = relationship("Niveau", back_populates="cours")
    notes = relationship("Note", back_populates="cours")
    programmes = relationship("Programme", back_populates="cours")

class Professeur(Base, ObservableMixin):
    __tablename__ = "professeurs"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    sexe = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telephone = Column(String(255), nullable=False)
    adresse = Column(String(255), nullable=False)
    matiere_enseignee = Column(String(255))
    status = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    # user = relationship(
    #     "User",
    #     primaryjoin="and_(Professeur.id==foreign(User.userable_id), User.userable_type=='professeur')",
    #     uselist=False,
    #     back_populates="professeur"
    # )
    user = relationship(
        "User",
        primaryjoin="and_(Professeur.id==foreign(User.userable_id), User.userable_type=='App\\\\Models\\\\Professeur')",
        uselist=False,
        viewonly=True  # <-- important, pour éviter conflit de direction
    )
    programmes = relationship("Programme", back_populates="professeur")

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    token = Column(String(500), unique=True, index=True) 
    expires_at = Column(DateTime)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)

class User(Base, ObservableMixin):
    __tablename__ = "users"
    __table_args__ = {
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_charset': 'utf8mb4',
         'mysql_engine':'InnoDB'
    }
    
    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(255), nullable=True,index=True, unique=True)
    email_verified_at = Column(DateTime)
    password = Column(String(255), nullable=False)
    two_factor_secret = Column(Text)
    two_factor_recovery_codes = Column(Text)
    two_factor_confirmed_at = Column(DateTime)
    remember_token = Column(String(100))
    current_team_id = Column(Integer)
    profile_photo_path = Column(String(2048))
    status = Column(String(255), nullable=False, default="1")
    userable_type = Column(String(255), nullable=False)
    userable_id = Column(CHAR(36), nullable=False)
    password_changed_at = Column(DateTime)
    client_info = Column(JSON)
    client_infos = Column(String(255))
    code_pin = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    depenses = relationship("Depense", back_populates="user")
    heart_autos = relationship("HeartAuto", back_populates="user")
    loans = relationship("Loan", back_populates="user", foreign_keys="Loan.user_id")
    loans_approved = relationship("Loan", back_populates="approver", foreign_keys="Loan.approved_by")
    log_actives = relationship("LogActive", back_populates="user")
    order_items = relationship("OrderItem", back_populates="user")
    ventes = relationship("Vente", back_populates="user")

    
    # other_transaction = relationship("OtherTransaction", back_populates="user")
    other_transactions = relationship(
        "OtherTransaction", 
        back_populates="user",
        foreign_keys="[OtherTransaction.user_id]"
    )

    etudiant = relationship(
        "Etudiant",
        primaryjoin="and_(User.userable_id==foreign(Etudiant.id), User.userable_type=='App\\\\Models\\\\Etudiant')",
        uselist=False
    )

    professeur = relationship(
        "Professeur",
        primaryjoin="and_(User.userable_id==foreign(Professeur.id), User.userable_type=='App\\\\Models\\\\Professeur')",
        uselist=False
    )

    personnel = relationship(
        "Personnel",
        primaryjoin="and_(User.userable_id==foreign(Personnel.id), User.userable_type=='App\\\\Models\\\\Personnel')",
        uselist=False
    )

    # roles = relationship("ModelHasRole", back_populates="user")
    # permission = relationship("PermissionHasRole", back_populates="user")

    heart_autos =relationship("HeartAuto", back_populates="user")

    roles = relationship(
        "Role",
        secondary="model_has_roles",
        primaryjoin="User.id == model_has_roles.c.model_id",
        secondaryjoin="Role.id == model_has_roles.c.role_id",
        back_populates="user",
        lazy="selectin"
    )
    
    permissions = relationship(
        "Permission",
        secondary="model_has_permissions",
        primaryjoin="User.id == model_has_permissions.c.model_id",
        secondaryjoin="Permission.id == model_has_permissions.c.permission_id",
        back_populates="user",
        lazy="selectin"
    )