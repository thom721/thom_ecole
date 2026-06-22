from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.Schemas.SCommunaute import EventCreate, EventUpdate, EventResponse
from app.Models.MRelations import AudienceType
from app.services import event_service
import shutil, uuid, os

from app.Helper.persistent_storage import EVENTS_DIR

router = APIRouter(prefix="/api/v1/events", tags=["Événements"])

UPLOAD_DIR = str(EVENTS_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[EventResponse])
def list_events(
    audience: Optional[AudienceType] = None,
    published_only: bool = False,
    db: Session = Depends(get_db)
):
    return event_service.get_all(db, audience, published_only)

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = event_service.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    return event

@router.post("/", response_model=EventResponse, status_code=201)
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    return event_service.create(db, data)

@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, data: EventUpdate, db: Session = Depends(get_db)):
    event = event_service.update(db, event_id, data)
    if not event:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    return event

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    if not event_service.delete(db, event_id):
        raise HTTPException(status_code=404, detail="Événement introuvable")
    return {"message": "Événement supprimé"}

@router.post("/{event_id}/upload-image")
def upload_image(event_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    event = event_service.get_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    ext      = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    disk_path = os.path.join(UPLOAD_DIR, filename)
    with open(disk_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    event.image_url = f"/static/uploads/events/{filename}"
    db.commit()
    return {"image_url": event.image_url}
 