import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from backend import models
from backend.database import engine, DB_AVAILABLE, LocalSession

# Import Routers
from backend.routers import pages, auth, admin, catalog, client, technician, invoice, documents, traceability

# --- LOGGING CONFIGURATION ---
logger = logging.getLogger("sgo")

# --- DATABASE INITIALIZATION ---
if DB_AVAILABLE and os.getenv("AUTO_CREATE_TABLES", "").lower() in {"1", "true", "yes"}:
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        import backend.database as database
        database.DB_AVAILABLE = False

# --- APP INITIALIZATION ---
app = FastAPI()


@app.get("/api/health", tags=["health"])
def healthcheck():
    if not DB_AVAILABLE or LocalSession is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    db = LocalSession()
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Healthcheck database query failed: %s", exc)
        raise HTTPException(status_code=503, detail="Database is not reachable") from exc
    finally:
        db.close()
    return {"status": "ok", "database": "ok"}

# --- CORS MIDDLEWARE ---
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- STATIC FILES ---
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# --- INCLUDE ROUTERS ---
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(catalog.router)
app.include_router(client.router)
app.include_router(technician.router)
app.include_router(invoice.router)
app.include_router(documents.router)
app.include_router(documents.client_router)
app.include_router(traceability.router)
