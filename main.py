from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import engine, LocalSession, DB_AVAILABLE

# Inicialización de la base de datos
if DB_AVAILABLE:
    try:
        # Crea las tablas si no existen: clients, technicians, service_catalog, offers, services
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        import database
        database.DB_AVAILABLE = False

app = FastAPI()

# Configuración de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependencia para obtener la sesión de base de datos
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
    return FileResponse("static/html/ServicioLogin.html")

# --- RUTAS DE AUTENTICACIÓN ---

@app.post("/api/client/signup")
def create_client(client_data: schemas.ClientCreateWeb, db: Session = Depends(get_db)):
    if db.query(models.Client).filter(models.Client.email == client_data.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_client = models.Client(
        first_name=client_data.first_name,
        last_name=client_data.last_name,
        email=client_data.email,
        hashed_password=client_data.password, 
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
    # 1. Busca primero si el email pertenece a un Cliente
    client = db.query(models.Client).filter(
        models.Client.email == login_data.email,
        models.Client.hashed_password == login_data.password
    ).first()
    
    if client:
        return {
            "role": "client",
            "email": client.email,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "profile_picture": client.profile_picture
        }

    # 2. Si no es cliente, busca si es un Técnico
    tech = db.query(models.Technician).filter(
        models.Technician.email == login_data.email,
        models.Technician.hashed_password == login_data.password
    ).first()
    
    if tech:
        return {
            "role": "technician",
            "email": tech.email,
            "first_name": tech.first_name,
            "last_name": tech.last_name,
            "profile_picture": tech.profile_picture
        }

    # 3. Si no existe en ninguna de las dos tablas, da error
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# --- RUTAS DEL CATÁLOGO DE SERVICIOS ---

@app.get("/api/catalog", response_model=List[schemas.ServiceCatalogResponse])
def get_catalog(db: Session = Depends(get_db)):
    return db.query(models.ServiceCatalog).all()

# --- RUTAS DE GESTIÓN DE OFERTAS (CLIENTE) ---

@app.post("/api/client/offers")
def create_offer(offer_in: schemas.OfferCreate, db: Session = Depends(get_db)):
    # Localizamos al cliente exacto usando el email que nos manda el frontend
    client = db.query(models.Client).filter(models.Client.email == offer_in.client_email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found in database")

    # Creación de la oferta base vinculada al ID real del cliente
    new_offer = models.Offer(client_id=client.id, status="requested")
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)

    # Procesamiento de cada servicio solicitado
    for s in offer_in.services:
        # Buscamos el servicio en el catálogo para guardar la referencia
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
    # Buscamos las ofertas usando el email que pasamos por parámetro en la URL
    client = db.query(models.Client).filter(models.Client.email == email).first()
    if not client:
        return []
    return db.query(models.Offer).filter(models.Offer.client_id == client.id).all()

# --- RUTAS DE GESTIÓN DE OFERTAS (TÉCNICO) ---

@app.get("/api/technician/offers", response_model=List[schemas.OfferResponse])
def get_all_offers(db: Session = Depends(get_db)):
    # Devuelve todas las solicitudes para el panel de staff
    return db.query(models.Offer).all()

@app.patch("/api/technician/offers/{offer_id}")
def update_offer_status(offer_id: int, new_status: str, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    offer.status = new_status
    db.commit()
    return {"message": f"Offer {offer_id} updated to {new_status}"}

# --- TECHNICIAN REVIEW OPERATIONS ---

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
def finalize_review_and_send(offer_id: int, review_data: dict, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Actualizamos estado a QUOTED (Presupuestada)
    offer.status = "quoted"
    offer.technician_comment = review_data.get("technician_comment")

    # Actualizamos servicios (horas y notas)
    for s_data in review_data.get("services", []):
        service = db.query(models.Service).filter(models.Service.id == s_data["id"]).first()
        if service:
            service.hours = s_data["hours"]
            service.comment = s_data["comment"]

    db.commit()
    return {"message": "Offer sent to client as QUOTED"}

@app.patch("/api/technician/offers/{offer_id}")
def update_status_simple(offer_id: int, new_status: str, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    offer.status = new_status
    db.commit()
    return {"message": "Status updated"}