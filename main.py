from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import models, schemas
from database import engine, LocalSession, DB_AVAILABLE

# 1. Database Initialization
if DB_AVAILABLE:
    try:
        # This will create the new tables: clients, technicians, offers, services
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"WARNING: Could not connect to database — {e}")
        import database
        database.DB_AVAILABLE = False

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Database dependency
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

# --- 3. API ROUTES ---

# --- CLIENT REGISTRATION (WEB) ---
@app.post("/api/client/signup")
def create_client(client_data: schemas.ClientCreateWeb, db: Session = Depends(get_db)):
    # Check if client already exists
    if db.query(models.Client).filter(models.Client.email == client_data.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_client = models.Client(
        first_name=client_data.first_name,
        last_name=client_data.last_name,
        email=client_data.email,
        hashed_password=client_data.password, # In production, use hashing!
        entity=client_data.entity,
        internal_account=client_data.internal_account,
        ip_address=client_data.ip_address,
        group_name=client_data.group_name,
        project_id=client_data.project_id,
        profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return {"message": "Client account created successfully"}

# --- CLIENT LOGIN ---
@app.post("/api/client/login")
def login_client(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    db_client = db.query(models.Client).filter(
        models.Client.email == login_data.email,
        models.Client.hashed_password == login_data.password
    ).first()

    if not db_client:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return {
        "role": "client",
        "email": db_client.email,
        "first_name": db_client.first_name,
        "last_name": db_client.last_name,
        "entity": db_client.entity,
        "profile_picture": db_client.profile_picture
    }

# --- TECHNICIAN LOGIN ---
@app.post("/api/technician/login")
def login_technician(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    db_tech = db.query(models.Technician).filter(
        models.Technician.email == login_data.email,
        models.Technician.hashed_password == login_data.password
    ).first()

    if not db_tech:
        raise HTTPException(status_code=401, detail="Technician access denied")

    return {
        "role": "technician",
        "email": db_tech.email,
        "first_name": db_tech.first_name,
        "last_name": db_tech.last_name,
        "profile_picture": db_tech.profile_picture
    }