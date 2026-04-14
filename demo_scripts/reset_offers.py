import os
import sys

# Añadimos el directorio padre al path para encontrar la carpeta 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models
from backend.database import LocalSession

db = LocalSession()

try:
    print("Borrando todos los servicios asociados para evitar errores de restricción de claves foráneas...")
    # Primero borramos los servicios que hacen referencia a las ofertas
    deleted_services = db.query(models.Service).delete()
    
    print("Borrando todas las ofertas...")
    # Ahora podemos borrar las ofertas de forma segura
    deleted_offers = db.query(models.Offer).delete()
    
    db.commit()
    print(f"Éxito: Se han eliminado {deleted_offers} ofertas y {deleted_services} servicios asociados de la base de datos.")
except Exception as e:
    print(f"Error reseteando la tabla de ofertas: {e}")
    db.rollback()
finally:
    db.close()
