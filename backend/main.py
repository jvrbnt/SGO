import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError

from backend import models, schemas
from backend.database import engine, LocalSession, DB_AVAILABLE

# --- SECURITY CONFIGURATION ---
load_dotenv()
SECRET_PEPPER = os.getenv("SECRET_PEPPER")

if not SECRET_PEPPER:
    raise RuntimeError("ERROR: SECRET_PEPPER variable not found in .env file!")

# Argon2id Hybrid Configuration
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID
)

# Database Initialization
if DB_AVAILABLE:
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        import backend.database as database
        database.DB_AVAILABLE = False

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

def get_db():
    if not DB_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Database is not available"
        )
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_index():
    return FileResponse("frontend/templates/ServicioLogin.html")

@app.get("/login")
async def read_login():
    return FileResponse("frontend/templates/ServicioLogin.html")

@app.get("/cliente")
async def read_cliente():
    return FileResponse("frontend/templates/ServicioCliente.html")

@app.get("/tecnico")
async def read_tecnico():
    return FileResponse("frontend/templates/ServicioTecnico.html")

@app.get("/registro")
async def read_registro():
    return FileResponse("frontend/templates/ServicioSign.html")

@app.get("/editar-cliente")
async def read_edit_cliente():
    return FileResponse("frontend/templates/ServicioEdit.html")

@app.get("/editar-tecnico")
async def read_edit_tecnico():
    return FileResponse("frontend/templates/servicioEditT.html")

@app.get("/Cookies.html")
async def read_cookies():
    return FileResponse("frontend/templates/Cookies.html")

@app.get("/Proteccion.html")
async def read_proteccion():
    return FileResponse("frontend/templates/Proteccion.html")

@app.get("/AvisoLegal.html")
async def read_avisolegal():
    return FileResponse("frontend/templates/AvisoLegal.html")

@app.get("/Contacto.html")
async def read_contacto():
    return FileResponse("frontend/templates/Contacto.html")

# --- AUTHENTICATION ROUTES ---

