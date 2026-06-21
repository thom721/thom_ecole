from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.Schemas.SPageSection import PageSectionCreate, PageSectionUpdate, PageSectionResponse
from app.services import page_section_service
from app.dependencies.Dependencie import require_role
from app.Models.MModels import User

router = APIRouter(prefix="/api/v1/page-sections", tags=["Page Sections"])

# ── Public ────────────────────────────────────────────────────────────────
@router.get("/{page}", response_model=List[PageSectionResponse])
def get_page_sections(page: str, db: Session = Depends(get_db)):
    return page_section_service.get_page(db, page, visible_only=True)

@router.get("/{page}/all", response_model=List[PageSectionResponse])
def get_all_page_sections(
    page: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    return page_section_service.get_page(db, page, visible_only=False)

# ── Admin ─────────────────────────────────────────────────────────────────
@router.post("/", response_model=PageSectionResponse, status_code=201)
def upsert_section(
    data: PageSectionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    return page_section_service.upsert(db, data)

@router.put("/{section_id}", response_model=PageSectionResponse)
def update_section(
    section_id: int,
    data: PageSectionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    s = page_section_service.update(db, section_id, data)
    if not s:
        raise HTTPException(status_code=404, detail="Section introuvable")
    return s

@router.patch("/{section_id}/toggle", response_model=PageSectionResponse)
def toggle_section(
    section_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    s = page_section_service.toggle_visibility(db, section_id)
    if not s:
        raise HTTPException(status_code=404, detail="Section introuvable")
    return s

@router.delete("/{section_id}")
def delete_section(
    section_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    if not page_section_service.delete(db, section_id):
        raise HTTPException(status_code=404, detail="Section introuvable")
    return {"message": "Section supprimée"}
