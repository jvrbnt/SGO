import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_scripts.init_db import reset_db
from demo_scripts.seed_catalog import reset_catalog
from demo_scripts.seed_demo import seed_demo_users
from demo_scripts.create_admin import seed_technician

def run_all():
    print("SISTEMA DE PREPARACIÓN DE BASE DE DATOS")
    
    print("\n[1/4] RESETTING TABLE STRUCTURE...")
    reset_db()
    
    print("\n[2/4] LOADING SERVICE CATALOG...")
    reset_catalog()
    
    print("\n[3/4] LOADING DEMO USERS...")
    seed_demo_users()

    print("\n[4/4] (OPTIONAL) CREATE NEW TECHNICIAN MANUALLY")
    resp = input("Do you want to create an extra technician right now? (y/n): ")
    if resp.lower() in ('s', 'si', 'y', 'yes'):
        seed_technician()

    print("\n Creado con éxito")

if __name__ == "__main__":
    run_all()
