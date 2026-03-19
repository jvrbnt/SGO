from pydantic import BaseModel, EmailStr
from typing import Optional, List

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