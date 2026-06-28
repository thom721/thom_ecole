from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.Models.MModels import User
from app.Models.MFinancials import CategorieProduit
from app.Schemas.SCategorieProduit import CategorieProduitSchema, CategorieProduitCreateSchema
from app.dependencies.Dependencie import get_current_user, user_has_permission
from app.Helper.context import UserContext, ActionContext

router = APIRouter(prefix="/api/v1", tags=["Catégories Produits"])


@router.get("/categories-produits", response_model=list[CategorieProduitSchema])
def index_categories_produits(db: Session = Depends(get_db)):
    return db.query(CategorieProduit).order_by(CategorieProduit.nom.asc()).all()


@router.post("/categories-produits", response_model=CategorieProduitSchema, status_code=201)
def store_categorie_produit(
    data: CategorieProduitCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Ajouter paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to create category")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("create")

    existing = db.query(CategorieProduit).filter(CategorieProduit.nom == data.nom).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cette catégorie existe déjà")

    categorie = CategorieProduit(nom=data.nom)
    db.add(categorie)
    db.commit()
    db.refresh(categorie)
    return categorie


@router.delete("/categories-produits/{categorie_id}")
def delete_categorie_produit(
    categorie_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not user_has_permission(current_user, "Supprimer paiement", db):
        raise HTTPException(status_code=403, detail="Unauthorized to delete category")
    UserContext.set_user_id(current_user.id)
    ActionContext.set_action("delete")

    categorie = db.query(CategorieProduit).filter(CategorieProduit.id == categorie_id).first()
    if not categorie:
        raise HTTPException(status_code=404, detail="Catégorie introuvable")

    db.delete(categorie)
    db.commit()
    return {"success": "Opération réussie"}
