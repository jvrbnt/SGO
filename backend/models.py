from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import relationship
import datetime
from backend.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Allow null for manual technician registration
    entity = Column(String, nullable=False)

    # Specific fields for MiNa internal users
    internal_account = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    project_id = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    # Relationship between client and their multiple requests/offers
    offers = relationship("Offer", back_populates="client")

class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)

    # Offers where the technician acts as the main manager
    managed_offers = relationship("Offer", back_populates="manager")
    # Specific services assigned individually to this technician
    assigned_services = relationship("Service", back_populates="technician")

class ServiceCatalog(Base):
    __tablename__ = "service_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # Service name according to catalog
    price_per_hour = Column(Float, nullable=False) # Base price for budget calculations

    # Reference to services requested based on this item
    services = relationship("Service", back_populates="catalog_item")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    # Estados: requested, quoted, accepted, finished
    status = Column(String, default="requested") 
    
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now) 
    
    technician_comment = Column(Text, nullable=True) # El comentario para el cliente  
    # Foreign keys to identify client and technical manager
    client_id = Column(Integer, ForeignKey("clients.id"))
    manager_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)

    # Relaciones
    client = relationship("Client", back_populates="offers")
    manager = relationship("Technician", back_populates="managed_offers")
    services = relationship("Service", back_populates="offer", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False) # Name of requested service (catalog copy)
    hours = Column(Float, default=0.0)
    comment = Column(Text, nullable=True)
    status = Column(String, default="pending") # Estados: pending, doing, done
    
    # Link with parent offer, assigned technician, and catalog origin
    offer_id = Column(Integer, ForeignKey("offers.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)
    catalog_id = Column(Integer, ForeignKey("service_catalog.id"), nullable=True)

    # Relaciones
    offer = relationship("Offer", back_populates="services")
    technician = relationship("Technician", back_populates="assigned_services")
    catalog_item = relationship("ServiceCatalog", back_populates="services")