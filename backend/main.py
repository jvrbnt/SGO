import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend import models
from backend.database import engine, DB_AVAILABLE

# Import Routers
from backend.routers import pages, auth, admin, catalog, client, technician, invoice, documents

# --- LOGGING CONFIGURATION ---
logger = logging.getLogger("sgo")

# --- DATABASE INITIALIZATION ---
if DB_AVAILABLE:
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        import backend.database as database
        database.DB_AVAILABLE = False

# --- APP INITIALIZATION ---
app = FastAPI()

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
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
