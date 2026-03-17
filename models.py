from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String) # nombre
    last_name = Column(String)  # apellidos
    email = Column(String, unique=True, index=True)
    password = Column(String)
    entity = Column(String)     # entidad
    role = Column(String, default="client") # client o technician
    
    # --- MI NA SPECIFIC FIELDS ---
    research_group = Column(String, nullable=True)     # grupo
    principal_investigator = Column(String, nullable=True) # ip (investigador principal)
    internal_account = Column(String, nullable=True)    # cuenta
    project_code = Column(String, nullable=True)        # proyecto
    profile_picture = Column(String, nullable=True)     # foto_perfil

    # Relación: Un usuario tiene muchas peticiones
    requests = relationship("Request", back_populates="client", foreign_keys="[Request.client_id]")

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="requested") 

    # --- PHASE 1: INITIAL REQUEST (CLIENT) ---
    service_name = Column(String)
    initial_hours = Column(Float)
    initial_comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    client_id = Column(Integer, ForeignKey("users.id"))

    # --- PHASE 2: TECHNICAL OFFER (TECHNICIAN) ---
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    offered_hours = Column(Float, nullable=True)
    technical_adjustment = Column(String, nullable=True)
    quoted_price = Column(Float, default=0.0) 
    offered_at = Column(DateTime, nullable=True)

    # --- PHASE 3: ACCEPTANCE (CLIENT) ---
    is_accepted = Column(Boolean, default=False)
    accepted_at = Column(DateTime, nullable=True)

    # --- PHASE 4: TRACEABILITY (CLOUD PATHS) ---
    path_initial_doc = Column(String, nullable=True)
    path_offer_doc = Column(String, nullable=True)
    path_acceptance_doc = Column(String, nullable=True)

    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="requests")
    technician = relationship("User", foreign_keys=[technician_id])