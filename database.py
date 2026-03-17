import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1. Cargamos las variables desde el archivo .env local
load_dotenv()

# 2. Obtenemos la URL completa desde la variable de entorno
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Motor que envía los datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Gestor de consultas (Usado en main.py para las peticiones API)
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Clase base de donde nacerán todas las tablas (Usada en models.py)
Base = declarative_base()