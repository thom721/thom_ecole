
# routes/Programme_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request,status
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, asc, or_, and_,distinct,select
import math
from app.Models.MModels import AnneeAcademique,Professeur,Niveau,Classe,Cours,Faculte,User,Etudiant
from app.Models.MRelations import Programme,ClasseEtudiant #,Classes
# from app.Models.MSystems import 
from app.database import get_db
from typing import Optional,List
from app.Schemas.programme_schema import (
    ProgrammeCreate, 
    ProgrammeUpdate, 
    ProgrammeResponse, 
    PaginatedProgrammeResponse,ProgrammeResponseOne,ProgrammeCoursRequest
)
from pydantic import BaseModel
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe
router = APIRouter(prefix="/api/v1", tags=["Programmes"])

# GET avec pagination, recherche et filtres
@router.get("/programme", response_model=PaginatedProgrammeResponse)
def get_programmes(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Recherche sur cours, classe, année, niveau"),
    class_id: Optional[str] = Query(None, description="Filtrer par ID de classe"),
    annee_academique_id: Optional[str] = Query(None, description="Filtrer par ID d'année académique"),
    niveau_id: Optional[str] = Query(None, description="Filtrer par ID de niveau"),
    faculte_id: Optional[str] = Query(None, description="Filtrer par ID de faculté"),
    db: Session = Depends(get_db)
):
    # Aliases pour les joins
    CoursAlias = aliased(Cours)
    FaculteAlias = aliased(Faculte)
    AnneeAcademiqueAlias = aliased(AnneeAcademique)
    ProfesseurAlias = aliased(Professeur)
    NiveauAlias = aliased(Niveau)
    ClasseAlias = aliased(Classe)
    
    # Query de base avec tous les joins
    query = (
        db.query(
            Programme.id.label("progId"),
            Programme.niveau_id,
            Programme.class_,
            Programme.session,
            Programme.heure,
            Programme.jours,
            Programme.note_de_passage,
            Programme.coefficients,
            Programme.Faculte_id,
            Programme.updated_at,
            
            # Champs des joins
            CoursAlias.cours_nom,
            ClasseAlias.id.label("classId"),
            ClasseAlias.nom_classe,
            ProfesseurAlias.id.label("profId"),
            ProfesseurAlias.nom.label("prof_nom"),
            ProfesseurAlias.prenom,
            NiveauAlias.name.label("niveau_name"),
            FaculteAlias.nom.label("fac_name"),
            AnneeAcademiqueAlias.annee_academique,
            AnneeAcademiqueAlias.id.label("annee_academique_id"),
            CoursAlias.id.label("coursId")
        )
        .outerjoin(CoursAlias, Programme.Cours_id == CoursAlias.id)
        .outerjoin(FaculteAlias, Programme.Faculte_id == FaculteAlias.id)
        .outerjoin(AnneeAcademiqueAlias, Programme.annee_academique == AnneeAcademiqueAlias.id)
        .outerjoin(ProfesseurAlias, Programme.professeur_id == ProfesseurAlias.id)
        .outerjoin(NiveauAlias, Programme.niveau_id == NiveauAlias.id)
        .outerjoin(ClasseAlias, Programme.class_ == ClasseAlias.id)
    )
    
    # Filtre par classe
    if class_id:
        query = query.filter(Programme.class_ == class_id)
    
    # Filtre par année académique
    if annee_academique_id:
        query = query.filter(Programme.annee_academique == annee_academique_id)
    
    # Filtre par niveau
    if niveau_id:
        query = query.filter(Programme.niveau_id == niveau_id)
    
    # Filtre par faculté
    if faculte_id:
        query = query.filter(Programme.Faculte_id == faculte_id)
    
    # Recherche textuelle (comme ton Laravel)
    if search:
        search_pattern = f"%{search}%"
        
        query = query.filter(
            or_(
                CoursAlias.cours_nom.ilike(search_pattern),
                ClasseAlias.nom_classe.ilike(search_pattern),
                AnneeAcademiqueAlias.annee_academique.ilike(search_pattern),
                NiveauAlias.name.ilike(search_pattern),
                ProfesseurAlias.nom.ilike(search_pattern),
                ProfesseurAlias.prenom.ilike(search_pattern)
            )
        )
    
    # Order by (comme ton Laravel)
    query = query.order_by(asc(NiveauAlias.name)).order_by(desc(Programme.updated_at))
    
    # Pagination
    total = query.count()
    skip = (page - 1) * per_page
    
    results = query.offset(skip).limit(per_page).all()
    
    # Transformer les résultats
    data = []
    
    for row in results:
        # Construire le nom complet du professeur
        professeur_fullname = None
        if row.prof_nom and row.prenom:
            professeur_fullname = f"{row.prof_nom} {row.prenom}"
        elif row.prof_nom:
            professeur_fullname = row.prof_nom
        
        data.append({
            "id": row.progId,
            "cours": row.cours_nom,
            "coefficients":float(row.coefficients) if row.coefficients else 0.0,
            "niveau_name": row.niveau_name,
            "professeur": professeur_fullname,
            "classe": row.nom_classe,
            "class_": row.class_,
            "annee_academique": row.annee_academique,
             "note_de_passage":float(row.note_de_passage) if row.note_de_passage else 0.0,
            # Champs additionnels
            "niveau_id": row.niveau_id,
            "faculte_id": row.Faculte_id,
            "annee_academique_id": row.annee_academique_id,
            "classId": row.classId,
            "profId": row.profId,
            "coursId": row.coursId,
            "session": row.session,
            "heure": row.heure,
            "jours": row.jours,
            "fac_name": row.fac_name,
            "prof_nom": row.prof_nom,
            "prenom": row.prenom,
            "updated_at": row.updated_at
        }) 
    # Calculer la dernière page
    last_page = math.ceil(total / per_page) if total else 1
    
    # Construire les query params pour la pagination
    query_params = {}
    if search:
        query_params["search"] = search
    if class_id:
        query_params["class_id"] = class_id
    if annee_academique_id:
        query_params["annee_academique_id"] = annee_academique_id
    if niveau_id:
        query_params["niveau_id"] = niveau_id
    if faculte_id:
        query_params["faculte_id"] = faculte_id
    
    return PaginatedProgrammeResponse(
        data=data,
        meta={
            "current_page": page,
            "last_page": last_page,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if data else 0,
            "to": skip + len(data) if data else 0,
            "query_params": query_params
        }
    )

