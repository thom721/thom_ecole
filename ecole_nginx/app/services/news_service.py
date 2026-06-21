 
from sqlalchemy.orm import Session
from app.Models.MRelations import News, AudienceType
from app.Schemas.SCommunaute import NewsCreate, NewsUpdate
from typing import Optional

def get_all(db: Session, audience: Optional[AudienceType] = None, published_only: bool = False):
    query = db.query(News)
    if audience:
        query = query.filter(News.audience == audience)
    if published_only:
        query = query.filter(News.is_published == True)
    return query.order_by(News.created_at.desc()).all()

def get_by_id(db: Session, news_id: int):
    return db.query(News).filter(News.id == news_id).first()

def create(db: Session, data: NewsCreate):
    news = News(**data.model_dump())
    db.add(news)
    db.commit()
    db.refresh(news)
    return news

def update(db: Session, news_id: int, data: NewsUpdate):
    news = get_by_id(db, news_id)
    if not news:
        return None
    for key, value in data.model_dump().items():
        setattr(news, key, value)
    db.commit()
    db.refresh(news)
    return news

def delete(db: Session, news_id: int):
    news = get_by_id(db, news_id)
    if not news:
        return False
    db.delete(news)
    db.commit()
    return True
 