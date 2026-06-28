from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.Models.MModels import User
from app.Models.MFinancials import Produit
from app.Schemas.SProduit import ProduitSchema, ProduitCreateSchema, ProduitUpdateSchema, PaginatedProduitResponse
from app.dependencies.Dependencie import get_current_user, user_has_permission
from app.Helper.context import UserContext, ActionContext

router = APIRouter(prefix="/api/v1", tags=["Produits"])


@router.get("/produits", response_model=PaginatedProduitResponse)
def index_produits(
    search: str | None = None,
    page: int = 1,
    per_page: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Produit)
    if search:
        query = query.filter(
            or_(
                Produit.nom.ilike(f"%{search}%"),
                Produit.category.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    skip = (page - 1) * per_page
    produits = query.order_by(Produit.nom.asc()).offset(skip).limit(per_page).all()

    return {
        "data": [ProduitSchema.from_model(p) for p in produits],
        "meta": {
            "current_page": page,
            "last_page": (total + per_page - 1) // per_page if total else 1,
            "per_page": per_page,
            "total": total,
            "from": skip + 1 if produits else 0,
            "to": skip + len(produits) if produits else 0,
        },
    }


@router.post("/produits", response_model=ProduitSchema, status_code=201)
def store_produit(
    data: ProduitCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Ajouter paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to create product")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("create")

    produit = Produit(**data.model_dump())
    db.add(produit)
    db.commit()
    db.refresh(produit)
    return ProduitSchema.from_model(produit)


@router.put("/produits/{produit_id}", response_model=ProduitSchema)
def update_produit(
    produit_id: str,
    data: ProduitUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Modifier paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to update product")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("update")

    produit = db.query(Produit).filter(Produit.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    for field, value in data.model_dump().items():
        setattr(produit, field, value)
    db.commit()
    db.refresh(produit)
    return ProduitSchema.from_model(produit)


@router.delete("/produits/{produit_id}")
def delete_produit(
    produit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Supprimer paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to delete product")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("delete")

    produit = db.query(Produit).filter(Produit.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    db.delete(produit)
    db.commit()
    return {"success": "Opération réussie"}
