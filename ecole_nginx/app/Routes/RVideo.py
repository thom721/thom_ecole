from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.Schemas.SCommunaute import VideoCreate, VideoUpdate, VideoResponse
from app.services import video_service

router = APIRouter(prefix="/api/v1/videos", tags=["Vidéos"])

@router.get("/", response_model=List[VideoResponse])
def list_videos(published_only: bool = False, db: Session = Depends(get_db)):
    return video_service.get_all(db, published_only)

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: str, db: Session = Depends(get_db)):
    video = video_service.get_by_id(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Vidéo introuvable")
    return video

@router.post("/", response_model=VideoResponse, status_code=201)
def create_video(data: VideoCreate, db: Session = Depends(get_db)):
    return video_service.create(db, data)

@router.put("/{video_id}", response_model=VideoResponse)
def update_video(video_id: str, data: VideoUpdate, db: Session = Depends(get_db)):
    video = video_service.update(db, video_id, data)
    if not video:
        raise HTTPException(status_code=404, detail="Vidéo introuvable")
    return video

@router.delete("/{video_id}")
def delete_video(video_id: str, db: Session = Depends(get_db)):
    if not video_service.delete(db, video_id):
        raise HTTPException(status_code=404, detail="Vidéo introuvable")
    return {"message": "Vidéo supprimée"}
