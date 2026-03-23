from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime # Importación necesaria para OfferResponse

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
    password: str # Mandatory for web signup

class ClientCreateAdmin(ClientBase):
    password: Optional[str] = None # Optional for technician-led registration

# --- TECHNICIAN SCHEMAS ---
class TechnicianCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

# --- LOGIN SCHEMAS ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# --- SERVICE CATALOG SCHEMAS ---
class ServiceCatalogBase(BaseModel):
    name: str
    price_per_hour: float

class ServiceCatalogResponse(ServiceCatalogBase):
    id: int
    class Config:
        from_attributes = True

# --- SERVICE & OFFER SCHEMAS ---
class ServiceBase(BaseModel):
    service_name: str
    hours: float
    comment: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: int
    status: str
    technician_id: Optional[int] = None
    catalog_id: Optional[int] = None # Añadido para trazabilidad con el catálogo
    class Config:
        from_attributes = True

class OfferCreate(BaseModel):
    services: List[ServiceCreate]

class OfferResponse(BaseModel):
    id: int
    status: str
    created_at: datetime # Corregido: ya no requiere el prefijo datetime.
    client_id: int
    manager_id: Optional[int] = None
    services: List[ServiceResponse]
    class Config:
        from_attributes = True