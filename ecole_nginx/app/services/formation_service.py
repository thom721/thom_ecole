from sqlalchemy.orm import Session
from app.Models.MFormation import Formation
from app.Schemas.SFormation import FormationCreate, FormationUpdate

def get_all(db: Session, published_only: bool = False):
    q = db.query(Formation)
    if published_only:
        q = q.filter(Formation.is_published == True)
    return q.order_by(Formation.ordre, Formation.id).all()

def get_by_id(db: Session, formation_id: int):
    return db.query(Formation).filter(Formation.id == formation_id).first()

def create(db: Session, data: FormationCreate):
    formation = Formation(**data.model_dump())
    db.add(formation)
    db.commit()
    db.refresh(formation)
    return formation

def update(db: Session, formation_id: int, data: FormationUpdate):
    formation = get_by_id(db, formation_id)
    if not formation:
        return None
    for key, value in data.model_dump().items():
        setattr(formation, key, value)
    db.commit()
    db.refresh(formation)
    return formation

def delete(db: Session, formation_id: int):
    formation = get_by_id(db, formation_id)
    if not formation:
        return False
    db.delete(formation)
    db.commit()
    return True
