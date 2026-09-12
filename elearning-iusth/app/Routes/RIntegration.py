import re
import secrets

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.Config import settings
from app.database import get_db
from app.Models.MCourse import CourseCategory, Course
from app.Models.MEnrollment import Enrollment, CourseRole, EnrollmentStatus
from app.Models.MUser import User, SystemRole
from app.Schemas.SIntegration import (
    EcoleNginxAnneeOut, EcoleNginxProgrammeOut, ImportResultOut,
    EcoleNginxClasseOut, EcoleNginxEtudiantOut, ActivateStudentIn, ActivateStudentOut,
    SyncCredentialsOut, EcoleNginxStaffCredentialOut,
)
from app.dependencies.auth import require_role, hash_password
from app.Helper.role_mapping import resolve_system_role

router = APIRouter(prefix="/integration/ecole-nginx", tags=["integration"],
                    dependencies=[Depends(require_role([SystemRole.admin]))])


def _client() -> httpx.Client:
    return httpx.Client(
        base_url=settings.ECOLE_NGINX_BASE_URL,
        headers={"X-Integration-Key": settings.ECOLE_NGINX_INTEGRATION_KEY},
        timeout=30.0,
    )


def _slugify(*parts: str) -> str:
    raw = "-".join(p for p in parts if p)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw).strip("-").lower()
    return slug[:90] or "cours"


@router.get("/annees-academiques", response_model=list[EcoleNginxAnneeOut])
def list_ecole_nginx_annees():
    try:
        with _client() as client:
            response = client.get("/integration/annees-academiques")
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"ecole_nginx injoignable : {e}")
    return response.json()


def _upsert_course_from_programme(
    db: Session,
    programme: EcoleNginxProgrammeOut,
    category_cache: dict[str, str],
    teacher_cache: dict[str, "User | None"],
    unmatched_courses_by_label: dict[str, list[str]],
) -> tuple[Course, bool, str | None]:
    """Crée ou met à jour le Course correspondant à `programme` (upsert par
    external_source/external_ref_id) + rapproche l'enseignant par email.
    Factorisé depuis import_from_ecole_nginx pour être réutilisé tel quel
    par RWebhooks.py::programme_changed (voir plan Épic 20) — même logique
    dans les deux cas (import complet ET push temps réel), pour ne jamais
    diverger entre les deux chemins.

    Renvoie (course, is_new, account_created_label) — account_created_label
    n'est pas None seulement si un compte professeur vient d'être
    auto-provisionné (voir settings.ECOLE_NGINX_AUTO_PROVISION_TEACHERS)."""
    account_created_label: str | None = None

    # Catégorie = faculté (créée si absente, recherchée par nom).
    category_id = None
    if programme.faculte_nom:
        if programme.faculte_nom in category_cache:
            category_id = category_cache[programme.faculte_nom]
        else:
            category = db.query(CourseCategory).filter(CourseCategory.name == programme.faculte_nom).first()
            if category is None:
                category = CourseCategory(
                    name=programme.faculte_nom,
                    slug=_slugify(programme.faculte_nom),
                )
                db.add(category)
                db.flush()
            category_id = category.id
            category_cache[programme.faculte_nom] = category_id

    full_name_parts = [programme.cours_nom or "Cours", programme.classe_nom, programme.annee_academique_label]
    full_name = " — ".join(p for p in full_name_parts if p)

    summary_lines = []
    if programme.professeur_nom or programme.professeur_prenom:
        summary_lines.append(f"Professeur : {programme.professeur_prenom or ''} {programme.professeur_nom or ''}".strip())
    if programme.niveau_name:
        summary_lines.append(f"Niveau : {programme.niveau_name}")
    if programme.jours or programme.heure:
        summary_lines.append(f"Horaire : {programme.jours or ''} {programme.heure or ''}".strip())
    summary = "\n".join(summary_lines) or None

    course = (
        db.query(Course)
        .filter(Course.external_source == "ecole_nginx", Course.external_ref_id == programme.id)
        .first()
    )
    is_new = course is None
    if course is None:
        short_name = _slugify(programme.cours_nom, programme.annee_academique_label, programme.classe_nom)
        # Évite une collision avec un cours déjà existant portant le même code.
        base_short_name, suffix = short_name, 1
        while db.query(Course).filter(Course.short_name == short_name).first() is not None:
            suffix += 1
            short_name = f"{base_short_name}-{suffix}"
        course = Course(
            external_source="ecole_nginx", external_ref_id=programme.id,
            short_name=short_name,
        )
        db.add(course)
    else:
        # Un programme réimporté/repoussé après suppression redevient visible
        # (voir RWebhooks.py::programme_deleted, qui met is_visible=False
        # plutôt que de supprimer le Course).
        course.is_visible = True

    course.full_name = full_name
    course.summary = summary
    course.category_id = category_id
    course.start_date = programme.annee_date_debut
    course.end_date = programme.annee_date_fin
    db.flush()

    # Rapprochement enseignant — dédoublonné par email sur tout l'appelant
    # (voir teacher_cache). Auto-création du compte SEULEMENT si
    # settings.ECOLE_NGINX_AUTO_PROVISION_TEACHERS est activé (voir
    # Config.py — désactivé par défaut, à activer explicitement par
    # établissement).
    teacher_email = programme.professeur_login_email or programme.professeur_email
    teacher_label = f"{programme.professeur_prenom or ''} {programme.professeur_nom or ''}".strip() or "professeur inconnu"

    if not teacher_email:
        unmatched_courses_by_label.setdefault(f"{teacher_label} (email inconnu)", []).append(full_name)
        return course, is_new, account_created_label

    if teacher_email in teacher_cache:
        teacher = teacher_cache[teacher_email]
    else:
        teacher = db.query(User).filter(User.email == teacher_email).first()
        if teacher is None and settings.ECOLE_NGINX_AUTO_PROVISION_TEACHERS:
            random_password = secrets.token_urlsafe(16)
            teacher = User(
                email=teacher_email,
                password_hash=hash_password(random_password),
                first_name=programme.professeur_prenom or "Professeur",
                last_name=programme.professeur_nom or "",
                system_role=SystemRole.teacher,
                must_change_password=True,
            )
            db.add(teacher)
            db.flush()
            account_created_label = f"{teacher_label} ({teacher_email})"
        teacher_cache[teacher_email] = teacher  # None mis en cache aussi : évite de re-requêter pour rien

    if teacher is None:
        unmatched_courses_by_label.setdefault(f"{teacher_label} ({teacher_email})", []).append(full_name)
        return course, is_new, account_created_label

    existing_enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course.id, Enrollment.user_id == teacher.id)
        .first()
    )
    if existing_enrollment is None:
        db.add(Enrollment(course_id=course.id, user_id=teacher.id,
                           role_in_course=CourseRole.teacher, status=EnrollmentStatus.active))

    return course, is_new, account_created_label


