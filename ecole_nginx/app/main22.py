
from fastapi import FastAPI,Depends,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import or_
from typing import List
from app.database import engine, Base
from sqlalchemy.orm import Session
from app.database import get_db
from app.Models.MModels import Cours,Professeur,Niveau,Classe,Faculte,Etudiant
from app.Schemas.Academic import ProfesseurResponseSchema
from app.Schemas.SMain import NiveauResponse,EtudiantSchema
from app.Schemas.cours_schema import simpleCoursResponse
from app.Routes import Etudiants, RAcademic,RCours,RProgramme,dashboard,RCoursEtudiant,RParamExam,RAnneAcademique,RClasses,RInscription,RPaiement,RPaiementParam,RClientInfos


# Créer les tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Gestion Scolaire - Le Mignon",
    description="API REST pour la gestion d'établissement scolaire",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(dashboard.router)
app.include_router(dashboard.router_class)
app.include_router(Etudiants.router)
app.include_router(RCours.router)
app.include_router(RProgramme.router)
app.include_router(RAnneAcademique.router)
app.include_router(RClasses.router)
app.include_router(RInscription.router)
app.include_router(RPaiement.router)
app.include_router(RPaiementParam.router)
app.include_router(RParamExam.router)
app.include_router(RCoursEtudiant.router)
app.include_router(RAcademic.router_annee)
app.include_router(RAcademic.router_niveau)
app.include_router(RAcademic.router_faculte)
app.include_router(RAcademic.router_classe)
app.include_router(RAcademic.router_professeur)
app.include_router(RAcademic.router_personnel)
app.include_router(RClientInfos.router)
app.include_router(RClientInfos.router)


@app.get("/api/v1/for-combo-cours", response_model=simpleCoursResponse)
def get_all_cours(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cours = db.query(Cours).offset(skip).limit(limit).all()
    return {"cours":cours} 

@app.get("/api/v1/for-combo-cours", response_model=ProfesseurResponseSchema)
def get_all_professeur(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prof = db.query(Professeur).offset(skip).limit(limit).all()
    return {"prof":prof} 


@app.get("/api/v1/niveau-with-class/{niveau}", response_model=NiveauResponse)
def get_niveau(niveau_id: str, db: Session = Depends(get_db)):

    try:
        # Niveau actif
        niveau = db.query(Niveau)\
            .filter(Niveau.id == niveau_id, Niveau.status == 1)\
            .first()

        if not niveau:
            raise HTTPException(status_code=404, detail="Niveau non trouvé")

        # Classes actuelles
        classe_actuelle = db.query(Classe)\
            .filter(Classe.niveau_id == niveau.id)\
            .order_by(Classe.created_at)\
            .all()

        # Cours
        cours = db.query(Cours)\
            .order_by(Cours.cours_nom)\
            .all()

        # Niveau d'étude avec LEFT JOIN
        # niveau_detude = db.query(
        #         NiveauDetude.id,
        #         NiveauDetude.niveau,
        #         Niveau.name,
        #         NiveauDetude.annee_detude
        #     )\
        #     .join(Niveau, Niveau.id == NiveauDetude.niveau, isouter=True)\
        #     .filter(NiveauDetude.niveau == niveau.id)\
        #     .order_by(NiveauDetude.id.desc())\
        #     .all()

        # Facultés
        facultes = db.query(Faculte).all()

        return {
            "niveau": niveau,
            # "niveau_detude": niveau_detude,
            "cours": cours,
            "facultes": facultes,
            "classe_actuelle": classe_actuelle
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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


class EtudiantResponse(BaseModel):
    data: List[EtudiantSchema]

@app.get("/live-student", response_model=EtudiantResponse)
def fetch_live_student(val: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    data = db.query(Etudiant)\
        .filter(
            or_(
                Etudiant.identifiant.ilike(f"%{val}%"),
                Etudiant.nom.ilike(f"%{val}%"),
                Etudiant.prenom.ilike(f"%{val}%"),
                Etudiant.code.ilike(f"%{val}%")
            )
        )\
        .limit(10)\
        .all()
    
    return {"data": data}

@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API de Gestion Scolaire - Le Mignon",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
