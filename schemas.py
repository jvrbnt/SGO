from pydantic import BaseModel
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