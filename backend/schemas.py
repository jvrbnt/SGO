from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- CLIENT SCHEMAS ---
class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    entity: str
    internal_account: Optional[str] = None
    ip_address: Optional[str] = None
    group_name: Optional[str] = None
    project_id: Optional[str] = None

class ClientCreateWeb(ClientBase):
    password: str # Required for web registration

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
    price1: float
    price2: Optional[float] = None
    price3: Optional[float] = None
    price4: Optional[float] = None
    class Config:
        from_attributes = True

class ServiceCatalogPriceUpdate(BaseModel):
    price1: Optional[float] = None
    price2: Optional[float] = None
    price3: Optional[float] = None
    price4: Optional[float] = None

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