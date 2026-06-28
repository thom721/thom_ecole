from pydantic import BaseModel, Field, ConfigDict


class CategorieProduitSchema(BaseModel):
    id: str
    nom: str

    model_config = ConfigDict(from_attributes=True)


class CategorieProduitCreateSchema(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
