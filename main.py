from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import models, schemas
from database import engine, LocalSession

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_index():
    return FileResponse("static/html/ServicioLogin.html")

# --- RUTA DE REGISTRO ---
@app.post("/api/signup")
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.email == user.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    nuevo_usuario = models.Usuario(
        nombre=user.nombre,
        apellidos=user.apellidos,
        email=user.email,
        password=user.password, 
        entidad=user.entidad,
        # Guardamos los campos extra:
        grupo=user.grupo,
        ip=user.ip,
        cuenta=user.cuenta,
        proyecto=user.proyecto,
        foto_perfil="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
    )
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": "Cuenta creada con éxito"}

# --- RUTA DE LOGIN ---
@app.post("/api/login")
def login(user: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.Usuario).filter(
        models.Usuario.email == user.email, 
        models.Usuario.password == user.password
    ).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    # Devolvemos el objeto completo para que el JS lo cargue directamente
    return {
        "email": db_user.email,
        "nombre": db_user.nombre,
        "apellidos": db_user.apellidos,
        "entidad": db_user.entidad,
        "grupo": db_user.grupo,
        "ip": db_user.ip,
        "cuenta": db_user.cuenta,
        "proyecto": db_user.proyecto,
        "fotoPerfil": db_user.foto_perfil,
        "peticiones": [] # (El siguiente paso será hacer una tabla para las peticiones)
    }