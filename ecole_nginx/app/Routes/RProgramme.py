
# routes/Programme_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request,status, BackgroundTasks
from app.Helper.elearning_webhook import notify_programme_changed, notify_programme_deleted
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
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe,resolve_professeur_id
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
    background_tasks: BackgroundTasks,
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

    # Synchronisation temps réel vers elearning-iusth (voir plan Épic 20)
    # — regroupé par année académique, un seul webhook par année présente
    # dans ce lot, jamais un appel par programme. Déclenché sur TOUT
    # changement (pas seulement le professeur) : le payload porte
    # maintenant la fiche complète (voir Helper/elearning_webhook.py), donc
    # elearning-iusth doit être notifié même si seul un horaire ou un
    # coefficient a changé.
    _programme_ids_changed_by_annee: dict[str, list[str]] = {}

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
                    "credits": item.credits,
                    "obligatoire": item.obligatoire,
                })
                _programme_ids_changed_by_annee.setdefault(item.annee_academique, []).append(item.id)
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
                        credits=item.credits,
                        obligatoire=item.obligatoire,
                    )
                    db.add(programme)
                    db.flush()
                    _programme_ids_changed_by_annee.setdefault(item.annee_academique, []).append(programme.id)

        db.commit()
        for annee_id, programme_ids in _programme_ids_changed_by_annee.items():
            background_tasks.add_task(notify_programme_changed, db, annee_id, programme_ids)
        return {"success": "Opération réussie"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))