# GET par ID
@router.get("/programme/{programme_id}", response_model=ProgrammeResponseOne)
def get_programme(programme_id: str, db: Session = Depends(get_db)):
    # Utiliser la même query que pour la liste mais filtrer par ID
    CoursAlias = aliased(Cours)
    FaculteAlias = aliased(Faculte)
    AnneeAcademiqueAlias = aliased(AnneeAcademique)
    ProfesseurAlias = aliased(Professeur)
    NiveauAlias = aliased(Niveau)
    ClasseAlias = aliased(Classe)
    
    result = (
        db.query(
            Programme.id.label("prog_id"),
            Programme.niveau_id,
            Programme.class_, 
            Programme.session,
            Programme.note_de_passage,
            Programme.coefficients,
            Programme.heure,
            Programme.jours,
            Programme.Faculte_id,
            Programme.updated_at,
            
            CoursAlias.cours_nom,
            ClasseAlias.id,
            ClasseAlias.nom_classe,
            ProfesseurAlias.id.label("professeur_id"),
            ProfesseurAlias.nom.label("prof_nom"),
            ProfesseurAlias.prenom,
            NiveauAlias.name.label("niveau_name"),
            FaculteAlias.nom.label("fac_name"),
            AnneeAcademiqueAlias.annee_academique,
            AnneeAcademiqueAlias.id.label("annee_academique_id"),
            CoursAlias.id.label("Cours_id")
        )
        .outerjoin(CoursAlias, Programme.Cours_id == CoursAlias.id)
        .outerjoin(FaculteAlias, Programme.Faculte_id == FaculteAlias.id)
        .outerjoin(AnneeAcademiqueAlias, Programme.annee_academique == AnneeAcademiqueAlias.id)
        .outerjoin(ProfesseurAlias, Programme.professeur_id == ProfesseurAlias.id)
        .outerjoin(NiveauAlias, Programme.niveau_id == NiveauAlias.id)
        .outerjoin(ClasseAlias, Programme.class_ == ClasseAlias.id)
        .filter(Programme.id == programme_id)
        .first()
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    
    # Construire le nom complet du professeur
    professeur_fullname = None
    if result.prof_nom and result.prenom:
        professeur_fullname = f"{result.prof_nom} {result.prenom}"
    elif result.prof_nom:
        professeur_fullname = result.prof_nom
    
    item = {
        "id": result.prog_id,
        "cours": result.cours_nom,
        "niveau_name": result.niveau_name,
        "professeur": professeur_fullname,
        "nom_classe": result.nom_classe,
        "annee_academique": result.annee_academique,
        "niveau_id": result.niveau_id,
        "faculte_id": result.Faculte_id,
        "annee_academique_id": result.annee_academique_id,
        "coefficients": float(result.coefficients) if result.coefficients else 0,
        "class_": result.class_,
        "professeur_id": result.professeur_id,
        "Cours_id": result.Cours_id,
        "session": result.session,
        "heure": result.heure,
        "jours": result.jours,
        "fac_name": result.fac_name,
        "prof_nom": result.prof_nom,
        "prenom": result.prenom,
        "updated_at": result.updated_at
    }
    return ProgrammeResponseOne(data=item)

@router.post("/programme")
def store_programme(
    payload: ProgrammeCoursRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    programme_items = payload.programmeCoursObject
    # print(programme_items)

    if not programme_items:
        raise HTTPException(status_code=422, detail="programmeCoursObject est requis")
    
    for index, item in enumerate(programme_items):
        niveau = db.query(Niveau).filter(Niveau.id == item.niveau_id).first()
        validate_exists(Niveau, Niveau.id, db, item.niveau_id)
        validate_exists(Cours, Cours.id, db, item.cours_id)
        validate_exists(Classe, Classe.id, db, item.class_)
        validate_exists(Professeur, Professeur.id, db, item.professeur_id)
        validate_exists(AnneeAcademique, AnneeAcademique.id, db, item.annee_academique)

        if not niveau:
            raise HTTPException(
                status_code=422,
                detail=f"Niveau invalide à l'index {index}"
            )

        # Faculté obligatoire pour Universitaire / Technique
        if niveau.name in ["Universitaire", "Technique"] and not item.faculte_id:
            validate_exists(Faculte, Faculte.id, db, item.faculte_id)
            if not item.note_de_passage:
                raise HTTPException(
                    status_code=422,
                    detail=f"Note de passage obligatoire pour le niveau {niveau.name}"
                )
            if item.faculte_id in (None, ''):
                raise HTTPException(
                    status_code=422,
                    detail=f"Faculte obligatoire pour le niveau {niveau.name}"
                )
            if item.jours in (None, ''):
                raise HTTPException(
                    status_code=422,
                    detail=f"Jours obligatoire pour le niveau {niveau.name}"
                )
            if item.heure in (None, ''):
                raise HTTPException(
                    status_code=422,
                    detail=f"heure obligatoire pour le niveau {niveau.name}"
                )


        # Jours & Heure obligatoires hors Préscolaire / Primaire
        if niveau.name in ["Prescolaire", "Primaire",'Cycle',"Secondaire"]:
            print(niveau.name,item.heure,item.jours)

            if item.jours in (None, '') and niveau.name in ['Cycle', 'Secondaire']:
                raise HTTPException(
                    status_code=422,
                    detail=f"Jours obligatoire pour le niveau {niveau.name}"
                )

            if item.heure in (None, '') and niveau.name in ['Cycle', 'Secondaire']:
                raise HTTPException(
                    status_code=422,
                    detail=f"L'heure est obligatoire pour le niveau {niveau.name}"
                )
     
            if not item.coefficients:
                raise HTTPException(
                    status_code=422,
                    detail=f"Coefficients obligatoire pour le niveau {niveau.name}"
                )

        # Session obligatoire pour Universitaire
        if niveau.name == "Universitaire" and not item.session:
            raise HTTPException(
                status_code=422,
                detail="session obligatoire pour niveau Universitaire"
            )
        
        has_update = any(item.id for item in programme_items)

        if has_update:
            if not user_has_permission(current_user, "Modifier cours", db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Non autorisé à modifier le programme"
                )
        else:
            if not user_has_permission(current_user, "Ajouter cours", db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Non autorisé à ajouter un programme"
                )

    try:
        for item in programme_items: 
            item_passage = item.note_de_passage if item.note_de_passage not in (None, '') else 0
            if item.id:
                db.query(Programme).filter(Programme.id == item.id).update({
                    "Cours_id": item.cours_id,
                    "niveau_id": item.niveau_id,
                    "coefficients": item.coefficients,
                    "annee_academique": item.annee_academique,
                    "professeur_id": item.professeur_id,
                    "Faculte_id": item.faculte_id,
                    "jours": item.jours,
                    "heure": item.heure,
                    "note_de_passage": item_passage,
                    "session": item.session,
                    "class_": item.class_,
                })
            else:
                # CREATE (équivalent firstOrCreate)
                exists = db.query(Programme).filter(
                    Programme.Cours_id == item.cours_id,
                    Programme.niveau_id == item.niveau_id,
                    Programme.annee_academique == item.annee_academique,
                    Programme.class_ == item.class_,
                ).first()

                if not exists:
                    programme = Programme(
                        Cours_id=item.cours_id,
                        niveau_id=item.niveau_id,
                        annee_academique=item.annee_academique,
                        class_=item.class_,
                        professeur_id=item.professeur_id,
                        Faculte_id=item.faculte_id,
                        jours=item.jours,
                        heure=item.heure,
                        session=item.session,
                        note_de_passage=item_passage,
                        coefficients=item.coefficients,
                    )
                    db.add(programme)

        db.commit()
        return {"success": "Opération réussie"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))

# DELETE
@router.get("/delete-programme/{programme_id}", status_code=200)
def delete_programme(programme_id: str, db: Session = Depends(get_db),current_user:User= Depends(get_current_user)):
    programme = db.query(Programme).filter(
        Programme.id == programme_id
    ).first()
    
    if not programme:
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    
    db.delete(programme)
    db.commit()
    
    return {"success": "Opération réussie 00","message": "Opération réussie"}

class ProgrammeAndCoursRequest(BaseModel):
    class_id: str
    annee_academique_id: str
    niveau_id: Optional[str]=None
    faculte_id: Optional[str]=None

@router.post("/programme-and-student-cours")
def get_cours_and_programme(
    payload: ProgrammeAndCoursRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    CoursAlias = aliased(Cours)
    FaculteAlias = aliased(Faculte)
    AnneeAcademiqueAlias = aliased(AnneeAcademique)
    ProfesseurAlias = aliased(Professeur)
    NiveauAlias = aliased(Niveau)
    ClasseAlias = aliased(Classe)
    
    # Query de base avec tous les joins
    results = (
        db.query(
            Programme.id.label("progId"),
            Programme.niveau_id,
            Programme.class_,
            Programme.session,
            Programme.heure,
            Programme.jours,
            Programme.note_de_passage,
            Programme.coefficients,
            Programme.Faculte_id,
            Programme.updated_at,
            
            # Champs des joins
            CoursAlias.cours_nom,
            ClasseAlias.id.label("classId"),
            ClasseAlias.nom_classe,
            ProfesseurAlias.id.label("profId"),
            ProfesseurAlias.nom.label("prof_nom"),
            ProfesseurAlias.prenom,
            NiveauAlias.name.label("niveau_name"),
            FaculteAlias.nom.label("fac_name"),
            AnneeAcademiqueAlias.annee_academique,
            AnneeAcademiqueAlias.id.label("annee_academique_id"),
            CoursAlias.id.label("coursId")
        )
        .outerjoin(CoursAlias, Programme.Cours_id == CoursAlias.id)
        .outerjoin(FaculteAlias, Programme.Faculte_id == FaculteAlias.id)
        .outerjoin(AnneeAcademiqueAlias, Programme.annee_academique == AnneeAcademiqueAlias.id)
        .outerjoin(ProfesseurAlias, Programme.professeur_id == ProfesseurAlias.id)
        .outerjoin(NiveauAlias, Programme.niveau_id == NiveauAlias.id)
        .outerjoin(ClasseAlias, Programme.class_ == ClasseAlias.id)
    ).filter(
        Programme.class_ == payload.class_id,
        Programme.annee_academique == payload.annee_academique_id).all()
    

    
    # Transformer les résultats
    data = []
    
    for row in results:
        # Construire le nom complet du professeur
        professeur_fullname = None
        if row.prof_nom and row.prenom:
            professeur_fullname = f"{row.prof_nom} {row.prenom}"
        elif row.prof_nom:
            professeur_fullname = row.prof_nom
        
        data.append({
            "id": row.progId,
            "cours": row.cours_nom,
            "coefficients":float(row.coefficients) if row.coefficients else 0.0,
            "niveau_name": row.niveau_name,
            "professeur": professeur_fullname,
            "classe": row.nom_classe,
            "class_": row.class_,
            "annee_academique": row.annee_academique,
             "note_de_passage":float(row.note_de_passage) if row.note_de_passage else 0.0,
            # Champs additionnels
            "niveau_id": row.niveau_id,
            "faculte_id": row.Faculte_id,
            "annee_academique_id": row.annee_academique_id,
            "classId": row.classId,
            "profId": row.profId,
            "coursId": row.coursId,
            "session": row.session,
            "heure": row.heure,
            "jours": row.jours,
            "fac_name": row.fac_name,
            "prof_nom": row.prof_nom,
            "prenom": row.prenom,
            "updated_at": row.updated_at
        }) 
    return data

@router.get("/mes-programmes")
def get_programmes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    # 1️⃣ récupérer année active
    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        raise HTTPException(status_code=404, detail="Aucune année active")

    # 2️⃣ récupérer programmes du prof pour cette année
    programmes = db.query(Programme)\
        .join(Cours, Programme.Cours_id == Cours.id)\
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        )\
        .all()

    # 3️⃣ transformer programmes en dicts
    programmes_list = []
    for p in programmes:
        programmes_list.append({
            "id": p.id,
            "cours_id": p.Cours_id,
            "cours_nom": p.cours.cours_nom if p.cours else None,
            "class": p.class_,
            "niveau_id": p.niveau_id,
            "session": p.session,
            "heure": p.heure,
            "annee_academique": p.annee_academique,
            "jours": p.jours,
            "coefficients": p.coefficients,
            "note_de_passage": p.note_de_passage
        })

    # 4️⃣ transformer l'année active en dict
    annee_dict = {
        "id": annee_active.id,
        "nom": annee_active.annee_academique,
        "status": annee_active.status
    }

    return {
        "annee": annee_dict,
        "programmes": programmes_list
    }


@router.get("/mes-programmes11")
def get_programmes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    # 1️⃣ récupérer année active
    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        raise HTTPException(status_code=404, detail="Aucune année active")

    # 2️⃣ récupérer programmes du prof pour cette année
    programmes = db.query(Programme).filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        ).all()

    return {
        "annee": annee_active,
        "programmes": programmes
    }

