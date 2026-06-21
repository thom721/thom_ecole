 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional, Literal
from decimal import Decimal
from app.database import get_db
from app.dependencies.Dependencie import get_current_user,user_has_permission,validate_exists,check_permission,first_or_create,user_has_role,first_or_update_safe,DualAuthChecker
from app.Models.MFinancials import OtherTransaction
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case, literal_column,or_
from pydantic import BaseModel, EmailStr, Field,computed_field , model_validator
from typing import List
from sqlalchemy.orm import joinedload
from app.Models.MModels import User
from app.Helper.context import UserContext,ActionContext,AdminAuthorization

class UserSimple(BaseModel):
    id: str
    name: str
    email: str
    class Config:
        from_attributes = True

class EtudiantSimple(BaseModel):
    id: Optional[str]=None
    nom: Optional[str]=None
    prenom: Optional[str]=None

    class Config:
        from_attributes = True

# class TransactionBase(BaseModel):
#     description: str = Field(..., enumerate(["Initiale", "Badge perdu", "Relevé de notes", "Diplôme", "Autre"]))
#     description_personnaliser:str
#     identifiant:Optional[str]=None
#     montant: Decimal
 

class TransactionBase(BaseModel):
    description: Literal["Initiale", "Badge perdu", "Relevé de notes", "Diplôme", "Autre"]
    description_supplementaire: Optional[str] = None
    identifiant: Optional[str] = None
    montant: Decimal

    @model_validator(mode='after')
    def check_description_custom(self) -> 'TransactionBase':
        desc = self.description
        custom = self.description_supplementaire
         
        if desc == "Autre" and (custom is None or custom.strip() == ""):
            raise ValueError(
                "Le champ description supplémentaire est obligatoire quand la description est 'Autre'."
            )
        return self

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(BaseModel):
    id: str
    description: str
    montant: float
    user_id: str
    created_at: datetime 
    user: Optional[UserSimple] 
    etudiant: Optional[EtudiantSimple]
    class Config:
        from_attributes = True

    @computed_field
    @property
    def date(self) -> str:
        if self.created_at:
            if isinstance(self.created_at, str):
                dt = datetime.fromisoformat(self.created_at)
            else:
                dt = self.created_at
            return dt.strftime("%d %b %Y")
        return ""
    
    @computed_field
    @property
    def utilisateur(self) -> str:
        return self.user.name if self.user else ""
        

class PaginatedResponse(BaseModel):
    data: List[TransactionResponse]
    total: int
    current_page: int
    last_page: int

router_transac = APIRouter(prefix="/api/v1", tags=["Transaction"])


from datetime import date
from sqlalchemy import cast, Date

@router_transac.get("/other-transaction", response_model=PaginatedResponse)
def read_all_transactions(
    current_page: int = Query(1, ge=1), 
    per_page: int = Query(10, ge=1, le=100),
    search_date: Optional[date] = Query(None, description="Recherche par date (YYYY-MM-DD)"),
    q: Optional[str] = Query(None, description="Recherche dans la description"),
    service: Session = Depends(get_db)
):
    offset = (current_page - 1) * per_page
    
 
    query = service.query(OtherTransaction).options(joinedload(OtherTransaction.user))

 
    if search_date:
        query = query.filter(cast(OtherTransaction.created_at, Date) == search_date)
 
    if q:
        query = query.filter(OtherTransaction.description.ilike(f"%{q}%"))

    total_count = query.count()
    
    # 4. Récupération des données paginées
    transactions = (
        query.order_by(OtherTransaction.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    
    last_page = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    return {
        "data": transactions, # Chaque transaction contient maintenant sa variable 'user'
        "total": total_count,
        "current_page": current_page,
        "last_page": last_page
    }
@router_transac.get("/other-transactions", response_model=PaginatedResponse)
def read_all_transactions(
    page: int = Query(1, ge=1), 
    per_page: int = Query(10, ge=1, le=100),
    service: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    offset = (page - 1) * per_page
    
    total_count = service.query(func.count(OtherTransaction.id)).scalar()
    
    # 2. On récupère les transactions ET les utilisateurs liés
    transactions = (
        service.query(OtherTransaction)
        .options(joinedload(OtherTransaction.user),joinedload(OtherTransaction.etudiant))
        .order_by(OtherTransaction.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    
    last_page = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    return {
        "data": transactions,
        "total": total_count,
        "current_page": page,
        "last_page": last_page
    }
# --- GET PAGINÉ ---
 
 
@router_transac.get("/other-transaction/{trans_id}", response_model=TransactionResponse)
def get_one_transaction(
    trans_id: str, 
    service: Session = Depends(get_db),current_user:User= Depends(get_current_user)
):
    # On cherche la transaction par son ID
    db_trans = service.query(OtherTransaction).filter(OtherTransaction.id == trans_id).first()
    
    if not db_trans:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
        
    return db_trans
# --- POST (CORRIGÉ) ---
@router_transac.post("/other-transaction", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate, 
    service: Session = Depends(get_db),
    current_user: Session = Depends(get_current_user)
):
    try:
        UserContext.set_user_id(current_user.id)
        print(transaction, UserContext.get_user_id())
        new_obj = OtherTransaction(
            description=transaction.description,
            montant=transaction.montant,
            identifiant=transaction.identifiant,
            description_supplementaire=transaction.description_supplementaire,
            user_id=current_user.id  
        )
        service.add(new_obj)
        service.commit()
        service.refresh(new_obj) # Recharge l'objet pour avoir l'ID et les timestamps
        return new_obj
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router_transac.patch("/edit-other-transaction/{trans_id}", response_model=TransactionResponse)
def update_transaction(
    trans_id: str,
    transaction_update: TransactionCreate,
    service: Session = Depends(get_db),
    auth_data: dict = Depends(DualAuthChecker("Modifier transaction")),
    # current_user: Session = Depends(get_current_user)
):
    
    current_user = auth_data["user_id"]
    current_admin = auth_data["admin_id"]

    UserContext.set_user_id(current_user)
    AdminAuthorization.set_admin_id(current_admin) 
    db_trans = service.query(OtherTransaction).filter(OtherTransaction.id == trans_id).first()

 
    
    if not db_trans:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")

    # 2. Vérification de sécurité (optionnel : seulement si l'admin ou le créateur peut modifier)
    if db_trans.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Pas autorisé à modifier cette transaction")

    # 3. Mise à jour des champs
    db_trans.description = transaction_update.description
    db_trans.montant = transaction_update.montant
    db_trans.identifiant=transaction_update.identifiant,
    db_trans.description_supplementaire=transaction_update.description_supplementaire,
    
    try:
        service.commit()
        service.refresh(db_trans)
        return db_trans
    except Exception as e:
        service.rollback()
        raise HTTPException(status_code=400, detail=str(e))
# --- DELETE ---
@router_transac.delete("/transactions/{trans_id}")
def delete_transaction(
    trans_id: str, 
    service: Session = Depends(get_db),
    auth_data: dict = Depends(DualAuthChecker("Supprimer transaction")),
    # current_user: Session = Depends(get_current_user)
):
    current_user = auth_data["user_id"]
    current_admin = auth_data["admin_id"]

    UserContext.set_user_id(current_user)
    AdminAuthorization.set_admin_id(current_admin)


    # if not user_has_permission(current_user, 'Supprimer transaction',service):
    #     raise HTTPException(status_code=201, detail="Vous n\'avez pas les permissions requise.")
    
    deleted = None # service.delete(trans_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    return {"status": "success", "message": "Transaction supprimée"}