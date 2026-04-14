import os
import sys
import random

# Añadimos el directorio padre al path para encontrar la carpeta 'backend'
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

first_names = ["Juan", "Maria", "Pedro", "Lucia", "Carlos", "Ana", "Miguel", "Laura", "Jose", "Carmen", "David", "Sofia", "Alejandro", "Elena", "Daniel", "Marta", "Manuel", "Paula", "Javier", "Raquel"]
last_names = ["Garcia", "Gonzalez", "Rodriguez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez", "Diaz", "Moreno", "Muñoz", "Alvarez", "Romero", "Alonso", "Gutierrez"]

print("Starting to add 20 clients...")

for i in range(20):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    email = f"client{i+1}.{fn.lower()}.{ln.lower()}@gmail.com"
    
    password_with_pepper = "123456" + SECRET_PEPPER
    hashed_pwd = ph.hash(password_with_pepper)
    
    # Aumentamos ligeramente la probabilidad de que salga 'Internal' añadiéndolo otra vez a la lista
    entity_choice = random.choice(['Internal', 'Internal', 'CSIC', 'UAM', 'University', 'OPIS', 'Company'])
    
    if entity_choice == 'Internal':
        internal_acct = f"ACC-{random.randint(1000, 9999)}"
        ip_addr = f"192.168.1.{random.randint(2, 254)}"
        proj_id = f"PRJ-{random.randint(100, 999)}"
        grp_name = random.choice(['FINDER', 'BIONANOMECHANICS', 'ES4TERM', 'OMS', 'MBE', 'METALNANO'])
    else:
        internal_acct = None
        ip_addr = None
        proj_id = None
        grp_name = None
        
    new_client = models.Client(
        first_name=fn,
        last_name=ln,
        email=email,
        hashed_password=hashed_pwd, 
        entity=entity_choice,
        internal_account=internal_acct,
        ip_address=ip_addr,
        project_id=proj_id,
        group_name=grp_name,
        profile_picture="https://static.vecteezy.com/system/resources/thumbnails/021/353/308/small/user-icon-for-website-and-mobile-apps-png.png"
    )
    db.add(new_client)

try:
    db.commit()
    print("Successfully added 20 clients.")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