@router.get("/mes-classes-etudiants1")
def get_classes_etudiants(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    # 1️⃣ récupérer les classes du professeur
    classes = db.query(distinct(Programme.class_))\
        .filter(Programme.professeur_id == prof_id)\
        .all()

    # transformer en liste simple
    class_list = [c[0] for c in classes if c[0] is not None]

    if not class_list:
        return {"message": "Aucune classe trouvée"}

    # 2️⃣ récupérer les étudiants pour ces classes
    etudiants = db.query(ClasseEtudiant)\
        .filter(ClasseEtudiant.classes_id.in_(class_list))\
        .all()

    return {
        "classes": class_list,
        "etudiants": etudiants
    }

@router.get("/mes-classes-etudiants2")
def get_classes_etudiants(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    # 1️⃣ récupérer année active
    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        return {"message": "Aucune année active"}

    # 2️⃣ requête unique pour toutes les classes du prof
    etudiants = (
        db.query(
            Etudiant,
            Programme.class_
        )
        .join(ClasseEtudiant, ClasseEtudiant.etudiant_id == Etudiant.id)
        .join(Programme, Programme.class_ == ClasseEtudiant.classes_id)
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        )
        .distinct()
        .all()
    )

    # 3️⃣ regrouper par classe
    result = {}

    for etudiant, classe in etudiants:
        if classe not in result:
            result[classe] = []
        result[classe].append(etudiant)

    return result

@router.get("/mes-classes-etudiants3")
def get_classes_etudiants(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    # 1️⃣ année active
    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        return {"message": "Aucune année active"}

    # 2️⃣ récupérer les classes DISTINCTES du prof
    classes = db.query(Programme.class_)\
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        )\
        .distinct()\
        .all()

    class_list = [c[0] for c in classes]

    if not class_list:
        return {"message": "Aucune classe trouvée"}

    # 3️⃣ récupérer les étudiants sans duplication
    etudiants = (
        db.query(Etudiant)
        .join(ClasseEtudiant, ClasseEtudiant.etudiant_id == Etudiant.id)
        .filter(ClasseEtudiant.classes_id.in_(class_list))
        .distinct()
        .all()
    )

    return etudiants


@router.get("/mes-classes-etudiants4")
def get_classes_etudiants(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    # 1️⃣ année active
    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        return {"message": "Aucune année active"}

    # 2️⃣ sous-requête pour récupérer les classes du prof
    subquery_classes = (
        db.query(Programme.class_)
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        )
        .distinct()
        .subquery()
    )
 
    etudiants = (
        db.query(Etudiant.nom,Etudiant.prenom,Etudiant.email,ClasseEtudiant.status,)
        .join(
            ClasseEtudiant,
            ClasseEtudiant.etudiant_id == Etudiant.id
        )
        .filter(
            ClasseEtudiant.classes_id.in_(select(subquery_classes))
        )
        .filter(
            ClasseEtudiant.annee_academique_id == annee_active.id
        )
        .distinct()
        .all()
    )

    return { "etudiants": etudiants,"programme":subquery_classes}

@router.get("/mes-classes-etudiants0")
def get_classes_etudiants(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    # 1️⃣ année active
    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        return {"message": "Aucune année active"}

    # 2️⃣ sous-requête des classes DISTINCTES
    subquery_classes = (
        db.query(Programme.class_)
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        )
        .distinct()
        .subquery()
    )

    classes = db.query(Programme.class_)\
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        ).distinct().all()
    class_list = [c[0] for c in classes if c[0]]

    if not class_list:
        return {"message": "Aucune classe trouvée"}

    # 3️⃣ récupérer les étudiants
    etudiants = (
        db.query(
            Etudiant.id,
            Etudiant.identifiant,
            Etudiant.nom,
            Etudiant.prenom,
            Etudiant.email,
            ClasseEtudiant.status
        )
        .join(
            ClasseEtudiant,
            ClasseEtudiant.etudiant_id == Etudiant.id
        )
        .filter(
            ClasseEtudiant.classes_id.in_(
                select(subquery_classes.c.class_)
            )
        )
        .filter(
            ClasseEtudiant.annee_academique_id == annee_active.id
        )
        .distinct()
        .all()
    )
    etudiants_list = [
        {
            "id": id,
            "identifiant": identifiant,
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "status": status
        }
        for id,identifiant, nom, prenom, email, status in etudiants
    ]
    # classe = 
    return {
        "classes": class_list,
        "etudiants": etudiants_list
    }

