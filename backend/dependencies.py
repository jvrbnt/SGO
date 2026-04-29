from fastapi import HTTPException, status
from backend.database import LocalSession, DB_AVAILABLE

def get_db():
    if not DB_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not available"
        )
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
