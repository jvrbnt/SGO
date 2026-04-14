import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo_scripts.init_db import reset_db
from demo_scripts.seed_catalog import reset_catalog
from demo_scripts.create_admin import seed_technician

def run_all():
    print("SISTEMA DE PREPARACIÓN DE BASE DE DATOS")
    
    print("\n[1/3] RESETTING TABLE STRUCTURE...")
    reset_db()
    
    print("\n[2/3] LOADING SERVICE CATALOG...")
    reset_catalog()


    print("\n[3/3] (OPTIONAL) CREATE NEW TECHNICIAN MANUALLY")
    resp = input("Do you want to create an extra technician right now? (y/n): ")
    if resp.lower() in ('s', 'si', 'y', 'yes'):
        seed_technician()

    print("\n Creado con éxito")

if __name__ == "__main__":
    run_all()