@router.get("/mes-cours")
def get_cours_prof(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    # 1️⃣ année académique active
    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        return {"message": "Aucune année active"}

    # 2️⃣ récupérer les cours DISTINCTS du prof pour l'année active
    cours = (
        db.query(Cours)
        .join(Programme, Programme.Cours_id == Cours.id)
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        )
        .distinct()
        .all()
    )
    # .cours_nom,Programme.jours,Programme.heure,Programme.coefficients,Programme.note_de_passage

    # 3️⃣ retourner uniquement les infos nécessaires
    result = [
        {"id": c.id, "nom": c.nom, "description": getattr(c, "description", None)}
        for c in cours
    ]

    return {"cours": result}

@router.get("/mes-classes-etudiants_last")
def get_classes_etudiants(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        return {"message": "Aucune année active"}

    classes = (
        db.query(Classe.id, Classe.nom_classe)
        .join(Programme, Programme.class_ == Classe.id)
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        )
        .distinct()
        .all()
    )

    if not classes:
        return {"message": "Aucune classe trouvée"}

    # ✅ Déclaration AVANT la boucle
    fullcount = 0
    result = []

    for classe_id, classe_nom in classes:

        etudiants = (
            db.query(
                Etudiant.id,
                Etudiant.identifiant,
                Etudiant.nom,
                Etudiant.prenom,
                Etudiant.email,
                ClasseEtudiant.status
            )
            .join(
                ClasseEtudiant,
                ClasseEtudiant.etudiant_id == Etudiant.id
            )
            .filter(
                ClasseEtudiant.classes_id == classe_id,
                ClasseEtudiant.annee_academique_id == annee_active.id
            )
            .distinct()
            .all()
        )

        student_count = len(etudiants)
        fullcount += student_count   # ✅ cumul correct

        result.append({
            "classe": classe_nom,
            "studentCount": student_count,
            "etudiants": [
                {
                    "id": id,
                    "identifiant": identifiant,
                    "nom": nom,
                    "prenom": prenom,
                    "email": email,
                    "status": status
                }
                for id, identifiant, nom, prenom, email, status in etudiants
            ]
        })

    return {
        "fullcount": fullcount,
        "classes": result
    }


