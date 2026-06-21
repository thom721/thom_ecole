from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel
from sqlalchemy import or_
from typing import List
from app.database import engine, Base
from sqlalchemy.orm import Session
from app.database import get_db
from app.Models.MModels import Cours,Professeur,Niveau,Classe,Faculte,Etudiant,User
from app.Schemas.Academic import simpleProfesseurResponse
from app.Schemas.SMain import NiveauResponse
from app.Schemas.cours_schema import simpleCoursResponse
# from app.Schemas.Etudiants import EtudiantResponse


router = APIRouter(prefix="/api/v1", tags=["Other route"])

# @router.get("/for-combo-cours", response_model=simpleCoursResponse)
# def get_all_cours(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     cours = db.query(Cours).offset(skip).limit(limit).all()
#     return {"cours":cours} 

# @router.get("/prof-for-combo", response_model=simpleProfesseurResponse)
# def get_all_professeur(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     prof = db.query(Professeur).offset(skip).limit(limit).all()
#     print(f"prof:  {prof}")
#     return {"prof":prof} 



# @router.get("/live-student", response_model=List[EtudiantSchema])
# def fetch_live_student(val: str = Query(..., min_length=1), db: Session = Depends(get_db)):
#     """
#     Recherche d'étudiants en direct par identifiant, nom, prénom ou code.
#     """
#     try:
#         # Query SQLAlchemy avec OR pour plusieurs colonnes
#         data = db.query(Etudiant)\
#             .filter(
#                 or_(
#                     Etudiant.identifiant.ilike(f"%{val}%"),
#                     Etudiant.nom.ilike(f"%{val}%"),
#                     Etudiant.prenom.ilike(f"%{val}%"),
#                     Etudiant.code.ilike(f"%{val}%")
#                 )
#             )\
#             .limit(10)\
#             .all()

#         return data

#     except Exception as e:
#         raise HTTPException(status_code=422, detail=str(e))


# class EtudiantResponse(BaseModel):
#     data: List[EtudiantSchema]

# @router.get("/live-student", response_model=EtudiantResponse)
# def fetch_live_student(val: str = Query(..., min_length=1), db: Session = Depends(get_db)):
#     data = db.query(Etudiant)\
#         .filter(
#             or_(
#                 Etudiant.identifiant.ilike(f"%{val}%"),
#                 Etudiant.nom.ilike(f"%{val}%"),
#                 Etudiant.prenom.ilike(f"%{val}%"),
#                 Etudiant.code.ilike(f"%{val}%")
#             )
#         )\
#         .limit(10)\
#         .all()
    
#     return {"data": data}