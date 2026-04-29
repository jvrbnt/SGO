from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas, auth as auth_service
from backend.dependencies import get_db
from backend.security import ph, SECRET_PEPPER

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/technicians", response_model=List[schemas.TechnicianResponse])
def admin_get_technicians(current_user = Depends(auth_service.require_admin), db: Session = Depends(get_db)):
    """List all technicians (admin only)."""
    return db.query(models.Technician).all()

@router.post("/technicians")
def admin_create_technician(tech_in: schemas.TechnicianCreate, current_user = Depends(auth_service.require_admin), db: Session = Depends(get_db)):
    """Create a new technician account (admin only)."""
    if db.query(models.Technician).filter(models.Technician.email == tech_in.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")

    password_with_pepper = tech_in.password + SECRET_PEPPER
    hashed_pwd = ph.hash(password_with_pepper)

    new_tech = models.Technician(
        first_name=tech_in.first_name,
        last_name=tech_in.last_name,
        email=tech_in.email,
        hashed_password=hashed_pwd,
        privilege_level="Technician"
    )
    db.add(new_tech)
    db.commit()
    return {"message": "Technician created successfully"}

@router.patch("/technicians/{tech_id}/role")
def admin_update_technician_role(tech_id: int, privilege_level: str, current_user = Depends(auth_service.require_admin), db: Session = Depends(get_db)):
    """Update a technician's role (cannot alter Admin accounts)."""
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
