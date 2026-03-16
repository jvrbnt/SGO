from sqlalchemy import Column, Integer, String
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    apellidos = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    entidad = Column(String)
    
    # --- CAMPOS EXTRA (Opcionales, pueden estar vacíos si no es de MiNa) ---
    grupo = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    cuenta = Column(String, nullable=True)
    proyecto = Column(String, nullable=True)
    
    # Campo para guardar la URL de la foto de perfil
    foto_perfil = Column(String, nullable=True)