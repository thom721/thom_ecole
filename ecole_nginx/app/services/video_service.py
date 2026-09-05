from sqlalchemy.orm import Session
from app.Models.MRelations import Video
from app.Schemas.SCommunaute import VideoCreate, VideoUpdate

def get_all(db: Session, published_only: bool = False):
    query = db.query(Video)
    if published_only:
        query = query.filter(Video.is_published == True)
    return query.order_by(Video.created_at.desc()).all()

def get_by_id(db: Session, video_id: str):
    return db.query(Video).filter(Video.id == video_id).first()

def create(db: Session, data: VideoCreate):
    video = Video(**data.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

def update(db: Session, video_id: str, data: VideoUpdate):
    video = get_by_id(db, video_id)
    if not video:
        return None
    for key, value in data.model_dump().items():
        setattr(video, key, value)
    db.commit()
    db.refresh(video)
    return video

def delete(db: Session, video_id: str):
    video = get_by_id(db, video_id)
    if not video:
        return False
    db.delete(video)
    db.commit()
    return True
