from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    entity = Column(String)

    # --- EXTRA FIELDS (Optional, can be empty if not from MiNa) ---
    group = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    account = Column(String, nullable=True)
    project = Column(String, nullable=True)

    # Field to store the profile picture URL
    profile_picture = Column(String, nullable=True)