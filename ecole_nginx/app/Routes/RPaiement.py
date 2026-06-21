from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_
import math
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import select, func, exists  
from app.Models.MModels import Etudiant, Niveau, Classe,AnneeAcademique,User
from app.Models.MFinancials import Paiement,ParametrePaiement
from app.Schemas.SPaiement import (
    PaginatedPaiementResponse, 
    PaiementResource,ShowPaiementResponse,StudentPaymentResponse,PaymentInfoResponse,PaymentInfoData,StudentPaymentData
)
from app.Models.MRelations import EtudiantFaculte,ClasseEtudiant 
from app.database import get_db
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe,require_role

FINANCIAL_ROLES = ['admin', 'Caissier', 'Responsable financier', 'Comptable']

router = APIRouter(prefix="/api/v1", tags=["Paiements"])

# GET paginé avec recherche et auto_load
@router.get("/paiement", response_model=PaginatedPaiementResponse)
def get_paiements(
    search: Optional[str] = Query(None, description="Recherche par nom, prénom ou identifiant"),
    page: Optional[int] = Query(None, description="Page number (None pour tout charger)"),
    per_page: int = Query(16, ge=1, le=100, description="Items per page"),
    auto_load: Optional[bool] = Query(None, description="Si None, retourne tout sans pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(FINANCIAL_ROLES))
):
    # Construire la requête de base avec jointure seulement pour étudiant
    # Les autres tables (niveaux, classes) semblent être des strings, pas des relations
    # query = (
    #     db.query(Paiement)
    #     .join(Etudiant, Paiement.etudiant_id == Etudiant.id)
    #     .join(Classe, Paiement.classe == Classe.id)
    #     .join(Niveau, Paiement.niveau_id == Niveau.id)
    #     .options(joinedload(Paiement.etudiant))
    # )
    from sqlalchemy.orm import joinedload, load_only

    query = (
        db.query(Paiement)
        .options(
            load_only(
                Paiement.id,
                Paiement.etudiant_id,
                Paiement.classe,
                Paiement.niveau_id,
                Paiement.annee_academique,
                Paiement.created_at,
                Paiement.updated_at,
            ),
            joinedload(Paiement.etudiant)
        )
        .join(Etudiant, Paiement.etudiant_id == Etudiant.id)
        .join(Classe, Paiement.classe == Classe.id)
        .join(Niveau, Paiement.niveau_id == Niveau.id)
    )
    
    # Appliquer la recherche si spécifiée
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Etudiant.nom.ilike(search_pattern),
                Etudiant.prenom.ilike(search_pattern),
                Etudiant.identifiant.ilike(search_pattern)
            )
        )
    
    # Trier par updated_at descendant
    query = query.order_by(desc(Paiement.updated_at))
    
    # Compter le total
    total = query.count()
    
    # Gérer la pagination selon auto_load
    # auto_load is None or 
    if page is None:
        # Retourner tout sans pagination
        paiements = query.all()
        current_page = 1
        last_page = 1
        per_page = total if total > 0 else 1
        skip = 0
    else:
        # Pagination normale
        current_page = page
        last_page = math.ceil(total / per_page) if total else 1
        skip = (current_page - 1) * per_page
        
        paiements = query.offset(skip).limit(per_page).all()
    
    # Transformer en PaiementResource
    data = []
    
    for paiement in paiements:
        # Pour niveaux et classes, vous devez faire des requêtes séparées
        # ou les avoir comme relations dans vos modèles
        # Ici je suppose que ce sont des champs strings
        data.append(PaiementResource(
            id=paiement.id,
            id_=paiement.etudiant.id if paiement.etudiant else None,
            identifiant=paiement.etudiant.identifiant if paiement.etudiant else None,
            nom=paiement.etudiant.nom if paiement.etudiant else None,
            prenom=paiement.etudiant.prenom if paiement.etudiant else None,
            annee=paiement.annee_academique,
            niveaux=paiement.niveau_ref.name,  # C'est un string, pas une relation
            classes=paiement.classe_ref.nom_classe,  # C'est un string, pas une relation
            # classes=paiement.classe.nom_classe,     # C'est un string, pas une relation
            # mois=paiement.mois,
            # accessoires=paiement.paiement_details
        ))
    
    # Calculer les métadonnées
    from_value = skip + 1 if data and skip is not None else 0
    to_value = skip + len(data) if data and skip is not None else 0

    meta = {
          "current_page": current_page,
          "last_page": last_page,
          "per_page": per_page,
          "total": total,
          "from": skip + 1 if data else 0,
          "to": skip + len(data) if data else 0
     }
        
        # Création de la réponse
    response_data = {
     "data": data,
     "meta": meta
     }
        
    return response_data
    
