import os
import sys
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from argon2 import PasswordHasher, Type

from backend import models
from backend.database import LocalSession

load_dotenv()
SECRET_PEPPER = os.getenv("SECRET_PEPPER")

if not SECRET_PEPPER:
    print("Error: SECRET_PEPPER not found in .env")
    exit(1)

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
    type=Type.ID
)

db = LocalSession()

first_names = ["Juan", "Maria", "Pedro", "Lucia", "Carlos", "Ana", "Miguel", "Laura", "Jose", "Carmen",
               "David", "Sofia", "Alejandro", "Elena", "Daniel", "Marta", "Manuel", "Paula", "Javier", "Raquel"]
last_names = ["Garcia", "Gonzalez", "Rodriguez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez",
              "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez", "Diaz", "Moreno", "Munoz", "Alvarez",
              "Romero", "Alonso", "Gutierrez"]

# Example IP (Investigador Principal) names for internal clients
ip_names = ["Dr. Garcia Fernandez", "Dr. Lopez Martin", "Dr. Sanchez Ruiz",
            "Dr. Hernandez Diaz", "Dr. Moreno Alvarez", "Dr. Romero Alonso"]

print("Starting to add 20 demo clients...")

for i in range(20):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    email = f"client{i+1}.{fn.lower()}.{ln.lower()}@demo.csic.es"

    password_with_pepper = "demo1234" + SECRET_PEPPER
    hashed_pwd = ph.hash(password_with_pepper)

    # Higher probability of Internal clients for testing
    entity_choice = random.choice(['Internal', 'Internal', 'CSIC', 'UAM', 'University', 'OPIS', 'Company'])

    if entity_choice == 'Internal':
        ip_name = random.choice(ip_names)
        ci = f"ACC-{random.randint(1000, 9999)}"
        cp = f"PRJ-{random.randint(100, 999)}"
        grp = random.choice(['FINDER', 'BIONANOMECHANICS', 'ES4TERM', 'OMS', 'MBE', 'METALNANO'])
    else:
        ip_name = None
        ci = None
        cp = None
        grp = None

    new_client = models.Client(
        first_name=fn,
        last_name=ln,
        email=email,
        hashed_password=hashed_pwd,
        entity=entity_choice,
        investigador_principal=ip_name,
        cuenta_interna=ci,
        codigo_proyecto=cp,
        grupo=grp,
        profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
    )
    db.add(new_client)

try:
    db.commit()
    print("Successfully added 20 demo clients.")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
