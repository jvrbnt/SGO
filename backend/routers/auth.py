from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError
from datetime import timedelta

from backend import models, schemas, auth as auth_service
from backend.dependencies import get_db
from backend.security import ph, SECRET_PEPPER

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/client/signup")
def create_client(client_data: schemas.ClientCreateWeb, db: Session = Depends(get_db)):
    """Register a new client account."""
    if (
        db.query(models.Client).filter(models.Client.email == client_data.email).first()
        or db.query(models.Technician).filter(models.Technician.email == client_data.email).first()
    ):
        raise HTTPException(status_code=400, detail="Email is already registered")

    password_with_pepper = client_data.password + SECRET_PEPPER
    hashed_pwd = ph.hash(password_with_pepper)

    new_client = models.Client(
        first_name=client_data.first_name,
        last_name=client_data.last_name,
        email=client_data.email,
        hashed_password=hashed_pwd,
        entity=client_data.entity,
        investigador_principal=client_data.investigador_principal,
        cuenta_interna=client_data.cuenta_interna,
        grupo=client_data.grupo,
        codigo_proyecto=client_data.codigo_proyecto,
        profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
    )
    db.add(new_client)
    db.commit()
    return {"message": "Client account created successfully"}

@router.post("/login")
def unified_login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Unified login - returns JWT and User Data."""
    password_with_pepper = login_data.password + SECRET_PEPPER

    # 1. Client Verification
    client = db.query(models.Client).filter(models.Client.email == login_data.email).first()
    if client:
        try:
            ph.verify(client.hashed_password, password_with_pepper)
            access_token = auth_service.create_access_token(
                data={"id": client.id, "role": "client"},
                expires_delta=timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": client.id,
                    "role": "client",
                    "email": client.email,
                    "first_name": client.first_name,
                    "last_name": client.last_name,
                    "display_name": client.display_name,
                    "nickname": client.display_name,
                    "profile_picture": client.profile_picture,
                    "entity": client.entity,
                    "investigador_principal": client.investigador_principal,
                    "cuenta_interna": client.cuenta_interna,
                    "codigo_proyecto": client.codigo_proyecto,
                    "grupo": client.grupo,
                }
            }
        except VerifyMismatchError:
            pass

    # 2. Technician Verification
    tech = db.query(models.Technician).filter(models.Technician.email == login_data.email).first()
    if tech:
        try:
            ph.verify(tech.hashed_password, password_with_pepper)
            access_token = auth_service.create_access_token(
                data={"id": tech.id, "role": "technician"},
                expires_delta=timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": tech.id,
                    "role": "technician",
                    "email": tech.email,
                    "first_name": tech.first_name,
                    "last_name": tech.last_name,
                    "display_name": tech.display_name,
                    "nickname": tech.display_name,
                    "profile_picture": tech.profile_picture,
                    "privilege_level": tech.privilege_level
                }
            }
        except VerifyMismatchError:
            pass

    raise HTTPException(status_code=401, detail="Incorrect credentials")

@router.get("/me")
def read_users_me(current_user = Depends(auth_service.get_current_user)):
    """Returns the user data associated with the JWT for session restoration."""
    if current_user.app_role == "client":
        return {
            "id": current_user.id,
            "role": "client",
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "display_name": getattr(current_user, "display_name", None),
            "nickname": getattr(current_user, "display_name", None),
            "profile_picture": getattr(current_user, "profile_picture", None),
            "entity": current_user.entity,
            "investigador_principal": current_user.investigador_principal,
            "cuenta_interna": current_user.cuenta_interna,
            "codigo_proyecto": current_user.codigo_proyecto,
            "grupo": current_user.grupo,
        }
    else:
        return {
            "id": current_user.id,
            "role": "technician",
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "display_name": getattr(current_user, "display_name", None),
            "nickname": getattr(current_user, "display_name", None),
            "profile_picture": getattr(current_user, "profile_picture", None),
            "privilege_level": getattr(current_user, "privilege_level", "Technician")
        }


@router.patch("/me")
def update_users_me(
    profile_data: schemas.ProfileUpdate,
    current_user=Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Persist editable profile fields for the logged-in user.
    This centralized endpoint replaces the insecure approach of only updating
    profile data in the frontend's localStorage. It ensures that the database
    is the source of truth for user profiles, including critical billing fields
    for internal clients.
    """
    current_user.display_name = profile_data.display_name
    if profile_data.profile_picture is not None:
        current_user.profile_picture = profile_data.profile_picture

    if current_user.app_role == "client":
        if profile_data.entity is not None:
            current_user.entity = profile_data.entity
        current_user.investigador_principal = profile_data.investigador_principal
        current_user.cuenta_interna = profile_data.cuenta_interna
        current_user.codigo_proyecto = profile_data.codigo_proyecto
        current_user.grupo = profile_data.grupo

    db.commit()
    db.refresh(current_user)
    return read_users_me(current_user)
