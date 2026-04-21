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

        # Official MiNa service catalog with pricing tiers
        catalogo_servicios = [
            {"name": "Electron Beam Lithography", "price_internal": 38.16, "price_csic": 44.77, "price_public": 110.20, "price_private": 120.69},
            {"name": "HR-SEM Microscopy", "price_internal": 51.87, "price_csic": 60.84, "price_public": 123.33, "price_private": 135.08},
            {"name": "Reactive Ion Etching (RIE)", "price_internal": 9.28, "price_csic": 10.89, "price_public": 123.96, "price_private": 135.77},
            {"name": "Focused Ion Beam (FIB)", "price_internal": 136.19, "price_csic": 159.75, "price_public": 275.91, "price_private": 302.19},
            {"name": "Metal Evaporation", "price_internal": 14.76, "price_csic": 17.32, "price_public": 84.99, "price_private": 93.08},
            {"name": "Atomic Force Microscopy (AFM)", "price_internal": 29.23, "price_csic": 34.29, "price_public": 84.66, "price_private": 92.72},
            {"name": "UV Lithography", "price_internal": 11.11, "price_csic": 13.03, "price_public": 80.80, "price_private": 88.49},
            {"name": "Profilometer", "price_internal": 5.94, "price_csic": 6.96, "price_public": 65.55, "price_private": 71.79},
            {"name": "Spin Coating", "price_internal": 5.96, "price_csic": 7.07, "price_public": 73.85, "price_private": 80.88},
            {"name": "Wet Etching", "price_internal": 6.79, "price_csic": 7.97, "price_public": 87.27, "price_private": 95.58},
            {"name": "X-Ray Diffraction (XRD)", "price_internal": 10.93, "price_csic": 12.82, "price_public": 328.40, "price_private": 359.67},
            {"name": "SiOx, SiNx Coatings (PECVD)", "price_internal": 8.76, "price_csic": 10.27, "price_public": 74.69, "price_private": 81.80},
            {"name": "Micro-welding", "price_internal": 20.96, "price_csic": 24.56, "price_public": 81.27, "price_private": 89.01}
        ]

        for s in catalogo_servicios:
            db.add(models.ServiceCatalog(
                name=s["name"],
                price_internal=s["price_internal"],
                price_csic=s["price_csic"],
                price_public=s["price_public"],
                price_private=s["price_private"]
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