from pydantic import BaseModel
from typing import Optional, List,Dict,Any

class ClientInfoSchema(BaseModel):
    id: str
    client_mac: str
    client_name: str
    authorisation: bool
    certi_key: Optional[str] = None
    ss_certi: Optional[dict] = None

    class Config:
        from_attributes = True

class AuthorisationResponse(BaseModel):
    success: str
    authorisation: bool
    id: str

class ClientListResponse(BaseModel):
    data_client: List[ClientInfoSchema]

# class AskingResponse(BaseModel):
#     status: int
#     data: Optional[str] = None
#     certy_ss: Optional[dict] = None

class AskingResponse(BaseModel):
    status: int
    data: Optional[Any] = None  # str (certi_key) pour /asking, dict (client_dict) pour /client-authorisation-connect/{mac}
    certy_ss: Optional[Dict[str, Any]] = None

 