#     return PaginatedPaiementResponse(
#         data=data,
#         meta={
#             "current_page": current_page,
#             "last_page": last_page,
#             "per_page": per_page,
#             "total": total,
#           #   "from": from_value,
#           #   "to": to_value
#         }
#     )


@router.get("/next-payment-step", response_model=PaymentInfoResponse)
def payment_info(
    etudiant: str = Query(..., description="ID de l'étudiant"),
    annee_academique: str = Query(..., description="Année académique format: 2024-2025"),
    classe: str = Query(..., description="ID de la classe"),
    niveau: str = Query(..., description="ID du niveau"),
    annee_a: str = Query(..., description="ID de l'année académique"),
    faculte: Optional[str] = Query(None, description="ID de la faculté"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(FINANCIAL_ROLES))
):
    print(annee_academique)
    try:
        # Formater l'année académique
        start_year, end_year = annee_academique.split('-')
        anne_format = f"{start_year}/{end_year}"
        
        # Vérifier si l'étudiant n'a pas de faculté associée
        etudiant_sans_faculte = db.query(
            exists(
                select(Etudiant.id)
                .outerjoin(EtudiantFaculte, EtudiantFaculte.etudiant_id == Etudiant.id)
                .where(EtudiantFaculte.faculte_id.is_(None))
                .where(Etudiant.id == etudiant)
            )
        ).scalar()
        
        # Vérifier si un paiement existe pour l'année académique donnée
        paiement_existe = db.query(
            exists(
                select(Paiement.id)
                .where(Paiement.annee_academique == anne_format)
                .where(Paiement.etudiant_id == etudiant)
            )
        ).scalar()
        
        # Construire la requête de base
        base_select = [
            Etudiant.id.label('studentId'),
            Etudiant.nom,
            Etudiant.prenom,
            Etudiant.aide_financiere,
            Etudiant.identifiant,
            Classe.id.label('classeId'),
            Classe.nom_classe,
            AnneeAcademique.annee_academique,
            AnneeAcademique.id,
            ParametrePaiement.echeance,
            ParametrePaiement.devise,
            ParametrePaiement.nb_echeance,
            ParametrePaiement.montant,
            ParametrePaiement.montant_par,
            ParametrePaiement.accessoires,
            Niveau.name,
            Niveau.id.label('id_niveau'),
            AnneeAcademique.date_debut,
            AnneeAcademique.date_fin,
        ]
        
        # Ajouter les colonnes de paiement si un paiement existe
        if paiement_existe:
            base_select.extend([
                Paiement.paiement_details,
                Paiement.mois
            ])
        
        query = select(*base_select).select_from(Etudiant)
        
        # Jointures conditionnelles selon la faculté
        if etudiant_sans_faculte:
            query = (
                query
                .join(ClasseEtudiant, ClasseEtudiant.etudiant_id == Etudiant.id)
                .join(Niveau, Niveau.id == ClasseEtudiant.niveau_id)
                .where(ClasseEtudiant.classes_id == classe)
                .where(Niveau.id == niveau)
            )
        else:
            query = (
                query
                .join(EtudiantFaculte, EtudiantFaculte.etudiant_id == Etudiant.id)
                .join(Niveau, Niveau.id == EtudiantFaculte.niveau_id)
                .where(EtudiantFaculte.faculte_id == faculte)
                .where(Niveau.id == niveau)
            )
        
        # Si le paiement existe, ajouter la jointure paiements
        if paiement_existe:
            query = (
                query
                .join(Paiement, Paiement.etudiant_id == Etudiant.id)
                .where(Paiement.annee_academique == anne_format)
            )
        
        # Jointures communes
        query = (
            query
            .join(ParametrePaiement, Niveau.id == ParametrePaiement.niveau_id)
            .join(Classe, Classe.id == ParametrePaiement.classe)
            .join(AnneeAcademique, AnneeAcademique.id == ParametrePaiement.anneeAcademique)
            .where(ParametrePaiement.niveau_id == niveau)
            .where(ParametrePaiement.classe == classe)
            .where(ParametrePaiement.anneeAcademique == annee_a)
            .where(Etudiant.id == etudiant)
        )
        
        # Exécuter la requête
        result = db.execute(query).first()
        
        # Construire la réponse
        data = None
        if result:
            row_dict = {
                'studentId': result.studentId,
                'nom': result.nom,
                'prenom': result.prenom,
                'aide_financiere': result.aide_financiere,
                'identifiant': result.identifiant,
                'classeId': result.classeId,
                'nom_classe': result.nom_classe,
                'annee_academique': result.annee_academique,
                'id': result.id,
                'echeance': result.echeance,
                'devise': result.devise,
                'nb_echeance': result.nb_echeance,
                'montant': result.montant,
                'montant_par': result.montant_par,
                'accessoires': result.accessoires,
                'name': result.name,
                'id_niveau': result.id_niveau,
                'date_debut': result.date_debut,
                'date_fin': result.date_fin,
                'paiement_details': getattr(result, 'paiement_details', {}) or {},
                'mois': getattr(result, 'mois', {}) or {}
                # 'paiement_details': getattr(result, 'paiement_details', None),
                # 'mois': getattr(result, 'mois', None)
            }
            data = PaymentInfoData(**row_dict)
        
        return PaymentInfoResponse(
            data=data,
            paiementExiste=paiement_existe
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Format d'année académique invalide: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

# GET par ID
@router.get("/paiement/{paiement_id}", response_model=ShowPaiementResponse)
def get_paiement(paiement_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role(FINANCIAL_ROLES))):
    paiement = (
        db.query(Paiement)
        .filter(Paiement.id == paiement_id)
        # .options(
        #     joinedload(Paiement.etudiant),
        #     joinedload(Paiement.niveau),
        #     joinedload(Paiement.classe)
        # )
        .first()
    )
    
    if not paiement:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
