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
    raise RuntimeError("¡ERROR: No se encontró la variable SECRET_PEPPER en el archivo .env!")

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
                "profile_picture": tech.profile_picture
            }
        except VerifyMismatchError:
            pass

    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# --- SERVICE CATALOG ROUTES ---

@app.get("/api/catalog", response_model=List[schemas.ServiceCatalogResponse])
def get_catalog(db: Session = Depends(get_db)):
    return db.query(models.ServiceCatalog).all()

# --- OFFER MANAGEMENT ROUTES (CLIENT) ---

@app.post("/api/client/offers")
def create_offer(offer_in: schemas.OfferCreate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.email == offer_in.client_email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found in database")

    new_offer = models.Offer(client_id=client.id, status="requested")
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

    for s_data in review_data.get("services", []):
        service = db.query(models.Service).filter(models.Service.id == s_data["id"]).first()
        if service:
            service.hours = s_data.hours
            service.comment = s_data.comment

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
    offer.manager_id = tech_id
    db.commit()
    return {"message": "Offer assigned successfully"}

@app.patch("/api/technician/services/{service_id}/assign")
def assign_service(service_id: int, tech_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.technician_id = tech_id
    db.commit()
    return {"message": "Service assigned successfully"}