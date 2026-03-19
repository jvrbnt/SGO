from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Nullable for offline/email clients
    entity = Column(String, nullable=False)

    # MiNa Specific Fields
    internal_account = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    project_id = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    # Relationships
    offers = relationship("Offer", back_populates="client")

class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) # Always required
    profile_picture = Column(String, nullable=True)

    # Relationships
    managed_offers = relationship("Offer", back_populates="manager")
    assigned_services = relationship("Service", back_populates="technician")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="requested") # requested, technical_offer, accepted, finished
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Foreign Keys
    client_id = Column(Integer, ForeignKey("clients.id"))
    manager_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="offers")
    manager = relationship("Technician", back_populates="managed_offers")
    services = relationship("Service", back_populates="offer", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False)
    hours = Column(Float, default=0.0)
    comment = Column(Text, nullable=True)
    status = Column(String, default="pending")
    
    # Foreign Keys
    offer_id = Column(Integer, ForeignKey("offers.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)

    # Relationships
    offer = relationship("Offer", back_populates="services")
    technician = relationship("Technician", back_populates="assigned_services")