# show_paiement
    return ShowPaiementResponse(show_paiement=paiement)
    # return PaiementResource(
    #     id=paiement.id,
    #     id_=paiement.etudiant.id if paiement.etudiant else None,
    #     identifiant=paiement.etudiant.identifiant if paiement.etudiant else None,
    #     nom=paiement.etudiant.nom if paiement.etudiant else None,
    #     prenom=paiement.etudiant.prenom if paiement.etudiant else None,
    #     annee=paiement.annee_academique,
    #     niveaux=paiement.niveau.name if paiement.niveau else None,
    #     classes=paiement.classe.nom_classe if paiement.classe else None,
    #     mois=paiement.mois,
    #     accessoires=paiement.paiement_details
    # )

class PaimentEtudiant(BaseModel):
    etudiant_id:str
    annee_academique: Optional[str]=None 
@router.post("/student-paiments", response_model=ShowPaiementResponse)
def get_paiement(data: PaimentEtudiant, db: Session = Depends(get_db), current_user: User = Depends(require_role(FINANCIAL_ROLES))):
    paiement = (
        db.query(Paiement)
        .filter(Paiement.etudiant_id == data.etudiant_id,
                Paiement.annee_academique == data.annee_academique
                )
        # .options(
        #     joinedload(Paiement.etudiant),
        #     joinedload(Paiement.niveau),
        #     joinedload(Paiement.classe)
        # )
        .first()
    )
    return ShowPaiementResponse(show_paiement=paiement)

