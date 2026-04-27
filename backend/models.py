from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
import datetime
from backend.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    entity = Column(String, nullable=False)

    # Fields specific to Internal (MiNa) clients — required when entity is "Internal"
    # IP = Investigador Principal, CI = Cuenta Interna, CP = Codigo de Proyecto
    investigador_principal = Column(String, nullable=True)  # IP — supervising researcher
    cuenta_interna = Column(String, nullable=True)          # CI — internal billing account
    codigo_proyecto = Column(String, nullable=True)         # CP — project code
    grupo = Column(String, nullable=True)                   # Research group within MiNa

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
    privilege_level = Column(String, nullable=False, default="Technician")

    # Offers where the technician acts as the main manager
    managed_offers = relationship("Offer", back_populates="manager")
    # Specific services assigned individually to this technician
    assigned_services = relationship("Service", back_populates="technician")

class ServiceCatalog(Base):
    __tablename__ = "service_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price_internal = Column(Float, nullable=False)  # MiNa internal users
    price_csic = Column(Float, nullable=False)      # External CSIC / UAM users
    price_public = Column(Float, nullable=False)    # Universities / OPIS
    price_private = Column(Float, nullable=False)   # Companies

    # Reference to services requested based on this catalog item
    services = relationship("Service", back_populates="catalog_item")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=False)
    total_price = Column(Float, nullable=False, default=0.0)
    comment = Column(Text, nullable=True)
    status = Column(String, default="invoiced")
    created_at = Column(DateTime, default=datetime.datetime.now)

    # Relationships
    client = relationship("Client")
    technician = relationship("Technician")
    offers = relationship("Offer", back_populates="invoice")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, index=True, nullable=True) # e.g., '001_2026'
    # Status flow: requested → quoted → accepted → invoiced → finished
    status = Column(String, default="requested")

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    technician_comment = Column(Text, nullable=True)
    # Foreign keys to identify client and technical manager
    client_id = Column(Integer, ForeignKey("clients.id"))
    manager_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    # Relationships
    client = relationship("Client", back_populates="offers")
    manager = relationship("Technician", back_populates="managed_offers")
    services = relationship("Service", back_populates="offer", cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="offers")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False)  # Name of requested service (catalog copy)
    hours = Column(Float, default=0.0)
    original_hours = Column(Float, default=0.0)
    quoted_price = Column(Float, nullable=True)  # Final price set by technician
    comment = Column(Text, nullable=True)
    status = Column(String, default="pending")  # Status flow: pending → doing → done
    is_deleted = Column(Boolean, default=False)  # Logically deleted by technician
    added_by_technician = Column(Boolean, default=False)  # Added by technician during review

    # Link with parent offer, assigned technician, and catalog origin
    offer_id = Column(Integer, ForeignKey("offers.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)
    catalog_id = Column(Integer, ForeignKey("service_catalog.id"), nullable=True)

    # Relationships
    offer = relationship("Offer", back_populates="services")
    technician = relationship("Technician", back_populates="assigned_services")
    catalog_item = relationship("ServiceCatalog", back_populates="services")