# DELETE
@router.get("/delete-programme/{programme_id}", status_code=200)
def delete_programme(
    programme_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    programme = db.query(Programme).filter(
        Programme.id == programme_id
    ).first()

    if not programme:
        raise HTTPException(status_code=404, detail="Programme non trouvé")

    annee_academique = programme.annee_academique
    db.delete(programme)
    db.commit()

    # Un programme supprimé n'est jamais rattrapé par un import (l'import
    # n'upserte que ce qu'il reçoit, il ne supprime jamais ce qui manque) —
    # voir Helper/elearning_webhook.py::notify_programme_deleted.
    background_tasks.add_task(notify_programme_deleted, annee_academique, programme_id)

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
    prof_id = resolve_professeur_id(current_user, db)
    if not prof_id:
        raise HTTPException(status_code=404, detail="Aucune fiche professeur associée à ce compte")

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
    prof_id = resolve_professeur_id(current_user, db)
    if not prof_id:
        return {"message": "Aucune fiche professeur associée à ce compte"}

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
    prof_id = resolve_professeur_id(current_user, db)
    if not prof_id:
        return {"message": "Aucune fiche professeur associée à ce compte"}

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

def _parse_data_etudiant(raw):
    """data_etudiant est une colonne JSON qui contient parfois une chaîne
    JSON (double encodage), parfois un dict, parfois "[]" — même
    normalisation que RNotes.parse_etudiant_data."""
    import json
    if isinstance(raw, str):
        try:
            raw = json.loads(raw) if raw.strip() else {}
        except (ValueError, TypeError):
            return {}
    return raw if isinstance(raw, dict) else {}


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


@router.get("/mes-statistiques-prof")
def get_statistiques_prof(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Agrégats de l'espace enseignant (Mes Classes, Statistiques, Tableau de
    bord) pour l'année active, limités aux matières du prof connecté.

    Les notes vivent dans cours_etudiants.data_etudiant (la table notes est
    vide) : {identifiant: {type_matiere: {matiere: {professeur_id,
    coefficients, notes: {examen: valeur}}}}}. Moyenne sur 10, même formule
    que les bulletins (BulletinPrint.py) : somme(notes) / somme(coefficients)
    * 10."""
    from datetime import datetime, timedelta
    from app.Models.MRelations import CoursEtudiant, Presence

    prof_id = resolve_professeur_id(current_user, db)
    if not prof_id:
        raise HTTPException(status_code=404, detail="Aucune fiche professeur associée à ce compte")

    annee_active = db.query(AnneeAcademique).filter(AnneeAcademique.status == 1).first()
    if not annee_active:
        raise HTTPException(status_code=404, detail="Aucune année active")

    programmes = (
        db.query(Programme)
        .filter(
            Programme.professeur_id == prof_id,
            Programme.annee_academique == annee_active.id
        )
        .all()
    )

    # Matières enseignées par classe (repli quand professeur_id manque dans
    # le JSON des notes saisies avant l'ajout de ce champ)
    matieres_par_classe = {}
    for p in programmes:
        if p.class_ and p.cours:
            matieres_par_classe.setdefault(p.class_, set()).add(p.cours.cours_nom)

    classe_ids = list(matieres_par_classe.keys())
    classes_db = {c.id: c for c in db.query(Classe).filter(Classe.id.in_(classe_ids)).all()} if classe_ids else {}
    niveaux = {n.id: n.name for n in db.query(Niveau).all()}

    # Effectifs
    inscrits = (
        db.query(ClasseEtudiant.classes_id, Etudiant.id, Etudiant.nom, Etudiant.prenom)
        .join(Etudiant, Etudiant.id == ClasseEtudiant.etudiant_id)
        .filter(
            ClasseEtudiant.classes_id.in_(classe_ids),
            ClasseEtudiant.annee_academique_id == annee_active.id
        )
        .all()
    ) if classe_ids else []
    etudiants_par_classe = {}
    noms = {}
    for classe_id, etu_id, nom, prenom in inscrits:
        etudiants_par_classe.setdefault(classe_id, set()).add(etu_id)
        noms[etu_id] = f"{prenom or ''} {nom or ''}".strip()

    # Moyennes par étudiant (matières du prof uniquement)
    rows = (
        db.query(CoursEtudiant)
        .filter(
            CoursEtudiant.classe.in_(classe_ids),
            CoursEtudiant.annee_academique == annee_active.annee_academique
        )
        .all()
    ) if classe_ids else []

    moyennes = {}  # (classe_id, etudiant_id) -> moyenne /10
    toutes_notes = []  # chaque note ramenée sur 10, pour la distribution
    for row in rows:
        data = _parse_data_etudiant(row.data_etudiant)
        matieres_classe = matieres_par_classe.get(row.classe, set())
        total_notes = total_coef = 0.0
        for par_type in data.values():
            if not isinstance(par_type, dict):
                continue
            for matieres in par_type.values():
                if not isinstance(matieres, dict):
                    continue
                for nom_matiere, info in matieres.items():
                    if not isinstance(info, dict):
                        continue
                    pid = info.get("professeur_id")
                    if pid != prof_id and not (pid is None and nom_matiere in matieres_classe):
                        continue
                    coef = _to_float(info.get("coefficients")) or 0.0
                    for valeur in (info.get("notes") or {}).values():
                        n = _to_float(valeur)
                        if n is None or coef <= 0:
                            continue
                        total_notes += n
                        total_coef += coef
                        toutes_notes.append(n / coef * 10)
        if total_coef > 0:
            moyennes[(row.classe, row.etudiant_id)] = total_notes / total_coef * 10

    # Présences (par classe + 8 dernières semaines)
    presences = (
        db.query(Presence.classes_id, Presence.date_daujourdhui, Presence.valeur)
        .filter(
            Presence.classes_id.in_(classe_ids),
            Presence.annee_academique_id == annee_active.id
        )
        .all()
    ) if classe_ids else []
    pres_classe = {}
    debut_semaine = datetime.now().date() - timedelta(days=datetime.now().weekday())
    semaines = [{"debut": (debut_semaine - timedelta(weeks=i)), "total": 0, "presents": 0} for i in range(7, -1, -1)]
    for classe_id, date_jour, valeur in presences:
        stats = pres_classe.setdefault(classe_id, [0, 0])
        stats[0] += 1
        stats[1] += 1 if valeur else 0
        if date_jour:
            d = date_jour.date() if hasattr(date_jour, "date") else date_jour
            for s in semaines:
                if s["debut"] <= d < s["debut"] + timedelta(weeks=1):
                    s["total"] += 1
                    s["presents"] += 1 if valeur else 0
                    break

    def pct(a, b):
        return round(a / b * 100) if b else None

    SEUIL = 5.0  # moyenne de passage sur 10
    classes = []
    for classe_id in classe_ids:
        classe = classes_db.get(classe_id)
        moy_classe = [m for (c, _), m in moyennes.items() if c == classe_id]
        p_stats = pres_classe.get(classe_id, [0, 0])
        classes.append({
            "classe_id": classe_id,
            "nom": classe.nom_classe if classe else classe_id,
            "niveau": niveaux.get(classe.niveau_id) if classe else None,
            "matieres": sorted(matieres_par_classe[classe_id]),
            "studentCount": len(etudiants_par_classe.get(classe_id, ())),
            "moyenne": round(sum(moy_classe) / len(moy_classe), 2) if moy_classe else None,
            "reussite": pct(sum(1 for m in moy_classe if m >= SEUIL), len(moy_classe)),
            "presence": pct(p_stats[1], p_stats[0]),
            "notesCount": len(moy_classe),
        })
    classes.sort(key=lambda c: c["nom"])

    toutes_moy = list(moyennes.values())
    total_pres = sum(s[0] for s in pres_classe.values())
    total_presents = sum(s[1] for s in pres_classe.values())

    tranches = [("<3", 0, 3), ("3-5", 3, 5), ("5-6", 5, 6), ("6-7", 6, 7), ("7-8", 7, 8), (">8", 8, 10.01)]
    distribution = [
        {"tranche": label, "pct": pct(sum(1 for n in toutes_notes if lo <= n < hi), len(toutes_notes)) or 0}
        for label, lo, hi in tranches
    ]

    top = sorted(moyennes.items(), key=lambda kv: kv[1], reverse=True)[:5]
    top_etudiants = [{
        "etudiant_id": etu_id,
        "nom": noms.get(etu_id, ""),
        "classe": classes_db[c].nom_classe if c in classes_db else "",
        "moyenne": round(m, 2),
    } for (c, etu_id), m in top]

    return {
        "annee": {"id": annee_active.id, "nom": annee_active.annee_academique},
        "kpis": {
            "etudiants": len({e for s in etudiants_par_classe.values() for e in s}),
            "moyenne": round(sum(toutes_moy) / len(toutes_moy), 2) if toutes_moy else None,
            "reussite": pct(sum(1 for m in toutes_moy if m >= SEUIL), len(toutes_moy)),
            "presence": pct(total_presents, total_pres),
            "en_difficulte": sum(1 for m in toutes_moy if m < SEUIL),
        },
        "classes": classes,
        "distribution": distribution,
        "presence_semaines": [
            {"debut": s["debut"].isoformat(), "pct": pct(s["presents"], s["total"])} for s in semaines
        ],
        "top_etudiants": top_etudiants,
    }