@router.get("/fetch-data-with-payment-params/{etudiant_id}", response_model=StudentPaymentResponse)
def fetch_data_for_student_with_payment_params(
    etudiant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(FINANCIAL_ROLES))
):
    # Vérifier si l'étudiant existe sans faculté
    has_no_faculty = db.query(
        exists(
            select(Etudiant.id)
            .outerjoin(EtudiantFaculte, EtudiantFaculte.etudiant_id == Etudiant.id)
            .where(EtudiantFaculte.faculte_id.is_(None))
            .where(Etudiant.id == etudiant_id)
        )
    ).scalar()

    if has_no_faculty:
        query = (
            select(
                Etudiant.id.label('studentId'),
                Etudiant.nom,
                Etudiant.prenom,
                Etudiant.identifiant,
                Classe.nom_classe,
                Classe.id.label('classeId'),
                ParametrePaiement.echeance,
                ParametrePaiement.montant,
                ParametrePaiement.devise,
                Niveau.name,
                Niveau.id.label('niveauId'),
                AnneeAcademique.date_debut,
                AnneeAcademique.annee_academique,
                AnneeAcademique.id.label('anneeId'),
                AnneeAcademique.date_fin
            )
            .select_from(Etudiant)
            .join(ClasseEtudiant, ClasseEtudiant.etudiant_id == Etudiant.id)
            .join(Niveau, Niveau.id == ClasseEtudiant.niveau_id)
            .join(AnneeAcademique, AnneeAcademique.id == ClasseEtudiant.annee_academique_id)
            .join(Classe, Classe.id == ClasseEtudiant.classes_id)
            .outerjoin(
                ParametrePaiement,
                (ParametrePaiement.anneeAcademique == ClasseEtudiant.annee_academique_id) &
                (ParametrePaiement.niveau_id == ClasseEtudiant.niveau_id) &
                (ParametrePaiement.classe == ClasseEtudiant.classes_id)
            )
            .where(ClasseEtudiant.etudiant_id == etudiant_id)
            .where(Etudiant.id == etudiant_id)
        )
    else:
        query = (
            select(
                Etudiant.id.label('studentId'),
                Etudiant.nom,
                Etudiant.prenom,
                Etudiant.identifiant,
                Classe.nom_classe,
                Classe.id.label('classeId'),
                ParametrePaiement.echeance,
                ParametrePaiement.montant,
                ParametrePaiement.devise,
                Niveau.name,
                Niveau.id.label('niveauId'),
                AnneeAcademique.date_debut,
                AnneeAcademique.annee_academique,
                AnneeAcademique.id.label('anneeId'),
                AnneeAcademique.date_fin,
                EtudiantFaculte.faculte_id
            )
            .select_from(Etudiant)
            .join(EtudiantFaculte, EtudiantFaculte.etudiant_id == Etudiant.id)
            .join(Classe, Classe.id == EtudiantFaculte.classes_id)
            .join(Niveau, Niveau.id == EtudiantFaculte.niveau_id)
            .join(AnneeAcademique, AnneeAcademique.id == EtudiantFaculte.annee_academique_id)
            .outerjoin(
                ParametrePaiement,
                (ParametrePaiement.anneeAcademique == EtudiantFaculte.annee_academique_id) &
                (ParametrePaiement.niveau_id == EtudiantFaculte.niveau_id) &
                (ParametrePaiement.classe == EtudiantFaculte.classes_id) &
                (ParametrePaiement.faculte_id == EtudiantFaculte.faculte_id)
            )
            .where(EtudiantFaculte.etudiant_id == etudiant_id)
            .where(Etudiant.id == etudiant_id)
        )

    results = db.execute(query).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    data = []
    print(results)
    for row in results:
        row_dict = {
            'studentId': row.studentId,
            'nom': row.nom,
            'prenom': row.prenom,
            'identifiant': row.identifiant,
            'nom_classe': row.nom_classe,
            'classeId': row.classeId,
            'echeance': row.echeance,
            'montant': row.montant,
            'devise': row.devise,
            'name': row.name,
            'niveauId': row.niveauId,
            'date_debut': row.date_debut,
            'annee_academique': row.annee_academique,
            'anneeId': row.anneeId,
            'date_fin': row.date_fin,
            'faculte_id': getattr(row, 'faculte_id', None)
        }
        data.append(StudentPaymentData(**row_dict))

    return StudentPaymentResponse(data=data)


# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from sqlalchemy import select, exists, func
# from typing import Optional
# from pydantic import BaseModel, Field
# from datetime import date



#  https://aplekol360.local/api/v1/next-payment-step?niveau=e7f8d26b-e3c5-11ef-9913-3e7db61a5f8d&annee_a=8ef65c55-8166-4557-bc2f-5482d605cd76&etudiant=f07821f8-0e48-42c1-9caf-c227dd9dbcb8&classe=c2201015-7d3a-4bc2-810c-e2a8278b0410&annee_academique=2025-2026&faculte=None - server replied: Not Found GET v1/next-payment-step?niveau=e7f8d26b-e3c5-11ef-9913-3e7db61a5f8d&annee_a=8ef65c55-8166-4557-bc2f-5482d605cd76&etudiant=f07821f8-0e48-42c1-9caf-c227dd9dbcb8&classe=c2201015-7d3a-4bc2-810c-e2a8278b0410&annee_academique=2025-2026&faculte=None

    

