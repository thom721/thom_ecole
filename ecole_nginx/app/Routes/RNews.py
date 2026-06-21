from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.Schemas.SCommunaute import NewsCreate, NewsUpdate, NewsResponse
from app.Models.MRelations import AudienceType
from app.services import news_service
import shutil, uuid, os

router = APIRouter(prefix="/api/v1/news", tags=["Actualités"])

UPLOAD_DIR = "static/uploads/news"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[NewsResponse])
def list_news(
    audience: Optional[AudienceType] = None,
    published_only: bool = False,
    db: Session = Depends(get_db)
):
    return news_service.get_all(db, audience, published_only)

@router.get("/{news_id}", response_model=NewsResponse)
def get_news(news_id: int, db: Session = Depends(get_db)):
    news = news_service.get_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Actualité introuvable")
    return news

@router.post("/", response_model=NewsResponse, status_code=201)
def create_news(data: NewsCreate, db: Session = Depends(get_db)):
    return news_service.create(db, data)

@router.put("/{news_id}", response_model=NewsResponse)
def update_news(news_id: int, data: NewsUpdate, db: Session = Depends(get_db)):
    news = news_service.update(db, news_id, data)
    if not news:
        raise HTTPException(status_code=404, detail="Actualité introuvable")
    return news

@router.delete("/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db)):
    if not news_service.delete(db, news_id):
        raise HTTPException(status_code=404, detail="Actualité introuvable")
    return {"message": "Actualité supprimée"}

@router.post("/{news_id}/upload-image")
def upload_image(news_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    news = news_service.get_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Actualité introuvable")
    ext      = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path     = f"{UPLOAD_DIR}/{filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    news.image_url = f"/{path}"
    db.commit()
    return {"image_url": news.image_url}
 
