from sqlalchemy.orm import Session
from app.Models.MRelations import Category
from app.Schemas.SCommunaute import CategoryCreate

def get_all(db: Session):
    return db.query(Category).order_by(Category.name).all()

def get_by_id(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def get_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()

def create(db: Session, data: CategoryCreate):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def update(db: Session, category_id: int, data: CategoryCreate):
    cat = get_by_id(db, category_id)
    if not cat:
        return None
    cat.name = data.name
    db.commit()
    db.refresh(cat)
    return cat

def delete(db: Session, category_id: int):
    cat = get_by_id(db, category_id)
    if not cat:
        return False
    db.delete(cat)
    db.commit()
    return True