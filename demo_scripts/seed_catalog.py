import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import LocalSession
import backend.models as models

def reset_catalog():
    db = LocalSession()
    try:
        print("--- Cleaning Catalog ---")
        db.query(models.Service).delete()
        db.query(models.Offer).delete()
        db.query(models.ServiceCatalog).delete()

        catalogo_servicios = [
            {"name": "Litografía por haz de electrones", "price_per_hour": 0.0},
            {"name": "Microscopía electrónica de barrido de alta resolución", "price_per_hour": 0.0},
            {"name": "Ataques de iones reactivos (RIE)", "price_per_hour": 0.0},
            {"name": "Ataques por haz de iones (FIB)", "price_per_hour": 0.0},
            {"name": "Evaporación de metales", "price_per_hour": 0.0},
            {"name": "Microscopía de fuerzas atómicas", "price_per_hour": 0.0},
            {"name": "Litografías UV", "price_per_hour": 0.0},
            {"name": "Recubrimientos con centrífuga", "price_per_hour": 0.0},
            {"name": "Ataques húmedos", "price_per_hour": 0.0},
            {"name": "Difracción de rayos X", "price_per_hour": 0.0},
            {"name": "Recubrimientos de SiOx, SiNx (PECVD)", "price_per_hour": 0.0}
        ]

        for s in catalogo_servicios:
            db.add(models.ServiceCatalog(name=s["name"], price_per_hour=s["price_per_hour"]))
        
        db.commit()
        print("SUCCESS: Official catalog loaded.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_catalog()