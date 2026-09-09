from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MCourse import Section
from app.Models.MGlossary import Glossary, GlossaryEntry
from app.Models.MEnrollment import CourseRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SGlossary import (
    GlossaryCreate, GlossaryUpdate, GlossaryOut, GlossaryDetailOut,
    GlossaryEntryCreate, GlossaryEntryUpdate, GlossaryEntryOut, GlossaryConceptOut,
)
from app.dependencies.auth import get_current_active_user, get_enrollment_or_none, assert_course_role

router = APIRouter(tags=["glossaries"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]


def _get_section_or_404(db: Session, section_id: str) -> Section:
    section = db.query(Section).filter(Section.id == section_id).first()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section introuvable")
    return section


def _get_glossary_and_course(db: Session, glossary_id: str) -> tuple[Glossary, str]:
    glossary = db.query(Glossary).filter(Glossary.id == glossary_id).first()
    if glossary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Glossaire introuvable")
    section = db.query(Section).filter(Section.id == glossary.section_id).first()
    return glossary, section.course_id


def _get_entry_and_course(db: Session, entry_id: str) -> tuple[GlossaryEntry, str]:
    entry = db.query(GlossaryEntry).filter(GlossaryEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrée introuvable")
    _glossary, course_id = _get_glossary_and_course(db, entry.glossary_id)
    return entry, course_id


def _demote_existing_main_glossary(db: Session, course_id: str, except_id: str | None) -> None:
    """Un seul glossaire principal par COURS (pas par section) — même
    comportement que le vrai Moodle : en activer un nouveau démote
    automatiquement l'ancien."""
    others = (
        db.query(Glossary)
        .join(Section, Glossary.section_id == Section.id)
        .filter(Section.course_id == course_id, Glossary.is_main.is_(True))
    )
    if except_id:
        others = others.filter(Glossary.id != except_id)
    for g in others.all():
        g.is_main = False


@router.post("/sections/{section_id}/glossaries", response_model=GlossaryOut, status_code=status.HTTP_201_CREATED)
def create_glossary(
    section_id: str, data: GlossaryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    section = _get_section_or_404(db, section_id)
    assert_course_role(db, current_user, section.course_id, _TEACHING_ROLES)

    if data.is_main:
        _demote_existing_main_glossary(db, section.course_id, except_id=None)

    glossary = Glossary(section_id=section_id, **data.model_dump())
    db.add(glossary)
    db.commit()
    db.refresh(glossary)
    return glossary


@router.get("/glossaries/{glossary_id}", response_model=GlossaryDetailOut)
def get_glossary(
    glossary_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    glossary, course_id = _get_glossary_and_course(db, glossary_id)
    is_teaching = current_user.system_role == SystemRole.admin
    if not is_teaching:
        enrollment = get_enrollment_or_none(db, course_id, current_user.id)
        if enrollment is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
        is_teaching = enrollment.role_in_course in _TEACHING_ROLES

    entries = sorted(glossary.entries, key=lambda e: e.concept.lower())
    if not is_teaching:
        entries = [e for e in entries if e.is_approved or e.created_by == current_user.id]

    return GlossaryDetailOut(
        id=glossary.id, section_id=glossary.section_id, title=glossary.title, description=glossary.description,
        is_visible=glossary.is_visible, is_main=glossary.is_main, allow_student_entries=glossary.allow_student_entries,
        require_approval=glossary.require_approval, allow_duplicates=glossary.allow_duplicates,
        entries=[GlossaryEntryOut.model_validate(e) for e in entries],
    )


@router.patch("/glossaries/{glossary_id}", response_model=GlossaryOut)
def update_glossary(
    glossary_id: str, data: GlossaryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    glossary, course_id = _get_glossary_and_course(db, glossary_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    payload = data.model_dump(exclude_unset=True)
    if payload.get("is_main") is True:
        _demote_existing_main_glossary(db, course_id, except_id=glossary_id)

    for field, value in payload.items():
        setattr(glossary, field, value)

    db.commit()
    db.refresh(glossary)
    return glossary


@router.delete("/glossaries/{glossary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_glossary(
    glossary_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    glossary, course_id = _get_glossary_and_course(db, glossary_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    if db.query(GlossaryEntry).filter(GlossaryEntry.glossary_id == glossary_id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="Ce glossaire a déjà des entrées — suppression bloquée")
    db.delete(glossary)
    db.commit()


@router.post("/glossaries/{glossary_id}/entries", response_model=GlossaryEntryOut, status_code=status.HTTP_201_CREATED)
def create_entry(
    glossary_id: str, data: GlossaryEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    glossary, course_id = _get_glossary_and_course(db, glossary_id)
    enrollment = get_enrollment_or_none(db, course_id, current_user.id)
    is_teaching = current_user.system_role == SystemRole.admin or (
        enrollment is not None and enrollment.role_in_course in _TEACHING_ROLES
    )
    if not is_teaching:
        if enrollment is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
        if not glossary.allow_student_entries:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                 detail="Les étudiants ne peuvent pas ajouter d'entrée à ce glossaire")

    if not glossary.allow_duplicates:
        exists = any(e.concept.strip().lower() == data.concept.strip().lower() for e in glossary.entries)
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce concept existe déjà dans ce glossaire")

    entry = GlossaryEntry(
        glossary_id=glossary_id, concept=data.concept, definition=data.definition,
        created_by=current_user.id, is_approved=is_teaching or not glossary.require_approval,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/glossary-entries/{entry_id}", response_model=GlossaryEntryOut)
def get_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    entry, course_id = _get_entry_and_course(db, entry_id)
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")
    return entry


@router.patch("/glossary-entries/{entry_id}", response_model=GlossaryEntryOut)
def update_entry(
    entry_id: str, data: GlossaryEntryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    entry, course_id = _get_entry_and_course(db, entry_id)
    if entry.created_by != current_user.id:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/glossary-entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    entry, course_id = _get_entry_and_course(db, entry_id)
    if entry.created_by != current_user.id:
        assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    db.delete(entry)
    db.commit()


@router.patch("/glossary-entries/{entry_id}/approve", response_model=GlossaryEntryOut)
def approve_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    entry, course_id = _get_entry_and_course(db, entry_id)
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)
    entry.is_approved = True
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/courses/{course_id}/glossary/concepts", response_model=list[GlossaryConceptOut])
def list_course_concepts(
    course_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.system_role != SystemRole.admin:
        if get_enrollment_or_none(db, course_id, current_user.id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non inscrit à ce cours")

    entries = (
        db.query(GlossaryEntry)
        .join(Glossary, GlossaryEntry.glossary_id == Glossary.id)
        .join(Section, Glossary.section_id == Section.id)
        .filter(Section.course_id == course_id, GlossaryEntry.is_approved.is_(True))
        .all()
    )
    return [GlossaryConceptOut(entry_id=e.id, concept=e.concept) for e in entries]
