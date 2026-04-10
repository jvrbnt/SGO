import sys
from demo_scripts.init_db import reset_db
from demo_scripts.seed_catalog import reset_catalog
from demo_scripts.seed_demo import seed_demo_users
from demo_scripts.create_admin import seed_technician

def run_all():
    print("SISTEMA DE PREPARACIÓN DE BASE DE DATOS")
    
    print("\n[1/4] RESETEANDO ESTRUCTURA DE TABLAS...")
    reset_db()
    
    print("\n[2/4] CARGANDO CATÁLOGO DE SERVICIOS...")
    reset_catalog()
    
    print("\n[3/4] CARGANDO USUARIOS DEMO...")
    seed_demo_users()

    print("\n[4/4] (OPCIONAL) CREAR TÉCNICO NUEVO MANUALMENTE")
    resp = input("¿Deseas crear un técnico extra ahora mismo? (s/n): ")
    if resp.lower() in ('s', 'si', 'y', 'yes'):
        seed_technician()

    print("\n Creado con éxito")

if __name__ == "__main__":
    run_all()