from sqlalchemy import func

@router.get("/mes-classes-etudiants")
def get_classes_etudiants(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prof_id = current_user.userable_id

    annee_active = db.query(AnneeAcademique)\
        .filter(AnneeAcademique.status == 1)\
        .first()

    if not annee_active:
        return {"message": "Aucune année active"}

    # ✅ Une seule requête
    rows = (
        db.query(
            Classe.id.label("classe_id"),
            Classe.nom_classe.label("classe_nom"),
            Etudiant.id.label("etudiant_id"),
            Etudiant.identifiant,
            Etudiant.nom,
            Etudiant.prenom,
            Etudiant.email,
            ClasseEtudiant.status
        )
        .join(Programme, Programme.class_ == Classe.id)
        .join(ClasseEtudiant, ClasseEtudiant.classes_id == Classe.id)
        .join(Etudiant, Etudiant.id == ClasseEtudiant.etudiant_id)
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id,
            ClasseEtudiant.annee_academique_id == annee_active.id
        )
        .distinct()
        .all()
    )

    if not rows:
        return {"message": "Aucune donnée trouvée"}

    result = {}
    fullcount = 0

    for row in rows:
        classe_nom = row.classe_nom

        if classe_nom not in result:
            result[classe_nom] = {
                "studentCount": 0,
                "etudiants": []
            }

        result[classe_nom]["etudiants"].append({
            "id": row.etudiant_id,
            "identifiant": row.identifiant,
            "nom": row.nom,
            "prenom": row.prenom,
            "email": row.email,
            "status": row.status
        })

        result[classe_nom]["studentCount"] += 1
        fullcount += 1

    return {
        "studentCount": fullcount,
        "classes": result
    }