# crud/Programme_crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import Optional, List, Dict, Any
from app.Models.MRelations import Programme
from app.Schemas.programme_schema import ProgrammeCreate, ProgrammeUpdate

class ProgrammeCRUD:
    @staticmethod
    def get(db: Session, Programme_id: str) -> Optional[Programme]:
        return db.query(Programme).filter(Programme.id == Programme_id).first()
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        professeur_id: Optional[str] = None,
        cours_id: Optional[str] = None,
        niveau_id: Optional[str] = None,
        annee_academique: Optional[str] = None,
        faculte_id: Optional[str] = None,
        session: Optional[str] = None
    ) -> tuple[List[Programme], int]:
        query = db.query(Programme)
        
        # Recherche textuelle
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Programme.class_.ilike(search_term),
                    Programme.session.ilike(search_term),
                    Programme.heure.ilike(search_term),
                    Programme.jours.ilike(search_term),
                    Programme.annee_academique.ilike(search_term),
                    Programme.coefficients.ilike(search_term),
                    Programme.note_de_passage.ilike(search_term)
                )
            )
        
        # Filtres
        if professeur_id:
            query = query.filter(Programme.professeur_id == professeur_id)
        if cours_id:
            query = query.filter(Programme.Cours_id == cours_id)
        if niveau_id:
            query = query.filter(Programme.niveau_id == niveau_id)
        if annee_academique:
            query = query.filter(Programme.annee_academique == annee_academique)
        if faculte_id:
            query = query.filter(Programme.Faculte_id == faculte_id)
        if session:
            query = query.filter(Programme.session == session)
        
        # Compter total avant pagination
        total = query.count()
        
        # Appliquer pagination
        items = query.offset(skip).limit(limit).all()
        
        return items, total
    
    @staticmethod
    def create(db: Session, Programme: ProgrammeCreate) -> Programme:
        db_Programme = Programme(**Programme.model_dump())
        db.add(db_Programme)
        db.commit()
        db.refresh(db_Programme)
        return db_Programme
    
    @staticmethod
    def update(db: Session, Programme_id: str, Programme_update: ProgrammeUpdate) -> Optional[Programme]:
        db_Programme = ProgrammeCRUD.get(db, Programme_id)
        if not db_Programme:
            return None
        
        update_data = Programme_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_Programme, field, value)
        
        db.commit()
        db.refresh(db_Programme)
        return db_Programme
    
    @staticmethod
    def delete(db: Session, Programme_id: str) -> bool:
        db_Programme = ProgrammeCRUD.get(db, Programme_id)
        if not db_Programme:
            return False
        
        db.delete(db_Programme)
        db.commit()
        return True