from datetime import date

from pydantic import BaseModel


class EcoleNginxAnneeOut(BaseModel):
    id: str
    label: str
    date_debut: date
    date_fin: date
    status: bool


class EcoleNginxProgrammeOut(BaseModel):
    id: str
    cours_nom: str | None = None
    faculte_nom: str | None = None
    niveau_name: str | None = None
    classe_nom: str | None = None
    classe_id: str | None = None
    session: str | None = None
    heure: str | None = None
    jours: str | None = None
    coefficients: str | None = None
    note_de_passage: str | None = None
    professeur_nom: str | None = None
    professeur_prenom: str | None = None
    professeur_email: str | None = None
    professeur_login_email: str | None = None
    annee_academique_id: str
    annee_academique_label: str | None = None
    annee_date_debut: date | None = None
    annee_date_fin: date | None = None


class ImportResultOut(BaseModel):
    imported_count: int
    updated_count: int
    accounts_created: list[str] = []
    warnings: list[str] = []


class EcoleNginxClasseOut(BaseModel):
    id: str
    nom_classe: str
    niveau_name: str | None = None


class EcoleNginxEtudiantOut(BaseModel):
    etudiant_id: str
    identifiant: str
    code: str | None = None
    nom: str
    prenom: str
    email: str | None = None
    etudiant_login_email: str | None = None


class ActivateStudentIn(BaseModel):
    etudiant_id: str
    classe_id: str
    annee_academique_id: str
    email: str
    first_name: str
    last_name: str


class ActivateStudentOut(BaseModel):
    account_created: bool
    enrolled_courses: list[str] = []
    warnings: list[str] = []


class SyncCredentialsOut(BaseModel):
    accounts_created: list[str] = []
    skipped_existing: list[str] = []
    total_seen: int = 0


class EcoleNginxStaffCredentialOut(BaseModel):
    source_type: str
    source_id: str
    first_name: str
    last_name: str
    login_email: str
    password_hash: str
