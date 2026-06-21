from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.Schemas.SFormation import FormationCreate, FormationUpdate, FormationResponse
from app.services import formation_service
from app.dependencies.Dependencie import get_current_user, require_role
from app.Models.MModels import User
import shutil, uuid, os

router = APIRouter(prefix="/api/v1/formations", tags=["Formations"])

UPLOAD_DIR = "static/uploads/formations"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Public ────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[FormationResponse])
def list_formations(db: Session = Depends(get_db)):
    return formation_service.get_all(db, published_only=True)

@router.get("/all", response_model=List[FormationResponse])
def list_all_formations(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    return formation_service.get_all(db, published_only=False)

@router.get("/{formation_id}", response_model=FormationResponse)
def get_formation(formation_id: int, db: Session = Depends(get_db)):
    f = formation_service.get_by_id(db, formation_id)
    if not f:
        raise HTTPException(status_code=404, detail="Formation introuvable")
    return f

# ── Admin uniquement ──────────────────────────────────────────────────────
@router.post("/", response_model=FormationResponse, status_code=201)
def create_formation(
    data: FormationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    return formation_service.create(db, data)

@router.put("/{formation_id}", response_model=FormationResponse)
def update_formation(
    formation_id: int,
    data: FormationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    f = formation_service.update(db, formation_id, data)
    if not f:
        raise HTTPException(status_code=404, detail="Formation introuvable")
    return f

@router.delete("/{formation_id}")
def delete_formation(
    formation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    if not formation_service.delete(db, formation_id):
        raise HTTPException(status_code=404, detail="Formation introuvable")
    return {"message": "Formation supprimée"}

@router.post("/{formation_id}/upload-image")
def upload_image(
    formation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(['admin']))
):
    f = formation_service.get_by_id(db, formation_id)
    if not f:
        raise HTTPException(status_code=404, detail="Formation introuvable")
    ext      = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path     = f"{UPLOAD_DIR}/{filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    f.image_url = f"/{path}"
    db.commit()
    return {"image_url": f.image_url}
