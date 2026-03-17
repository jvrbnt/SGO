from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import models, schemas
from database import engine, LocalSession

# 1. Create tables in PostgreSQL using the updated models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. Database dependency
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

# --- 3. API ROUTES ---

@app.post("/api/signup")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email is already registered in the 'users' table
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password, 
        entity=user.entity,
        research_group=user.research_group,
        principal_investigator=user.principal_investigator,
        internal_account=user.internal_account,
        project_code=user.project_code,
        profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
    )
    db.add(new_user)
    db.commit()
    return {"mensaje": "Cuenta creada con éxito"}

@app.post("/api/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Query the 'users' table using English column names
    db_user = db.query(models.User).filter(
        models.User.email == user.email, 
        models.User.password == user.password
    ).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    # Return data to the frontend (keys match ServicioLogin.js)
    return {
        "email": db_user.email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "entity": db_user.entity,
        "role": db_user.role,
        "research_group": db_user.research_group,
        "principal_investigator": db_user.principal_investigator,
        "internal_account": db_user.internal_account,
        "project_code": db_user.project_code,
        "profile_picture": db_user.profile_picture,
        "requests": []
    }

# --- 4. STATIC FILES AND VIEWS ---

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/html/ServicioLogin.html")