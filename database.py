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
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Query manager (Used in main.py for API requests)
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Base class from which all tables will be created (Used in models.py)
Base = declarative_base()