from pydantic import BaseModel, EmailStr,computed_field
from typing import Optional
from datetime import datetime 
from app.config.Config import BASE_URL
import base64 

# from dotenv import load_dotenv
import os

# load_dotenv()  # charge automatiquement les variables depuis .env


# BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
# STORAGE_PATH = os.getenv("STORAGE_PATH", "storage")

def save_base64_image(base64_str: str, output_dir: str, filename: str) -> str:
    """
    Convertit un string base64 en fichier image et le sauvegarde dans output_dir.
    Retourne le chemin relatif du fichier sauvegardé.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Décoder le Base64
    image_data = base64.b64decode(base64_str)
    
    # Déterminer l'extension (si ton Base64 contient le header, ex: data:image/png;base64,...)
    if base64_str.startswith("data:image/"):
        ext = base64_str.split(";")[0].split("/")[1]  # png, jpg, etc.
        filename = f"{filename}.{ext}"
    
    file_path = os.path.join(output_dir, filename)
    
    # Écrire le fichier
    with open(file_path, "wb") as f:
        f.write(image_data)

    return file_path


class ProfileBase(BaseModel):
    nom: str
    email: EmailStr
    ligne1: str
    ligne2: Optional[str] = None
    adresse: str
    slogan: Optional[str] = None
    description: Optional[str] = None
    info_de_fondation: Optional[str] = None
    logo_image_path: str
    logo_image_base64: Optional[str] = None
    school_url: Optional[str] = None
    is_receive_arriere: Optional[bool] = False


class ProfileCreate(ProfileBase):
    pass  # Pour création

class ProfileUpdate(ProfileBase):
    pass  # Pour mise à jour

class ProfileOut(ProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime
    @computed_field
    @property
    def logo_image_url(self) -> str:
        if not self.logo_image_path:
            return None 
        return f"{BASE_URL}/static/{self.logo_image_path}"

    class Config:
        from_attributes = True  # Permet de retourner les objets SQLAlchemy directement

class ShowProfile(BaseModel):
    data:ProfileOut
    # class Config:
    #     from_attributes = True


