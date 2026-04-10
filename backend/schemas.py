from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- ESQUEMAS DE CLIENTE ---
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
    password: str # Necesario para el registro desde la web

class ClientResponse(ClientBase):
    id: int
    profile_picture: Optional[str] = None
    class Config:
        from_attributes = True

# --- ESQUEMAS DE TÉCNICO ---
class TechnicianResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    profile_picture: Optional[str] = None
    class Config:
        from_attributes = True

# --- LOGIN Y CATÁLOGO ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ServiceCatalogResponse(BaseModel):
    id: int
    name: str
    price_per_hour: float
    class Config:
        from_attributes = True

# --- ESQUEMAS DE SERVICIOS ---
class ServiceBase(BaseModel):
    service_name: str
    hours: float
    comment: Optional[str] = None

class ServiceResponse(ServiceBase):
    id: int
    catalog_id: Optional[int] = None
    technician_id: Optional[int] = None
    technician: Optional[TechnicianResponse] = None
    class Config:
        from_attributes = True

# --- ESQUEMAS DE OFERTAs ---

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
    
    # Datos anidados para que no salga N/A
    client: ClientResponse 
    services: List[ServiceResponse]
    manager: Optional[TechnicianResponse] = None
    
    class Config:
        from_attributes = True

# Esquema para la actualización de servicios en el panel de revisión
class ServiceUpdate(BaseModel):
    id: int
    hours: float
    comment: Optional[str] = None

# Esquema para la actualización desde el panel de revisión
class OfferReviewUpdate(BaseModel):
    services: List[ServiceUpdate]
    technician_comment: Optional[str] = None
    status: str = "quoted"
    
class TechnicianCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str