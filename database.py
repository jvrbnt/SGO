import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Si DATABASE_URL no está en el .env, esto devolverá None
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Forzamos un error claro si falta la configuración
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("ERROR: No se ha encontrado la variable DATABASE_URL en el archivo .env")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()