from pydantic import BaseModel, EmailStr, model_validator, field_validator, ConfigDict
import re
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

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Enforce a basic password policy: min 8 characters and at least one digit."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

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
    display_name: Optional[str] = None
    profile_picture: Optional[str] = None
    class Config:
        from_attributes = True

# --- TECHNICIAN SCHEMAS ---
class TechnicianResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    display_name: Optional[str] = None
    profile_picture: Optional[str] = None
    privilege_level: str

    class Config:
        from_attributes = True

# --- LOGIN AND CATALOG ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    # Unified schema for updating user profiles via /api/me
    # This ensures that both generic fields (display_name, profile_picture) 
    # and Internal (MiNa) specific billing fields are handled securely in one place.
    display_name: Optional[str] = None
    profile_picture: Optional[str] = None
    entity: Optional[str] = None
    investigador_principal: Optional[str] = None
    cuenta_interna: Optional[str] = None
    codigo_proyecto: Optional[str] = None
    grupo: Optional[str] = None

    @model_validator(mode="after")
    def validate_client_entity_fields(self):
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
                raise ValueError(f"Internal clients must provide: {', '.join(missing)}")
        return self


class TraceabilityEntryUpdate(BaseModel):
    # Schema representing the fields of an RG-12 Quality Control form for a single service.
    # Allows tracking of sample delivery, verification, and conformity over time.
    service_id: int
    request_date: Optional[datetime] = None
    acceptance_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    mina_autoservicio: Optional[str] = None
    sample_provided: Optional[str] = None
    verification: Optional[str] = None
    charge_note: Optional[str] = None
    conformity: Optional[str] = None
    observations: Optional[str] = None


class TraceabilityEntryResponse(TraceabilityEntryUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    offer_id: int
    service_name: str
    client_name: str
    client_type: str
    group_internal: Optional[str] = None
    internal_account: Optional[str] = None
    project_code: Optional[str] = None
    quoted_price: Optional[float] = None
    hours: Optional[float] = None


class TraceabilityBulkUpdate(BaseModel):
    entries: List[TraceabilityEntryUpdate]

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

    @field_validator("hours")
    @classmethod
    def validate_positive_hours(cls, v):
        if v <= 0:
            raise ValueError("Hours must be greater than 0")
        return v

class ServiceCreateInline(BaseModel):
    service_name: str
    hours: float = 0.0
    original_hours: Optional[float] = None
    comment: Optional[str] = None

    @field_validator("hours")
    @classmethod
    def validate_positive_hours(cls, v):
        if v <= 0:
            raise ValueError("Hours must be greater than 0")
        return v

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

    @field_validator("offer_ids")
    @classmethod
    def validate_offer_ids(cls, v):
        if not v:
            raise ValueError("At least one offer is required")
        if len(set(v)) != len(v):
            raise ValueError("Offer IDs must not contain duplicates")
        return v

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

    @field_validator("services")
    @classmethod
    def validate_services_not_empty(cls, v):
        if not v:
            raise ValueError("At least one service is required")
        return v

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

    @field_validator("hours")
    @classmethod
    def validate_non_negative_hours(cls, v):
        if v < 0:
            raise ValueError("Hours cannot be negative")
        return v

    @field_validator("quoted_price")
    @classmethod
    def validate_non_negative_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Quoted price cannot be negative")
        return v

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

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Enforce a basic password policy: min 8 characters and at least one digit."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v
