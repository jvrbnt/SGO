import models
import schemas
from database import LocalSession
from pydantic import ValidationError

def seed_technician():
    db = LocalSession()
    print("--- MiNa SGO: Technician Initializer with Validation ---")

    # 1. Collect inputs
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email (e.g., user@domain.com): ")
    password = input("Password: ")

    # 2. Validate using Pydantic Schema
    # This ensures the email format is correct before touching the DB
    try:
        validated_data = schemas.TechnicianCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
    except ValidationError as e:
        print("\n[!] VALIDATION ERROR: The provided data is invalid.")
        for error in e.errors():
            # Shows exactly which field failed (e.g., 'email') and why
            print(f"    - {error['loc'][0]}: {error['msg']}")
        return

    # 3. Check if email already exists in the technicians table
    existing_tech = db.query(models.Technician).filter(
        models.Technician.email == validated_data.email
    ).first()
    
    if existing_tech:
        print(f"\n[!] ERROR: Technician with email {validated_data.email} already exists.")
        return

    # 4. Create database record using validated data
    new_tech = models.Technician(
        first_name=validated_data.first_name,
        last_name=validated_data.last_name,
        email=validated_data.email,
        hashed_password=validated_data.password # Currently stored as plain text
    )

    try:
        db.add(new_tech)
        db.commit()
        print(f"\nSUCCESS: Technician '{validated_data.first_name}' created successfully.")
        print("You can now use these credentials in the Staff Access login.")
    except Exception as e:
        db.rollback()
        print(f"\n[!] DATABASE ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_technician()