@router.post("/import", response_model=ImportResultOut)
def import_from_ecole_nginx(annee_academique_id: str, db: Session = Depends(get_db)):
    try:
        with _client() as client:
            response = client.get("/integration/programmes", params={"annee_academique_id": annee_academique_id})
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"ecole_nginx injoignable : {e}")

    programmes = [EcoleNginxProgrammeOut(**row) for row in response.json()]

    imported_count = 0
    updated_count = 0
    accounts_created: list[str] = []
    category_cache: dict[str, str] = {}
    # Dédoublonnage par professeur (voir plan) : un seul compte créé/
    # retrouvé même s'il apparaît sur plusieurs cours dans cet import.
    teacher_cache: dict[str, User | None] = {}
    # Professeurs non rapprochés (aucun email connu, OU compte absent et
    # provisionnement auto désactivé) — regroupés par professeur plutôt
    # qu'une ligne par cours.
    unmatched_courses_by_label: dict[str, list[str]] = {}

    for programme in programmes:
        _course, is_new, account_created_label = _upsert_course_from_programme(
            db, programme, category_cache, teacher_cache, unmatched_courses_by_label
        )
        if is_new:
            imported_count += 1
        else:
            updated_count += 1
        if account_created_label:
            accounts_created.append(account_created_label)

    warnings = [
        f"{label} : aucun compte elearning-iusth rapproché — cours concernés : " + ", ".join(courses)
        for label, courses in unmatched_courses_by_label.items()
    ]

    db.commit()
    return ImportResultOut(imported_count=imported_count, updated_count=updated_count,
                            accounts_created=accounts_created, warnings=warnings)


@router.get("/classes", response_model=list[EcoleNginxClasseOut])
def list_ecole_nginx_classes(annee_academique_id: str):
    try:
        with _client() as client:
            response = client.get("/integration/classes", params={"annee_academique_id": annee_academique_id})
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"ecole_nginx injoignable : {e}")
    return response.json()


@router.get("/classes/{classe_id}/students", response_model=list[EcoleNginxEtudiantOut])
def list_ecole_nginx_classe_students(classe_id: str, annee_academique_id: str):
    try:
        with _client() as client:
            response = client.get(f"/integration/classes/{classe_id}/students", params={"annee_academique_id": annee_academique_id})
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"ecole_nginx injoignable : {e}")
    return response.json()


