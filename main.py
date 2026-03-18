from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import models, schemas
from database import engine, LocalSession

# 1. Create tables in PostgreSQL using the updated models
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Database dependency
def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_index():
    return FileResponse("static/html/ServicioLogin.html")

# --- 3. API ROUTES ---

# --- REGISTRATION ROUTE ---
@app.post("/api/signup")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_user = models.User(
        name=user.name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
        entity=user.entity,
        # Save the extra fields:
        group=user.group,
        ip=user.ip,
        account=user.account,
        project=user.project,
        profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
    )
    db.add(new_user)
    db.commit()
    return {"message": "Account created successfully"}

# --- LOGIN ROUTE ---
@app.post("/api/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email,
        models.User.password == user.password
    ).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Return the full object for direct JS loading
    return {
        "email": db_user.email,
        "name": db_user.name,
        "lastName": db_user.last_name,
        "entity": db_user.entity,
        "group": db_user.group,
        "ip": db_user.ip,
        "account": db_user.account,
        "project": db_user.project,
        "profilePicture": db_user.profile_picture,
        "requests": [] # (Next step will be creating a table for requests)
    }
