import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from argon2 import PasswordHasher, Type
from backend.database import LocalSession
import backend.models as models

# --- SECURITY CONFIGURATION ---
load_dotenv()
SECRET_PEPPER = os.getenv("SECRET_PEPPER")

if not SECRET_PEPPER:
    raise RuntimeError("¡ERROR: No se encontró la variable SECRET_PEPPER en el archivo .env!")

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID
)

def seed_demo_users():
    db = LocalSession()
    try:
        print("--- Cargando Usuarios de Prueba ---")
        # 1. Demo Technician
        if not db.query(models.Technician).filter(models.Technician.email == "admin@mina.es").first():
            hashed_admin = ph.hash("admin" + SECRET_PEPPER)
            admin = models.Technician(
                first_name="Javier",
                last_name="Admin",
                email="admin@mina.es",
                hashed_password=hashed_admin, 
                profile_picture="https://cdn-icons-png.flaticon.com/512/4086/4086679.png"
            )
            db.add(admin)

        # 2. Demo Client
        if not db.query(models.Client).filter(models.Client.email == "cliente@csic.es").first():
            hashed_client = ph.hash("password123" + SECRET_PEPPER)
            cliente = models.Client(
                first_name="Miguel",
                last_name="Investigador",
                email="cliente@csic.es",
                hashed_password=hashed_client,
                entity="CSIC",
                profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
            )
            db.add(cliente)
        
        db.commit()
        print("ÉXITO: Usuarios demo cargados.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_users()