import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1. Load variables from the local .env file
load_dotenv()

# 2. Get the full URL from the environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Engine that sends the data
Base = declarative_base()

if SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        # Esto fuerza a que la comunicación no dé errores de decodificación
        connect_args={
            "options": "-c lc_messages=C",
            "client_encoding": "utf8"
        }
    )
    LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    DB_AVAILABLE = True
else:
    print("WARNING: DATABASE_URL not set — running without database.")
    engine = None
    LocalSession = None
    DB_AVAILABLE = False