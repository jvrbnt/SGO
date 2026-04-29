import os
from dotenv import load_dotenv
from argon2 import PasswordHasher, Type

load_dotenv()
SECRET_PEPPER = os.getenv("SECRET_PEPPER")

if not SECRET_PEPPER:
    raise RuntimeError("ERROR: SECRET_PEPPER variable not found in .env file!")

# Argon2id Hybrid Configuration
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID
)