def resolve_courses_for_classe(db: Session, classe_id: str, annee_academique_id: str) -> tuple[list[Course], list[str]]:
    """Cours elearning-iusth déjà importés correspondant à une classe
    ecole_nginx pour une année — factorisé pour être réutilisé à la fois
    par `activate_student` (Épic 19) et par le webhook de synchronisation
    (Épic 20). Renvoie (cours résolus, avertissements pour les programmes
    pas encore importés)."""
    try:
        with _client() as client:
            response = client.get("/integration/programmes", params={"annee_academique_id": annee_academique_id})
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"ecole_nginx injoignable : {e}")

    programmes = [p for p in (EcoleNginxProgrammeOut(**row) for row in response.json()) if p.classe_id == classe_id]

    courses: list[Course] = []
    warnings: list[str] = []
    for programme in programmes:
        course = (
            db.query(Course)
            .filter(Course.external_source == "ecole_nginx", Course.external_ref_id == programme.id)
            .first()
        )
        if course is None:
            warnings.append(f"{programme.cours_nom or 'cours'} pas encore importé — lancez l'import de cours pour cette année d'abord")
            continue
        courses.append(course)
    return courses, warnings


@router.post("/activate-student", response_model=ActivateStudentOut)
def activate_student(data: ActivateStudentIn, db: Session = Depends(get_db)):
    """Active un étudiant ecole_nginx dans elearning-iusth (voir plan
    Épic 19) : crée son compte si absent (même mécanisme que le
    provisionnement professeur — mot de passe aléatoire,
    must_change_password=True), puis l'inscrit aux cours déjà importés
    correspondant à sa classe/année réelle. Prérequis explicite : l'import
    de cours (POST .../import) doit avoir été fait pour cette année avant
    — sinon avertissement explicite par cours manquant, jamais un échec
    silencieux."""
    user = db.query(User).filter(User.email == data.email).first()
    account_created = False
    if user is None:
        random_password = secrets.token_urlsafe(16)
        user = User(
            email=data.email, password_hash=hash_password(random_password),
            first_name=data.first_name, last_name=data.last_name,
            system_role=SystemRole.student, must_change_password=True,
        )
        db.add(user)
        db.flush()
        account_created = True

    courses, warnings = resolve_courses_for_classe(db, data.classe_id, data.annee_academique_id)

    enrolled_courses: list[str] = []
    for course in courses:
        existing_enrollment = (
            db.query(Enrollment)
            .filter(Enrollment.course_id == course.id, Enrollment.user_id == user.id)
            .first()
        )
        if existing_enrollment is None:
            db.add(Enrollment(course_id=course.id, user_id=user.id,
                               role_in_course=CourseRole.student, status=EnrollmentStatus.active))
        elif existing_enrollment.status == EnrollmentStatus.suspended:
            existing_enrollment.status = EnrollmentStatus.active
        enrolled_courses.append(course.full_name)

    db.commit()
    return ActivateStudentOut(account_created=account_created, enrolled_courses=enrolled_courses, warnings=warnings)


@router.post("/sync-credentials", response_model=SyncCredentialsOut)
def sync_staff_credentials(db: Session = Depends(get_db)):
    """Épic 22 : copie le hash bcrypt (jamais un mot de passe en clair)
    des comptes Professeur/Personnel ecole_nginx déjà résolus, pour que le
    même mot de passe fonctionne des deux côtés. Un compte elearning-iusth
    déjà existant (retrouvé par email) n'est jamais touché — ni recréé, ni
    son mot de passe modifié — voir décision de périmètre 3 du plan."""
    try:
        with _client() as client:
            response = client.get("/integration/staff-credentials")
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"ecole_nginx injoignable : {e}")

    entries = [EcoleNginxStaffCredentialOut(**row) for row in response.json()]

    accounts_created: list[str] = []
    skipped_existing: list[str] = []
    for entry in entries:
        existing = db.query(User).filter(User.email == entry.login_email).first()
        if existing is not None:
            skipped_existing.append(entry.login_email)
            continue
        db.add(User(
            email=entry.login_email, password_hash=entry.password_hash,
            first_name=entry.first_name or entry.source_type, last_name=entry.last_name or "",
            system_role=resolve_system_role(entry.source_type, entry.role_names), must_change_password=False,
        ))
        accounts_created.append(entry.login_email)

    db.commit()
    return SyncCredentialsOut(accounts_created=accounts_created, skipped_existing=skipped_existing, total_seen=len(entries))
