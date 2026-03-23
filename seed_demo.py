from database import LocalSession
import models

def seed_everything():
    db = LocalSession()
    try:
        # 1. Insertar Técnico Administrador
        admin = models.Technician(
            first_name="Javier",
            last_name="Admin",
            email="admin@mina.es",
            hashed_password="admin", # En producción usar hash
            profile_picture="https://cdn-icons-png.flaticon.com/512/4086/4086679.png"
        )
        db.add(admin)

        # 2. Insertar Catálogo de Servicios (Basado en tus fotos)
        services = [
            {"name": "LITOGRAFÍA DE ELECTRONES", "price_per_hour": 44.0},
            {"name": "LITOGRAFÍA ÓPTICA", "price_per_hour": 18.0},
            {"name": "RIE", "price_per_hour": 22.0},
            {"name": "PECVD", "price_per_hour": 20.0},
            {"name": "EVAPORACIÓN", "price_per_hour": 18.0},
            {"name": "SPUTTERING", "price_per_hour": 18.0},
            {"name": "SEM", "price_per_hour": 42.0}
        ]
        for s in services:
            db.add(models.ServiceCatalog(name=s["name"], price_per_hour=s["price_per_hour"]))
        
        db.commit()
        print("Demo data (Admin + Catalog) loaded.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_everything()