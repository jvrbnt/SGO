from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, List
from datetime import datetime

# --- CLIENT SCHEMAS ---
class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    entity: str
    # Fields for Internal (MiNa) clients — IP, CI, CP, Grupo
    investigador_principal: Optional[str] = None  # IP — supervising researcher
    cuenta_interna: Optional[str] = None          # CI — internal billing account
    codigo_proyecto: Optional[str] = None         # CP — project code
    grupo: Optional[str] = None                   # Research group within MiNa

class ClientCreateWeb(ClientBase):
    password: str

    @model_validator(mode="after")
    def validate_internal_fields(self):
        """Enforce that Internal (MiNa) clients must provide IP, CI, CP, and Grupo."""
        if self.entity == "Internal":
            missing = []
            if not self.investigador_principal:
                missing.append("IP (Investigador Principal)")
            if not self.cuenta_interna:
                missing.append("CI (Cuenta Interna)")
            if not self.codigo_proyecto:
                missing.append("CP (Código de Proyecto)")
            if not self.grupo:
                missing.append("Grupo")
            if missing:
                raise ValueError(
                    f"Internal clients must provide: {', '.join(missing)}"
                )
        return self

class ClientResponse(ClientBase):
    id: int
    profile_picture: Optional[str] = None
    class Config:
        from_attributes = True

# --- TECHNICIAN SCHEMAS ---
class TechnicianResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    profile_picture: Optional[str] = None
    privilege_level: str

    class Config:
        from_attributes = True

# --- LOGIN AND CATALOG ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ServiceCatalogResponse(BaseModel):
    id: int
    name: str
    price_internal: float
    price_csic: Optional[float] = None
    price_public: Optional[float] = None
    price_private: Optional[float] = None
    class Config:
        from_attributes = True

class ServiceCatalogPriceUpdate(BaseModel):
    price_internal: Optional[float] = None
    price_csic: Optional[float] = None
    price_public: Optional[float] = None
    price_private: Optional[float] = None

# --- SERVICE SCHEMAS ---
class ServiceBase(BaseModel):
    service_name: str
    hours: float
    comment: Optional[str] = None

class ServiceCreateInline(BaseModel):
    service_name: str
    hours: float = 0.0
    original_hours: Optional[float] = None
    comment: Optional[str] = None

class ServiceResponse(ServiceBase):
    id: int
    catalog_id: Optional[int] = None
    technician_id: Optional[int] = None
    quoted_price: Optional[float] = None
    original_hours: Optional[float] = None
    status: str = "pending"
    is_deleted: bool = False
    added_by_technician: bool = False
    technician: Optional[TechnicianResponse] = None
    catalog_item: Optional[ServiceCatalogResponse] = None
    class Config:
        from_attributes = True

# --- INVOICE SCHEMAS ---
class InvoiceBase(BaseModel):
    client_id: int
    technician_id: int
    total_price: float
    comment: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    offer_ids: List[int]

class InvoiceResponse(InvoiceBase):
    id: int
    status: str
    created_at: datetime
    technician_first_name: Optional[str] = None
    technician_last_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- OFFER SCHEMAS ---
class OfferCreate(BaseModel):
    client_email: EmailStr
    services: List[ServiceBase]

class OfferResponse(BaseModel):
    id: int
    reference: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    technician_comment: Optional[str] = None
    client_id: int
    manager_id: Optional[int] = None
    invoice_id: Optional[int] = None

    # Nested data representations
    client: ClientResponse
    services: List[ServiceResponse]
    manager: Optional[TechnicianResponse] = None

    class Config:
        from_attributes = True

# Schema for service update in review panel
class ServiceUpdate(BaseModel):
    id: int
    hours: float
    quoted_price: Optional[float] = None
    comment: Optional[str] = None

# Schema for review panel updates
class OfferReviewUpdate(BaseModel):
    services: List[ServiceUpdate]
    technician_comment: Optional[str] = None
    status: str = "quoted"

class TechnicianCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    privilege_level: str = "Technician"