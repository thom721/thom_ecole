from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SaveDataIn(BaseModel):
    nom: str
    prenom: str
    email: str
    mac: str


class ClientOut(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    mac: str
    suspended: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClientListOut(ClientOut):
    """`suspended` ne reflète que le blocage manuel par un admin — distinct
    de la validité réelle de la licence, ajoutée ici pour éviter toute
    confusion sur le tableau de bord (voir docs/infini-software-PRD.md)."""
    licence_expiration: Optional[str] = None
    licence_active: Optional[bool] = None


class LicenceKeyOut(BaseModel):
    id: int
    key: str
    expiration_date: str
    days_valid: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentOut(BaseModel):
    id: int
    provider: str
    amount: float
    currency: str
    status: str
    provider_reference: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClientHistoriqueOut(ClientOut):
    licence_keys: list[LicenceKeyOut] = []
    payments: list[PaymentOut] = []


class AdminLoginIn(BaseModel):
    email: str
    password: str


class AdminLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PaiementCreateIn(BaseModel):
    mac: str
    provider: str  # "moncash" | "natcash" | "stripe"
    months: int = 1


class PricingConfigOut(BaseModel):
    monthly_price: float
    currency: str
    exchange_rate_usd_htg: float
    auto_release: bool = False
    updated_at: datetime

    class Config:
        from_attributes = True


class PricingConfigIn(BaseModel):
    monthly_price: float
    currency: str = "USD"
    exchange_rate_usd_htg: float
    auto_release: bool = False


class ActiverPlanIn(BaseModel):
    """Activation manuelle d'un plan par l'admin (paiement reçu hors-ligne :
    cash, chèque, virement...). mac + email doivent correspondre à un client
    déjà enregistré, par sécurité contre une faute de frappe sur le mac."""
    mac: str
    email: str
    months: int = 1


class PaymentPendingOut(BaseModel):
    """Paiement confirmé par le fournisseur mais en attente d'activation admin (auto_release=False)."""
    id: int
    provider: str
    amount: float
    currency: str
    days_valid: int
    created_at: datetime
    client_id: int
    client_nom: str
    client_prenom: str
    client_email: str
    client_mac: str

    class Config:
        from_attributes = True
