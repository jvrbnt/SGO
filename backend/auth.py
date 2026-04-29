import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend import models
from backend.database import LocalSession

# Load security key from environment
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("ERROR: JWT_SECRET_KEY variable not found in .env file!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # Token lasts 12 hours

# OAuth2 scheme for Swagger UI/FastAPI dependency injection (though we use fetch in JS)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

from backend.dependencies import get_db

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generates a signed JWT with user data and expiration time."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Middleware function. Extracts JWT from Authorization header,
    validates the signature, checks expiration, and retrieves the user object.
    Raises 401 Unauthorized if anything fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        
        if user_id is None or role is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    # Fetch from correct table based on role
    user = None
    if role == "client":
        user = db.query(models.Client).filter(models.Client.id == user_id).first()
        if user:
            setattr(user, "app_role", "client")
            setattr(user, "privilege_level", "Client") 
    elif role == "technician":
        user = db.query(models.Technician).filter(models.Technician.id == user_id).first()
        if user:
            setattr(user, "app_role", "technician")
            # user.privilege_level exists natively models.Technician
            
    if user is None:
        raise credentials_exception
        
    return user

def require_admin(current_user = Depends(get_current_user)):
    """Enforces that the current logged-in user is an Admin."""
    if current_user.app_role != "technician" or current_user.privilege_level != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def require_technician_or_higher(current_user = Depends(get_current_user)):
    """Enforces that the current logged-in user is at least a Technician."""
    if current_user.app_role != "technician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technician privileges required"
        )
    return current_user
