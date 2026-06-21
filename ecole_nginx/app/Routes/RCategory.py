from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.Schemas.SCommunaute import CategoryCreate, CategoryResponse

from app.services import category_service

router = APIRouter(prefix="/api/v1/categories", tags=["Catégories"])

@router.get("/", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return category_service.get_all(db)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = category_service.get_by_id(db, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")
    return cat

@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    existing = category_service.get_by_name(db, data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Catégorie déjà existante")
    return category_service.create(db, data)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db)):
    cat = category_service.update(db, category_id, data)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")
    return cat

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    if not category_service.delete(db, category_id):
        raise HTTPException(status_code=404, detail="Catégorie introuvable")
    return {"message": "Catégorie supprimée"}