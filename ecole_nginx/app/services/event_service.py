from sqlalchemy.orm import Session
from app.Models.MRelations import Event, AudienceType
from app.Schemas.SCommunaute import EventCreate, EventUpdate
from typing import Optional

def get_all(db: Session, audience: Optional[AudienceType] = None, published_only: bool = False):
    query = db.query(Event)
    if audience:
        query = query.filter(Event.audience == audience)
    if published_only:
        query = query.filter(Event.is_published == True)
    return query.order_by(Event.start_date).all()

def get_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def create(db: Session, data: EventCreate):
    event = Event(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

def update(db: Session, event_id: int, data: EventUpdate):
    event = get_by_id(db, event_id)
    if not event:
        return None
    for key, value in data.model_dump().items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event

def delete(db: Session, event_id: int):
    event = get_by_id(db, event_id)
    if not event:
        return False
    db.delete(event)
    db.commit()
    return True