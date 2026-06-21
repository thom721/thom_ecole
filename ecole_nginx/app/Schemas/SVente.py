 
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, validator , ConfigDict,confloat,UUID4

from datetime import datetime
from uuid import UUID 

    

class UserMini(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


class EtudiantMini(BaseModel):
    id: str
    nom: str
    prenom: str
    identifiant: str

    class Config:
        from_attributes = True


class OrderItemSchema(BaseModel):
    id: str
    # ajoute ici les champs nécessaires

    class Config:
        from_attributes = True


class VenteSchema(BaseModel):
    id: str
    order_itemId: str
    nom: str
    quantite: int
    total: float
    utilisateur: str
    date: str
    category: str | None
    user_id: str
    prix: float
    etudiant_id: str

    @classmethod
    def from_model(cls, vente):
        return cls(
            id=vente.id,
            order_itemId=str(vente.order_itemId),
            nom=f"{vente.etudiant.nom} {vente.etudiant.prenom}",
            quantite=sum(int(item.quantite) for item in vente.order_items),
            total=sum(item.total for item in vente.order_items),
            utilisateur=vente.user.name,
            date=vente.created_at.strftime("%Y-%m-%d %H:%M"),
            category=vente.category,
            user_id=vente.user_id,
            prix=float(vente.prix) if vente.prix else 1,
            etudiant_id=vente.etudiant_id,
        )
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    data: list
    meta: dict
# =====================================================DEPENSE==============================================
class DepenseSchema(BaseModel):
    id: str
    description: str
    prix: float
    user_name: str | None
    date: str

    @classmethod
    def from_model(cls, depense):
        return cls(
            id=depense.id,
            description=depense.description,
            prix=depense.prix,
            user_name=depense.user.name if depense.user else None,
            date=depense.created_at.strftime("%Y-%m-%d %H:%M"),
        )
     #     class Config:
#         from_attributes = True
    model_config = ConfigDict(from_attributes=True)

class DepenseSchemaPost(BaseModel):
    id: str | None
    description: str = Field(..., min_length=3)
    prix: float



# ============================================================================================================================================================================================================
class RepaymentSchema(BaseModel):
    id: str
    paid_amount: float
    loans_id:str
    payment_date:Optional[datetime]=None
    payment_method:Optional[str]=None
    collected_by:str
    created_at: str  

    @classmethod
    def from_orm(cls, repayment):
        return cls(
            id=repayment.id,
            paid_amount=repayment.paid_amount,
            loans_id=repayment.loans_id,
          #   payment_date=repayment.payment_date.strftime("%d %b %Y %H:%M"),
            payment_method=repayment.payment_method,
            collected_by=repayment.collected_by,
            created_at=repayment.created_at.strftime("%d %b %Y %H:%M"),
        )

    class Config:
        from_attributes = True


class LoanSchema(BaseModel):
    id: str
    amount: float
    term_months: int
    interest_rate: float
    monthly_payment: float
    remaining_balance: float
    status: str
    user: str | None
    date: str
    repayments: list[RepaymentSchema]

    @classmethod
    def from_model(cls, loan):
        return cls(
            id=loan.id,
            amount=loan.amount,
            term_months=loan.term_months,
            interest_rate=loan.interest_rate,
            monthly_payment=loan.monthly_payment,
            remaining_balance=loan.remaining_balance or loan.amount,
            status=loan.status,
            user=loan.user.name if loan.user else None,
            date=loan.created_at.strftime("%d %b %Y %H:%M"),
            # 🔹 Transformer chaque repayment en schema
            repayments=[RepaymentSchema.from_orm(r) for r in loan.repayments]
        )

    class Config:
        from_attributes = True



# confloat(gt=0) = numérique > 0
# conint(gt=0) = entier > 0
class LoanCreateSchema(BaseModel):
    user_id: UUID4
    amount: float = Field(..., gt=0)  # numeric|min:1
    term_months: int =  Field(...,gt=0)  # integer|min:1
    interest_rate: float = Field(..., ge=0) #= 0  # facultatif, défaut 0
    monthly_payment: float = Field(..., ge=0)  # tu dois calculer ou passer côté client
#     loan.monthly_payment = data.amount * (1 + data.interest_rate/100) / data.term_months

# from pydantic import BaseModel, , confloat
# from typing import Optional

class LoanRepaySchema(BaseModel):
    loans_id: UUID4
    paid_amount: float = Field(..., gt=0)  # numeric|min:0.01
    payment_method: Optional[str] = None

# =============================================================================================================================================================================================================



class OrderItemSchema(BaseModel):
    id: Optional[str] = None
    nom: str = Field(..., max_length=255)
    status: Optional[int]  = None#= Field(1, ge=0, le=2)
    category: str = Field(..., max_length=100)
    prix: float = Field(..., gt=0)
    quantite: int = Field(..., gt=0)
    total: float = Field(..., gt=0)
    
    @model_validator(mode="before")
    def check_etudiant_id(cls, values):
        if not values.get("status") and not values.get("etudiant_id"):
            raise ValueError("etudiant_id is required when id is not provided")
        return values

class VenteSchemaPost(BaseModel):
    id: Optional[str] = None
    user_id: str
    etudiant_id: Optional[str] = None
    items: List[OrderItemSchema]

    # validation conditionnelle : etudiant_id requis si id n'est pas fourni
    @model_validator(mode="before")
    def check_etudiant_id(cls, values):
        if not values.get("id") and not values.get("etudiant_id"):
            raise ValueError("etudiant_id is required when id is not provided")
        return values


