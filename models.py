from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Permitir nulo para registros manuales de técnicos
    entity = Column(String, nullable=False)

    # Campos específicos para usuarios internos de MiNa
    internal_account = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    group_name = Column(String, nullable=True)
    project_id = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    # Relación entre el cliente y sus múltiples solicitudes/ofertas
    offers = relationship("Offer", back_populates="client")

class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)

    # Ofertas donde el técnico actúa como responsable principal
    managed_offers = relationship("Offer", back_populates="manager")
    # Servicios específicos asignados individualmente a este técnico
    assigned_services = relationship("Service", back_populates="technician")

class ServiceCatalog(Base):
    __tablename__ = "service_catalog"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # Nombre del servicio según el catálogo
    price_per_hour = Column(Float, nullable=False) # Precio base para cálculos de presupuesto

    # Referencia a los servicios que se han solicitado basados en este ítem
    services = relationship("Service", back_populates="catalog_item")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="requested") # Estados: requested, technical_offer, accepted, finished
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Claves foráneas para identificar al cliente y al responsable técnico
    client_id = Column(Integer, ForeignKey("clients.id"))
    manager_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)

    # Relaciones
    client = relationship("Client", back_populates="offers")
    manager = relationship("Technician", back_populates="managed_offers")
    services = relationship("Service", back_populates="offer", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False) # Nombre del servicio solicitado (copia del catálogo)
    hours = Column(Float, default=0.0)
    comment = Column(Text, nullable=True)
    status = Column(String, default="pending") # Estados: pending, doing, done
    
    # Vinculación con la oferta madre, el técnico asignado y el origen en el catálogo
    offer_id = Column(Integer, ForeignKey("offers.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)
    catalog_id = Column(Integer, ForeignKey("service_catalog.id"), nullable=True)

    # Relaciones
    offer = relationship("Offer", back_populates="services")
    technician = relationship("Technician", back_populates="assigned_services")
    catalog_item = relationship("ServiceCatalog", back_populates="services")