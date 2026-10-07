"""Wipe all offers (test data) and pre-load the running X-ray offers.

Usage: python -m demo_scripts.reset_offers_and_prepare
Offers are attached to a client when they sign up with the prepared email
(or right now, if that client already exists).
"""
from backend import models
from backend.database import LocalSession
from backend.prepared_offers import claim_prepared_offers

SERVICE = "X-Ray Diffraction (XRD)"

# reference, email, consumed hours, requested hours, price
PREPARED = [
    ("144_2025", "cristina.vicente@csic.es", 7.58, 10, 109.30),
    ("291_2025", "paloma.berrocal@csic.es", 6, 10, 109.30),
    ("010_2026", "josemaria.dominguez@csic.es", 11.41, 51.91, 567.38),
    ("031_2026", "samuel.ramsay@csic.es", 13, 20, 218.60),
    ("044_2026", "ester.palmero@csic.es", 23, 50, 546.50),
    ("059_2026", "olga.caballero@csic.es", 7.25, 10, 109.30),
    ("062_2026", "andres.conca@csic.es", 34, 50, 546.50),
    ("066_2026", "victor.zamora.csic@gmail.com", 3, 6, 100.0),
]


def main():
    db = LocalSession()
    try:
        db.query(models.TraceabilityEntry).delete()
        db.query(models.GeneratedDocument).delete()
        db.query(models.Service).delete()
        db.query(models.Offer).delete()
        db.query(models.Invoice).delete()
        db.query(models.PreparedOffer).delete()
        for reference, email, consumed, hours, price in PREPARED:
            db.add(models.PreparedOffer(
                email=email.lower(), reference=reference, service_name=SERVICE,
                hours=hours, consumed_hours=consumed, price=price,
            ))
        db.commit()

        for client in db.query(models.Client).all():
            created = claim_prepared_offers(db, client)
            if created:
                print(f"{client.email}: {created} offer(s) attached to the existing account")
        print(f"{len(PREPARED)} prepared offers loaded")
    finally:
        db.close()


if __name__ == "__main__":
    main()
