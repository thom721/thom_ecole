from sqlalchemy.orm import Session
from app.Models.MPageSection import PageSection
from app.Schemas.SPageSection import PageSectionCreate, PageSectionUpdate
from typing import List

def get_page(db: Session, page: str, visible_only: bool = False) -> List[PageSection]:
    q = db.query(PageSection).filter(PageSection.page == page)
    if visible_only:
        q = q.filter(PageSection.is_visible == True)
    return q.order_by(PageSection.ordre, PageSection.id).all()

def get_by_id(db: Session, section_id: int):
    return db.query(PageSection).filter(PageSection.id == section_id).first()

def get_by_key(db: Session, page: str, key: str):
    return db.query(PageSection).filter(
        PageSection.page == page,
        PageSection.section_key == key
    ).first()

def upsert(db: Session, data: PageSectionCreate) -> PageSection:
    existing = get_by_key(db, data.page, data.section_key)
    if existing:
        for k, v in data.model_dump(exclude_none=True).items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    section = PageSection(**data.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    return section

def update(db: Session, section_id: int, data: PageSectionUpdate) -> PageSection | None:
    section = get_by_id(db, section_id)
    if not section:
        return None
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(section, k, v)
    db.commit()
    db.refresh(section)
    return section

def delete(db: Session, section_id: int) -> bool:
    section = get_by_id(db, section_id)
    if not section:
        return False
    db.delete(section)
    db.commit()
    return True

def toggle_visibility(db: Session, section_id: int) -> PageSection | None:
    section = get_by_id(db, section_id)
    if not section:
        return None
    section.is_visible = not section.is_visible
    db.commit()
    db.refresh(section)
    return section
