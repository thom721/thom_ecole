from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.Schemas.SPageSection import PageSectionCreate, PageSectionUpdate, PageSectionResponse
from app.services import page_section_service
from app.dependencies.Dependencie import require_role
from app.Models.MModels import User
from app.Helper.persistent_storage import PAGE_SECTIONS_DIR
import os, shutil, uuid

router = APIRouter(prefix="/api/v1/page-sections", tags=["Page Sections"])
UPLOAD_DIR = str(PAGE_SECTIONS_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

@router.post("/upload-image")
def upload_image(
    file: UploadFile = File(...),
    _: User = Depends(require_role(['admin']))
):
    """Upload générique pour une image d'item de section (ex: activities) —
    l'image ne vit pas dans une colonne dédiée comme Formation.image_url,
    mais dans le JSON `items` de la section, donc pas d'id de ligne à
    associer ici : on renvoie juste l'URL, le frontend la stocke dans le
    bon item avant d'enregistrer (voir saveItem() dans HomeView.vue)."""
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    disk_path = os.path.join(UPLOAD_DIR, filename)
    with open(disk_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"image_url": f"/static/uploads/page_sections/{filename}"}

@router.delete("/{section_id}")
def delete_section(
    section_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    if not page_section_service.delete(db, section_id):
        raise HTTPException(status_code=404, detail="Section introuvable")
    return {"message": "Section supprimée"}
