from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProduitSchema(BaseModel):
    id: str
    nom: str
    category: str
    prix: float
    quantite_stock: float
    description: Optional[str] = None
    created_at: str

    @classmethod
    def from_model(cls, p):
        return cls(
            id=p.id,
            nom=p.nom,
            category=p.category,
            prix=float(p.prix),
            quantite_stock=float(p.quantite_stock),
            description=p.description,
            created_at=p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "",
        )

    model_config = ConfigDict(from_attributes=True)


class ProduitCreateSchema(BaseModel):
    nom: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    prix: float = Field(..., gt=0)
    quantite_stock: float = Field(0, ge=0)
    description: Optional[str] = Field(None, max_length=500)


class ProduitUpdateSchema(ProduitCreateSchema):
    pass


class PaginatedProduitResponse(BaseModel):
    data: list[ProduitSchema]
    meta: dict
