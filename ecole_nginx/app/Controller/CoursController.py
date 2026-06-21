# crud/cours_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List, Dict, Any
import math
from app.Models.MModels import Cours
from app.Schemas.cours_schema import CoursCreate, CoursUpdate

class CoursCRUD:
    @staticmethod
    def get(db: Session, cours_id: str) -> Optional[Cours]:
        return db.query(Cours).filter(Cours.id == cours_id).first()
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        niveau_id: Optional[str] = None,
        type_matiere: Optional[str] = None
    ) -> tuple[List[Cours], int]:
        query = db.query(Cours)
        
        # Recherche textuelle
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Cours.cours_nom.ilike(search_term),
                    Cours.coefficients.ilike(search_term),
                    Cours.note_de_passage.ilike(search_term)
                )
            )
        
        # Filtres
        if niveau_id:
            query = query.filter(Cours.niveau_id == niveau_id)
        if type_matiere:
            query = query.filter(Cours.type_matiere == type_matiere)
        
        # Compter total avant pagination
        total = query.count()
        
        # Appliquer pagination
        items = query.offset(skip).limit(limit).all()
        
        return items, total
    
    @staticmethod
    def create(db: Session, cours: CoursCreate) -> Cours:
        db_cours = Cours(**cours.model_dump())
        db.add(db_cours)
        db.commit()
        db.refresh(db_cours)
        return db_cours
    
    @staticmethod
    def update(db: Session, cours_id: str, cours_update: CoursUpdate) -> Optional[Cours]:
        db_cours = CoursCRUD.get(db, cours_id)
        if not db_cours:
            return None
        
        update_data = cours_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cours, field, value)
        
        db.commit()
        db.refresh(db_cours)
        return db_cours
    
    @staticmethod
    def delete(db: Session, cours_id: str) -> bool:
        db_cours = CoursCRUD.get(db, cours_id)
        if not db_cours:
            return False
        
        db.delete(db_cours)
        db.commit()
        return True