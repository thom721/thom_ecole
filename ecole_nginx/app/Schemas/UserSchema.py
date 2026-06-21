from pydantic import BaseModel,computed_field
from typing import Optional,List
from app.config.Config import BASE_URL

class RoleSchema(BaseModel):
    id: str
    name: str
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    username: Optional[str]=None
    profile_photo_path:Optional[str]=None
    status:Optional[int]=0
    roles: Optional[List[RoleSchema]] = []

    @computed_field
    @property
    def profile_image_url(self) -> str:
        if not self.profile_photo_path:
            return None 
        return f"{BASE_URL}/static/profile/{self.profile_photo_path}"

    class Config:
        from_attributes = True

