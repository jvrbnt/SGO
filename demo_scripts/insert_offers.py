import os
import sys
import random

# Añadimos el directorio padre al path para encontrar la carpeta 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models
from backend.database import LocalSession

db = LocalSession()

try:
    print("Obteniendo clientes y catálogo de servicios de la base de datos...")
    clients = db.query(models.Client).all()
    
    if not clients:
        print("Error: No hay clientes en la base de datos. Por favor, ejecuta primero insert_clients.py")
        sys.exit(1)
        
    catalog_items = db.query(models.ServiceCatalog).all()
    
    # Si no hay catálogo, utilizamos una lista genérica
    if not catalog_items:
        service_names = ["Fabricación de máscaras", "Caracterización eléctrica", "Litografía óptica", "Deposición de metales", "Ataque reactivo"]
        catalog_items = None
        print("Aviso: El catálogo de servicios está vacío. Se usarán nombres de servicio por defecto.")
    else:
        service_names = [item.name for item in catalog_items]

    print("Empezando a crear 20 ofertas...")
    
    for i in range(20):
        client = random.choice(clients)
        
        # Crear nueva oferta
        new_offer = models.Offer(
            client_id=client.id,
            status="requested"
        )
        db.add(new_offer)
        db.flush() # Para obtener el ID de la oferta
        
        num_services = random.randint(1, 5)
        
        # Seleccionar servicios únicos para esta oferta
        if len(service_names) >= num_services:
            selected_services = random.sample(service_names, num_services)
        else:
            selected_services = random.choices(service_names, k=num_services)
            
        for s_name in selected_services:
            # Encontrar el item del catálogo si existe
            catalog_id = None
            if catalog_items:
                for item in catalog_items:
                    if item.name == s_name:
                        catalog_id = item.id
                        break
                        
            new_service = models.Service(
                service_name=s_name,
                hours=random.uniform(1, 6),
                comment=f"Lo quiero rápidito ponte en marcha con la {s_name}",
                offer_id=new_offer.id,
                catalog_id=catalog_id
            )
            db.add(new_service)
            
    db.commit()
    print("¡Éxito! Se han creado 20 ofertas con servicios asignados exitosamente.")
    
except Exception as e:
    print(f"Error al crear las ofertas: {e}")
    db.rollback()
finally:
    db.close()
