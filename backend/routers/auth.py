from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from backend import models, schemas, auth as auth_service
from backend.email import send_password_reset_email, send_welcome_email
from backend.dependencies import get_db
from backend.security import ph, SECRET_PEPPER

router = APIRouter(prefix="/api", tags=["auth"])

PASSWORD_RESET_MINUTES = 30


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value

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
    send_welcome_email(new_client.email, new_client.first_name)
    return {"message": "Client account created successfully"}


@router.post("/forgot-password")
def request_password_reset(reset_data: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    """Create a short-lived reset token without revealing whether an email exists."""
    user = db.query(models.Client).filter(models.Client.email == reset_data.email).first()
    user_type = "client"
    if not user:
        user = db.query(models.Technician).filter(models.Technician.email == reset_data.email).first()
        user_type = "technician"

    if user:
        now = _utc_now()
        query = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.used_at.is_(None))
        if user_type == "client":
            query = query.filter(models.PasswordResetToken.client_id == user.id)
        else:
            query = query.filter(models.PasswordResetToken.technician_id == user.id)
        query.update({models.PasswordResetToken.used_at: now}, synchronize_session=False)

        raw_token = secrets.token_urlsafe(32)
        reset_token = models.PasswordResetToken(
            client_id=user.id if user_type == "client" else None,
            technician_id=user.id if user_type == "technician" else None,
            token_hash=_token_hash(raw_token),
            expires_at=now + timedelta(minutes=PASSWORD_RESET_MINUTES),
        )
        db.add(reset_token)
        db.commit()
        send_password_reset_email(user.email, user.first_name, raw_token)

    return {"message": "If the email is registered, you will receive password reset instructions."}


@router.post("/reset-password")
def reset_password(reset_data: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    """Validate and consume a password reset token exactly once."""
    reset_token = (
        db.query(models.PasswordResetToken)
        .with_for_update()
        .filter(
            models.PasswordResetToken.token_hash == _token_hash(reset_data.token),
            models.PasswordResetToken.used_at.is_(None),
        )
        .first()
    )
    if not reset_token or _as_utc(reset_token.expires_at) <= _utc_now():
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token")

    user = reset_token.client or reset_token.technician
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token")

    user.hashed_password = ph.hash(reset_data.new_password + SECRET_PEPPER)
    reset_token.used_at = _utc_now()
    db.commit()
    return {"message": "Password updated successfully"}

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
