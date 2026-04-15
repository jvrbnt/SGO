import os
import sys
import random

# Add parent directory to path to find 'backend' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models
from backend.database import LocalSession

db = LocalSession()

try:
    print("Fetching clients and service catalog from database...")
    clients = db.query(models.Client).all()
    
    if not clients:
        print("Error: No clients found in database. Please run insert_clients.py first.")
        sys.exit(1)
        
    catalog_items = db.query(models.ServiceCatalog).all()
    
    # Use generic list if catalog is empty
    if not catalog_items:
        service_names = ["Mask Fabrication", "Electrical Characterization", "Optical Lithography", "Metal Deposition", "Reactive Etching"]
        catalog_items = None
        print("Warning: Service catalog is empty. Using default service names.")
    else:
        service_names = [item.name for item in catalog_items]

    print("Starting to create 20 sample offers...")
    
    for i in range(20):
        client = random.choice(clients)
        
        # Create new offer
        new_offer = models.Offer(
            client_id=client.id,
            status="requested"
        )
        db.add(new_offer)
        db.flush() # Get offer ID
        
        num_services = random.randint(1, 5)
        
        # Select unique services for this offer
        if len(service_names) >= num_services:
            selected_services = random.sample(service_names, num_services)
        else:
            selected_services = random.choices(service_names, k=num_services)
            
        for s_name in selected_services:
            # Find catalog item if exists
            catalog_id = None
            if catalog_items:
                for item in catalog_items:
                    if item.name == s_name:
                        catalog_id = item.id
                        break
                        
            new_service = models.Service(
                service_name=s_name,
                hours=random.randint(1, 6),
                comment=f"Please proceed with {s_name} as soon as possible.",
                offer_id=new_offer.id,
                catalog_id=catalog_id
            )
            db.add(new_service)
            
    db.commit()
    print("Success! 20 offers with assigned services have been created successfully.")
    
except Exception as e:
    print(f"Error creating offers: {e}")
    db.rollback()
finally:
    db.close()
