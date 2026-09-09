from pydantic import BaseModel


class EnrollmentChangeIn(BaseModel):
    etudiant_id: str
    classes_id: str
    status: bool
    etudiant_login_email: str | None = None


class EnrollmentChangedIn(BaseModel):
    annee_academique_id: str
    changes: list[EnrollmentChangeIn]


class ProgrammeChangeIn(BaseModel):
    programme_id: str
    professeur_id: str
    professeur_login_email: str | None = None


class ProgrammeChangedIn(BaseModel):
    annee_academique_id: str
    changes: list[ProgrammeChangeIn]


class WebhookAckOut(BaseModel):
    processed: int
    skipped: int
