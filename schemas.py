from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    last_name: str
    email: str
    password: str
    entity: str

    # Optional fields (default to None if not sent)
    group: Optional[str] = None
    ip: Optional[str] = None
    account: Optional[str] = None
    project: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    # Lo que devolvemos al frontend tras el login
    id: int
    first_name: str
    last_name: str
    email: str
    entity: str
    role: str
    research_group: Optional[str] = None
    principal_investigator: Optional[str] = None
    internal_account: Optional[str] = None
    project_code: Optional[str] = None
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True