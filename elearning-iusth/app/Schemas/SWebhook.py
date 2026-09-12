from pydantic import BaseModel

from app.Schemas.SIntegration import EcoleNginxProgrammeOut


class EnrollmentChangeIn(BaseModel):
    etudiant_id: str
    classes_id: str
    status: bool
    etudiant_login_email: str | None = None


class EnrollmentChangedIn(BaseModel):
    annee_academique_id: str
    changes: list[EnrollmentChangeIn]


# Même forme que EcoleNginxProgrammeOut (l'import complet, voir
# RIntegration.py::import_from_ecole_nginx) : ecole_nginx pousse maintenant
# la fiche complète du programme à chaque création/modification, pas
# seulement le professeur — voir RWebhooks.py::programme_changed, qui upserte
# le Course via le même helper que l'import (_upsert_course_from_programme).
ProgrammeChangeIn = EcoleNginxProgrammeOut


class ProgrammeChangedIn(BaseModel):
    annee_academique_id: str
    changes: list[ProgrammeChangeIn]


class ProgrammeDeletedIn(BaseModel):
    annee_academique_id: str
    programme_id: str


class WebhookAckOut(BaseModel):
    processed: int
    skipped: int


class DevoirGradeOut(BaseModel):
    email: str
    # Mélangé (toutes catégories confondues) — utilisé par le système à
    # crédits ecole_nginx (une seule note_finale, pas de split Intra/Final).
    note_devoirs: float | None
    # Calculés uniquement sur les catégories tagguées evaluation_phase
    # (voir plan Épic 24) — utilisés par le système bloc ecole_nginx
    # (Intra et Final sont deux notes cumulatives distinctes ; sans ce
    # split, la même contribution serait comptée deux fois).
    note_devoirs_intra: float | None = None
    note_devoirs_finale: float | None = None
