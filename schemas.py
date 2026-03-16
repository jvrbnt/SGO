from pydantic import BaseModel
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    apellidos: str
    email: str
    password: str
    entidad: str
    
    # Campos opcionales (por defecto serán None si no se envían)
    grupo: Optional[str] = None
    ip: Optional[str] = None
    cuenta: Optional[str] = None
    proyecto: Optional[str] = None

class UsuarioLogin(BaseModel):
    email: str
    password: str