@app.post("/api/client/signup")
def create_client(client_data: schemas.ClientCreateWeb, db: Session = Depends(get_db)):
    if db.query(models.Client).filter(models.Client.email == client_data.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")

    # Argon2id Hashing with Pepper
    password_with_pepper = client_data.password + SECRET_PEPPER
    hashed_pwd = ph.hash(password_with_pepper)

    new_client = models.Client(
        first_name=client_data.first_name,
        last_name=client_data.last_name,
        email=client_data.email,
        hashed_password=hashed_pwd, 
        entity=client_data.entity,
        internal_account=client_data.internal_account,
        ip_address=client_data.ip_address,
        group_name=client_data.group_name,
        project_id=client_data.project_id,
        profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
    )
    db.add(new_client)
    db.commit()
    return {"message": "Client account created successfully"}

@app.post("/api/login")
def unified_login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    password_with_pepper = login_data.password + SECRET_PEPPER

    # 1. Client Verification
    client = db.query(models.Client).filter(models.Client.email == login_data.email).first()
    if client:
        try:
            ph.verify(client.hashed_password, password_with_pepper)
            return {
                "id": client.id,
                "role": "client",
                "email": client.email,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "profile_picture": client.profile_picture
            }
        except VerifyMismatchError:
            pass

    # 2. Technician Verification
    tech = db.query(models.Technician).filter(models.Technician.email == login_data.email).first()
    if tech:
        try:
            ph.verify(tech.hashed_password, password_with_pepper)
            return {
                "id": tech.id,
                "role": "technician",
                "email": tech.email,
                "first_name": tech.first_name,
                "last_name": tech.last_name,
                "profile_picture": tech.profile_picture,
                "privilege_level": tech.privilege_level
            }
        except VerifyMismatchError:
            pass

    raise HTTPException(status_code=401, detail="Incorrect credentials")

# --- ADMIN MANAGEMENT ROUTES ---

@app.get("/api/admin/technicians", response_model=List[schemas.TechnicianResponse])
def admin_get_technicians(db: Session = Depends(get_db)):
    return db.query(models.Technician).all()

@app.post("/api/admin/technicians")
def admin_create_technician(tech_in: schemas.TechnicianCreate, db: Session = Depends(get_db)):
    if db.query(models.Technician).filter(models.Technician.email == tech_in.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")

    password_with_pepper = tech_in.password + SECRET_PEPPER
    hashed_pwd = ph.hash(password_with_pepper)

    new_tech = models.Technician(
        first_name=tech_in.first_name,
        last_name=tech_in.last_name,
        email=tech_in.email,
        hashed_password=hashed_pwd,
        privilege_level="Technician"  # Force default to Technician when creating via Admin panel
    )
    db.add(new_tech)
    db.commit()
    return {"message": "Technician created successfully"}

@app.patch("/api/admin/technicians/{tech_id}/role")
def admin_update_technician_role(tech_id: int, privilege_level: str, db: Session = Depends(get_db)):
    if privilege_level not in ["Mod", "Technician"]:
        raise HTTPException(status_code=400, detail="Invalid role assignment")
        
    tech = db.query(models.Technician).filter(models.Technician.id == tech_id).first()
    if not tech:
        raise HTTPException(status_code=404, detail="Technician not found")
        
    if tech.privilege_level == "Admin":
        raise HTTPException(status_code=403, detail="Cannot alter an Admin's role")
        
    tech.privilege_level = privilege_level
    db.commit()
    return {"message": f"Role updated to {privilege_level}"}

# --- SERVICE CATALOG ROUTES ---

@app.get("/api/catalog", response_model=List[schemas.ServiceCatalogResponse])
def get_catalog(db: Session = Depends(get_db)):
    return db.query(models.ServiceCatalog).all()

@app.put("/api/catalog/{item_id}", response_model=schemas.ServiceCatalogResponse)
def update_catalog_price(item_id: int, price_update: schemas.ServiceCatalogPriceUpdate, db: Session = Depends(get_db)):
    catalog_item = db.query(models.ServiceCatalog).filter(models.ServiceCatalog.id == item_id).first()
    if not catalog_item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    if price_update.price1 is not None:
        catalog_item.price1 = price_update.price1
    if price_update.price2 is not None:
        catalog_item.price2 = price_update.price2
    if price_update.price3 is not None:
        catalog_item.price3 = price_update.price3
    if price_update.price4 is not None:
        catalog_item.price4 = price_update.price4

    db.commit()
    db.refresh(catalog_item)
    return catalog_item

# --- OFFER MANAGEMENT ROUTES (CLIENT) ---

@app.post("/api/client/offers")
def create_offer(offer_in: schemas.OfferCreate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.email == offer_in.client_email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found in database")

    # Check if this client already has an active offer managed by someone
    active_offer = db.query(models.Offer).filter(
        models.Offer.client_id == client.id,
        models.Offer.manager_id.isnot(None),
        models.Offer.status.notin_(["invoiced", "finished"])
    ).first()
    
    manager_id = active_offer.manager_id if active_offer else None

    new_offer = models.Offer(client_id=client.id, status="requested", manager_id=manager_id)
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)

    for s in offer_in.services:
        catalog_item = db.query(models.ServiceCatalog).filter(
            models.ServiceCatalog.name == s.service_name
        ).first()
        
        new_service = models.Service(
            service_name=s.service_name,
            hours=s.hours,
            original_hours=s.hours,
            comment=s.comment,
            offer_id=new_offer.id,
            catalog_id=catalog_item.id if catalog_item else None
        )
        db.add(new_service)
    
    db.commit()
    return {"message": "Offer requested successfully", "offer_id": new_offer.id}

@app.get("/api/client/my-offers", response_model=List[schemas.OfferResponse])
def get_client_offers(email: str, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.email == email).first()
    if not client:
        return []
    return db.query(models.Offer).filter(models.Offer.client_id == client.id).all()

# --- OFFER MANAGEMENT ROUTES (TECHNICIAN) ---

@app.get("/api/technician/offers", response_model=List[schemas.OfferResponse])
def get_all_offers(db: Session = Depends(get_db)):
    return db.query(models.Offer).all()

@app.get("/api/technician/offers/{offer_id}", response_model=schemas.OfferResponse)
def get_single_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer

@app.put("/api/technician/offers/{offer_id}/review")
def finalize_review_and_send(offer_id: int, review_data: schemas.OfferReviewUpdate, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    offer.status = "quoted"
    offer.technician_comment = review_data.technician_comment

    for s_data in review_data.services:
        service = db.query(models.Service).filter(models.Service.id == s_data.id).first()
        if service and not service.is_deleted:
            service.hours = s_data.hours
            service.comment = s_data.comment
            if s_data.quoted_price is not None:
                service.quoted_price = s_data.quoted_price

    db.commit()
    return {"message": "Offer sent to client as QUOTED"}

@app.patch("/api/technician/offers/{offer_id}")
def update_status_simple(offer_id: int, new_status: str, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    offer.status = new_status
    db.commit()
    return {"message": "Status updated"}

@app.patch("/api/technician/offers/{offer_id}/assign")
def assign_offer(offer_id: int, tech_id: int, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    client_id = offer.client_id
    offer.manager_id = tech_id
    
    # Auto-assign this tech to ALL other 'requested' offers from the same client
    requested_offers = db.query(models.Offer).filter(
        models.Offer.client_id == client_id,
        models.Offer.status == "requested",
        models.Offer.manager_id.is_(None)
    ).all()
    
    for req_offer in requested_offers:
        req_offer.manager_id = tech_id
        
    db.commit()
    return {"message": "Offer(s) assigned successfully"}

@app.patch("/api/technician/services/{service_id}/assign")
def assign_service(service_id: int, tech_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.technician_id = tech_id
    db.commit()
    return {"message": "Service assigned successfully"}

@app.patch("/api/technician/services/{service_id}/unassign")
def unassign_service(service_id: int, tech_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if service.offer.status != "requested":
        raise HTTPException(status_code=400, detail="Cannot unassign from an offer that is already quoted, accepted, or finished.")
    if service.technician_id != tech_id:
        raise HTTPException(status_code=403, detail="Only the assigned technician can unassign themselves")
    service.technician_id = None
    db.commit()
    return {"message": "Service unassigned successfully"}

@app.patch("/api/technician/offers/{offer_id}/unassign")
def unassign_offer(offer_id: int, tech_id: int, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.status != "requested":
        raise HTTPException(status_code=400, detail="Cannot unassign from an offer that is already quoted, accepted, or finished.")
    if offer.manager_id != tech_id:
        raise HTTPException(status_code=403, detail="Only the current manager can unassign themselves")
        
    # Check if there are any active (quoted/accepted) offers managed by this tech for this client
    active_in_progress = db.query(models.Offer).filter(
        models.Offer.client_id == offer.client_id,
        models.Offer.manager_id == tech_id,
        models.Offer.status.in_(["quoted", "accepted"])
    ).first()
    
    if active_in_progress:
        raise HTTPException(status_code=400, detail="Cannot unassign: you are managing active (quoted/accepted) offers for this client.")
        
    # Valid to unassign: Unassign from ALL 'requested' offers for this client
    all_requested = db.query(models.Offer).filter(
        models.Offer.client_id == offer.client_id,
        models.Offer.manager_id == tech_id,
        models.Offer.status == "requested"
    ).all()
    
    for req_offer in all_requested:
        req_offer.manager_id = None
        
    db.commit()
    return {"message": "Unassigned from all requested offers for client"}

@app.delete("/api/technician/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service.offer.status not in ["requested", "quoted"]:
        raise HTTPException(status_code=400, detail=f"Cannot delete services from an offer in '{service.offer.status}' status")
        
    service.is_deleted = True
    db.commit()
    return {"message": "Service logically deleted"}

@app.post("/api/technician/offers/{offer_id}/services")
def add_service_to_offer(offer_id: int, service_in: schemas.ServiceCreateInline, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if offer.status not in ["requested", "quoted"]:
        raise HTTPException(status_code=400, detail=f"Cannot add services to an offer in '{offer.status}' status")

    catalog_item = db.query(models.ServiceCatalog).filter(
        models.ServiceCatalog.name == service_in.service_name
    ).first()
    
    new_service = models.Service(
        service_name=service_in.service_name,
        hours=service_in.hours,
        original_hours=service_in.hours,
        comment=service_in.comment,
        offer_id=offer.id,
        catalog_id=catalog_item.id if catalog_item else None,
        added_by_technician=True
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return {"message": "Service added successfully", "service_id": new_service.id}

# --- INVOICE / BILLING ROUTES ---

@app.get("/api/technician/billing-clients", response_model=List[schemas.ClientResponse])
def get_billing_clients(tech_id: int, db: Session = Depends(get_db)):
    # Returns clients who have at least one active offer (not invoiced/finished) managed by this tech
    clients = db.query(models.Client).join(models.Offer).filter(
        models.Offer.manager_id == tech_id,
        models.Offer.status.notin_(["invoiced", "finished"])
    ).distinct().all()
    return clients

@app.get("/api/technician/billing-offers", response_model=List[schemas.OfferResponse])
def get_billing_offers(tech_id: int, client_id: int, db: Session = Depends(get_db)):
    # Returns underlying offers for a chosen client
    offers = db.query(models.Offer).filter(
        models.Offer.client_id == client_id,
        models.Offer.manager_id == tech_id,
        models.Offer.status.notin_(["invoiced", "finished"])
    ).all()
    return offers

def get_all_offers(db: Session = Depends(get_db)):
    return db.query(models.Offer).all()

@app.get("/api/technician/offers/{offer_id}", response_model=schemas.OfferResponse)
def get_single_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer

@app.put("/api/technician/offers/{offer_id}/review")
def finalize_review_and_send(offer_id: int, review_data: schemas.OfferReviewUpdate, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    offer.status = "quoted"
    offer.technician_comment = review_data.technician_comment

    for s_data in review_data.services:
        service = db.query(models.Service).filter(models.Service.id == s_data.id).first()
        if service and not service.is_deleted:
            service.hours = s_data.hours
            service.comment = s_data.comment
            if s_data.quoted_price is not None:
                service.quoted_price = s_data.quoted_price

    db.commit()
    return {"message": "Offer sent to client as QUOTED"}

@app.patch("/api/technician/offers/{offer_id}")
def update_status_simple(offer_id: int, new_status: str, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    offer.status = new_status
    db.commit()
    return {"message": "Status updated"}

@app.patch("/api/technician/offers/{offer_id}/assign")
def assign_offer(offer_id: int, tech_id: int, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    client_id = offer.client_id
    offer.manager_id = tech_id
    
    # Auto-assign this tech to ALL other 'requested' offers from the same client
    requested_offers = db.query(models.Offer).filter(
        models.Offer.client_id == client_id,
        models.Offer.status == "requested",
        models.Offer.manager_id.is_(None)
    ).all()
    
    for req_offer in requested_offers:
        req_offer.manager_id = tech_id
        
    db.commit()
    return {"message": "Offer(s) assigned successfully"}

@app.patch("/api/technician/services/{service_id}/assign")
def assign_service(service_id: int, tech_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.technician_id = tech_id
    db.commit()
    return {"message": "Service assigned successfully"}

@app.patch("/api/technician/services/{service_id}/unassign")
def unassign_service(service_id: int, tech_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if service.offer.status != "requested":
        raise HTTPException(status_code=400, detail="Cannot unassign from an offer that is already quoted, accepted, or finished.")
    if service.technician_id != tech_id:
        raise HTTPException(status_code=403, detail="Only the assigned technician can unassign themselves")
    service.technician_id = None
    db.commit()
    return {"message": "Service unassigned successfully"}

@app.patch("/api/technician/offers/{offer_id}/unassign")
def unassign_offer(offer_id: int, tech_id: int, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.status != "requested":
        raise HTTPException(status_code=400, detail="Cannot unassign from an offer that is already quoted, accepted, or finished.")
    if offer.manager_id != tech_id:
        raise HTTPException(status_code=403, detail="Only the current manager can unassign themselves")
        
    # Check if there are any active (quoted/accepted) offers managed by this tech for this client
    active_in_progress = db.query(models.Offer).filter(
        models.Offer.client_id == offer.client_id,
        models.Offer.manager_id == tech_id,
        models.Offer.status.in_(["quoted", "accepted"])
    ).first()
    
    if active_in_progress:
        raise HTTPException(status_code=400, detail="Cannot unassign: you are managing active (quoted/accepted) offers for this client.")
        
    # Valid to unassign: Unassign from ALL 'requested' offers for this client
    all_requested = db.query(models.Offer).filter(
        models.Offer.client_id == offer.client_id,
        models.Offer.manager_id == tech_id,
        models.Offer.status == "requested"
    ).all()
    
    for req_offer in all_requested:
        req_offer.manager_id = None
        
    db.commit()
    return {"message": "Unassigned from all requested offers for client"}

@app.delete("/api/technician/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service.offer.status not in ["requested", "quoted"]:
        raise HTTPException(status_code=400, detail=f"Cannot delete services from an offer in '{service.offer.status}' status")
        
    service.is_deleted = True
    db.commit()
    return {"message": "Service logically deleted"}

@app.post("/api/technician/offers/{offer_id}/services")
def add_service_to_offer(offer_id: int, service_in: schemas.ServiceCreateInline, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if offer.status not in ["requested", "quoted"]:
        raise HTTPException(status_code=400, detail=f"Cannot add services to an offer in '{offer.status}' status")

    catalog_item = db.query(models.ServiceCatalog).filter(
        models.ServiceCatalog.name == service_in.service_name
    ).first()
    
    new_service = models.Service(
        service_name=service_in.service_name,
        hours=service_in.hours,
        original_hours=service_in.hours,
        comment=service_in.comment,
        offer_id=offer.id,
        catalog_id=catalog_item.id if catalog_item else None,
        added_by_technician=True
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return {"message": "Service added successfully", "service_id": new_service.id}

# --- INVOICE / BILLING ROUTES ---

@app.get("/api/technician/billing-clients", response_model=List[schemas.ClientResponse])
def get_billing_clients(tech_id: int, db: Session = Depends(get_db)):
    # Returns clients who have at least one active offer (not invoiced/finished) managed by this tech
    clients = db.query(models.Client).join(models.Offer).filter(
        models.Offer.manager_id == tech_id,
        models.Offer.status.notin_(["invoiced", "finished"])
    ).distinct().all()
    return clients

@app.get("/api/technician/billing-offers", response_model=List[schemas.OfferResponse])
def get_billing_offers(tech_id: int, client_id: int, db: Session = Depends(get_db)):
    # Returns underlying offers for a chosen client
    offers = db.query(models.Offer).filter(
        models.Offer.client_id == client_id,
        models.Offer.manager_id == tech_id,
        models.Offer.status.notin_(["invoiced", "finished"])
    ).all()
    return offers

@app.post("/api/technician/invoices")
def create_invoice(invoice_data: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    import traceback
    try:
        # 1. Create Invoice
        new_invoice = models.Invoice(
            client_id=invoice_data.client_id,
            technician_id=invoice_data.technician_id,
            total_price=invoice_data.total_price,
            comment=invoice_data.comment,
            status="invoiced"
        )
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)
        
        # 2. Attach and update targeted Offers
        for o_id in invoice_data.offer_ids:
            offer = db.query(models.Offer).filter(models.Offer.id == o_id).first()
            if offer:
                offer.status = "invoiced"
                offer.invoice_id = new_invoice.id
                
        db.commit()
        db.refresh(new_invoice)
        
        tech = db.query(models.Technician).filter(models.Technician.id == new_invoice.technician_id).first()
        return {
            "id": new_invoice.id,
            "client_id": new_invoice.client_id,
            "technician_id": new_invoice.technician_id,
            "technician_first_name": tech.first_name if tech else None,
            "technician_last_name": tech.last_name if tech else None,
            "total_price": new_invoice.total_price,
            "comment": new_invoice.comment,
            "status": new_invoice.status,
            "created_at": new_invoice.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ERROR: {traceback.format_exc()}")

@app.get("/api/client/invoices")
def get_client_invoices(email: str, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.email == email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    invoices = db.query(models.Invoice).filter(models.Invoice.client_id == client.id).all()
    result = []
    for inv in invoices:
        tech = db.query(models.Technician).filter(models.Technician.id == inv.technician_id).first()
        offers_data = []
        for o in inv.offers:
            offers_data.append({
                "id": o.id,
                "status": o.status,
                "technician_comment": o.technician_comment,
                "services": [{
                    "id": s.id, "service_name": s.service_name, "hours": s.hours,
                    "quoted_price": s.quoted_price, "is_deleted": s.is_deleted,
                    "added_by_technician": s.added_by_technician, "original_hours": s.original_hours,
                    "comment": s.comment
                } for s in o.services if not s.is_deleted]
            })
        result.append({
            "id": inv.id,
            "client_id": inv.client_id,
            "technician_id": inv.technician_id,
            "technician_first_name": tech.first_name if tech else None,
            "technician_last_name": tech.last_name if tech else None,
            "total_price": inv.total_price,
            "comment": inv.comment,
            "status": inv.status,
            "created_at": inv.created_at.isoformat(),
            "offers": offers_data
        })
    return result

@app.get("/api/technician/invoices/all")
def get_all_invoices(db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).order_by(models.Invoice.created_at.desc()).all()
    result = []
    for inv in invoices:
        tech = db.query(models.Technician).filter(models.Technician.id == inv.technician_id).first()
        result.append({
            "id": inv.id,
            "client_id": inv.client_id,
            "technician_id": inv.technician_id,
            "technician_first_name": tech.first_name if tech else None,
            "technician_last_name": tech.last_name if tech else None,
            "total_price": inv.total_price,
            "comment": inv.comment,
            "status": inv.status,
            "created_at": inv.created_at.isoformat()
        })
    return result

@app.post("/api/technician/invoices/{invoice_id}/finish")
def finish_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice.status = "finished"
    
    for offer in invoice.offers:
        offer.status = "finished"
        
    db.commit()
    return {"message": "Invoice and linked offers finished successfully"}
