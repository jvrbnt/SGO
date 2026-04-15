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
            {"name": "Electron Beam Lithography", "price1": 38.16, "price2": 44.77, "price3": 110.20, "price4": 120.69},
            {"name": "HR-SEM Microscopy", "price1": 51.87, "price2": 60.84, "price3": 123.33, "price4": 135.08},
            {"name": "Reactive Ion Etching (RIE)", "price1": 9.28, "price2": 10.89, "price3": 123.96, "price4": 135.77},
            {"name": "Focused Ion Beam (FIB)", "price1": 136.19, "price2": 159.75, "price3": 275.91, "price4": 302.19},
            {"name": "Metal Evaporation", "price1": 14.76, "price2": 17.32, "price3": 84.99, "price4": 93.08},
            {"name": "Atomic Force Microscopy (AFM)", "price1": 29.23, "price2": 34.29, "price3": 84.66, "price4": 92.72},
            {"name": "UV Lithography", "price1": 11.11, "price2": 13.03, "price3": 80.80, "price4": 88.49},
            {"name": "Profilometer", "price1": 5.94, "price2": 6.96, "price3": 65.55, "price4": 71.79},
            {"name": "Spin Coating", "price1": 5.96, "price2": 7.07, "price3": 73.85, "price4": 80.88},
            {"name": "Wet Etching", "price1": 6.79, "price2": 7.97, "price3": 87.27, "price4": 95.58},
            {"name": "X-Ray Diffraction (XRD)", "price1": 10.93, "price2": 12.82, "price3": 328.40, "price4": 359.67},
            {"name": "SiOx, SiNx Coatings (PECVD)", "price1": 8.76, "price2": 10.27, "price3": 74.69, "price4": 81.80},
            {"name": "Micro-welding", "price1": 20.96, "price2": 24.56, "price3": 81.27, "price4": 89.01}
        ]

        for s in catalogo_servicios:
            db.add(models.ServiceCatalog(
                name=s["name"], 
                price1=s["price1"],
                price2=s["price2"],
                price3=s["price3"],
                price4=s["price4"]
            ))
        
        db.commit()
        print("SUCCESS: Official catalog loaded.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_catalog()