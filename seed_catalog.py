from database import LocalSession
import models

def reset_catalog():
    db = LocalSession()
    try:
        print("--- Limpiando base de datos ---")
        # 1. Borrar ofertas de prueba antiguas para evitar bloqueos (Foreign Key)
        db.query(models.Service).delete()
        db.query(models.Offer).delete()
        
        # 2. Vaciar por completo el catálogo antiguo
        db.query(models.ServiceCatalog).delete()
        print("Catálogo antiguo eliminado.")

        # 3. Insertar la lista exclusiva y definitiva
        servicios_reales = [
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

        print("--- Cargando nuevo catálogo ---")
        for s in servicios_reales:
            db.add(models.ServiceCatalog(name=s["name"], price_per_hour=s["price_per_hour"]))
            print(f"Añadido: {s['name']}")
        
        db.commit()
        print("ÉXITO: El catálogo ahora contiene ÚNICAMENTE los servicios solicitados.")
    except Exception as e:
        db.rollback()
        print(f"Error crítico al guardar en PostgreSQL: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_catalog()