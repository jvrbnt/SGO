import sys
import os

# Add the root directory to the python path so it can find 'backend'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import LocalSession
import backend.models as models

def reset_catalog():
    db = LocalSession()
    try:
        print("--- Resetting Catalog ---")
        # First we must delete related entries to avoid foreign key constraint failures
        db.query(models.Service).delete()
        db.query(models.Offer).delete()
        
        # Now we can safely empty the catalog table
        db.query(models.ServiceCatalog).delete()
        
        db.commit()
        print("SUCCESS: Service catalog has been cleared.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_catalog()
