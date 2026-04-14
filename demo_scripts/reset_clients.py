import os
import sys

# Añadimos el directorio padre al path para encontrar la carpeta 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models
from backend.database import LocalSession

db = LocalSession()

try:
    print("Borrando todas las ofertas y servicios asociados para evitar errores de restricción de claves foráneas...")
    # First delete services that refer to offers
    db.query(models.Service).delete()
    # Delete offers that refer to clients
    db.query(models.Offer).delete()
    
    print("Borrando todos los clientes...")
    # Now we can safely delete clients
    deleted_clients = db.query(models.Client).delete()
    
    db.commit()
    print(f"Éxito: Se han eliminado {deleted_clients} clientes de la base de datos.")
except Exception as e:
    print(f"Error reseteando la tabla de clientes: {e}")
    db.rollback()
finally:
    db.close()
