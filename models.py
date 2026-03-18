from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    entity = Column(String)

    # --- EXTRA FIELDS (Optional, can be empty if not from MiNa) ---
    group = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    account = Column(String, nullable=True)
    project = Column(String, nullable=True)

    # Field to store the profile picture URL
    profile_picture = Column(String, nullable=True)
    
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
