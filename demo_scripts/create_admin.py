import os
from dotenv import load_dotenv
import backend.models as models
import backend.schemas as schemas
from backend.database import LocalSession
from pydantic import ValidationError
from argon2 import PasswordHasher, Type

# --- CONFIGURACIÓN DE SEGURIDAD ---
load_dotenv()
SECRET_PEPPER = os.getenv("SECRET_PEPPER")

# Misma configuración híbrida que el servidor
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID
)

def seed_technician():
    if not SECRET_PEPPER:
        print("\n[!] ERROR: No se encontró SECRET_PEPPER en el archivo .env")
        return

    db = LocalSession()
    print("--- MiNa SGO: Technician Initializer (Secure Hashing) ---")
    # 1. Collect inputs
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email: ")
    password = input("Password: ")

    # 2. Validate using Pydantic Schema
    try:
        validated_data = schemas.TechnicianCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
    except ValidationError as e:
        print("\n[!] VALIDATION ERROR:")
        for error in e.errors():
            print(f"    - {error['loc'][0]}: {error['msg']}")
        return

    # 3. Check if email already exists
    existing_tech = db.query(models.Technician).filter(
        models.Technician.email == validated_data.email
    ).first()
    
    if existing_tech:
        print(f"\n[!] ERROR: El email {validated_data.email} ya está registrado.")
        return

    # 4. Hasheo Híbrido con Pepper
    password_with_pepper = validated_data.password + SECRET_PEPPER
    hashed_pwd = ph.hash(password_with_pepper)

    # 5. Create database record
    new_tech = models.Technician(
        first_name=validated_data.first_name,
        last_name=validated_data.last_name,
        email=validated_data.email,
        hashed_password=hashed_pwd
    )

    try:
        db.add(new_tech)
        db.commit()
        print(f"\nSUCCESS: Técnico '{validated_data.first_name}' creado con Argon2id + Pepper.")
    except Exception as e:
        db.rollback()
        print(f"\n[!] DATABASE ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_technician()