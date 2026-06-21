
from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator,computed_field
from datetime import datetime, date
from enum import Enum
import math 
from app.database import get_db

# ============================================================================
# ENUMS
# ============================================================================

class ActionType(str, Enum):
    """Types d'actions possibles"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
    VIEW = "view"

class SortOrder(str, Enum):
    """Ordre de tri"""
    ASC = "asc"
    DESC = "desc"

# ============================================================================
# MODÈLES PYDANTIC AMÉLIORÉS
# ============================================================================

class LogBase(BaseModel):
    """Modèle de base pour un log"""
    id: str
    date: Optional[datetime] = None
    # user: Optional[str] = None
    action: Optional[str] = None
    model: Optional[str] = None
    model_type: Optional[str] = None
    model_id: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    paiement_key: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserResource(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}

class AdminResource(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}

class LogResource(BaseModel):
    """Resource pour l'API (version simplifiée)"""
    id: str
    # date: Optional[datetime] = None
    user: Optional[str] = None
    authorization_id: Optional[str] = None
    action: Optional[str] = None
    # model: Optional[str] = None
    model_type: Optional[str] = None
    model_id: Optional[str] = None
    # date: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

    @computed_field
    @property
    def date(self) -> str:
        if self.updated_at:
            if isinstance(self.updated_at, str):
                dt = datetime.fromisoformat(self.updated_at)
            else:
                dt = self.updated_at
            return dt.strftime("%d %b %Y")
        return ""
    @computed_field
    @property
    def model(self) -> str:
        try:
            return self.model_type.rsplit(".", 1)[-1]
        except Exception:
            return ""
    # class Config:
    #     from_attributes = True

class PaginationLinks(BaseModel):
    """Liens de pagination"""
    first: Optional[str] = None
    last: Optional[str] = None
    prev: Optional[str] = None
    next: Optional[str] = None

class PaginationMeta(BaseModel):
    """Métadonnées de pagination"""
    current_page: int
    per_page: int
    total: int
    last_page: int
    from_: int = Field(..., alias="from")
    to: int
    path: Optional[str] = None
    
    class Config:
        populate_by_name = True

class PaginatedLogsResponse(BaseModel):
    """Réponse paginée pour les logs"""
    data: List[LogResource]
    meta: PaginationMeta
    links: Optional[PaginationLinks] = None

class LogsResponse(BaseModel):
    """Réponse simple (sans pagination)"""
    data: List[LogResource]

class LogShowResponse(BaseModel):
    """Réponse pour un log unique"""
    data: Optional[LogBase]

class LogStatsResponse(BaseModel):
    """Statistiques sur les logs"""
    total_logs: int
    actions_count: dict[str, int]
    models_count: dict[str, int]
    recent_activity: int  # Logs des dernières 24h

