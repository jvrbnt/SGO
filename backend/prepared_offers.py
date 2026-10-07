"""Pre-loaded running offers that are attached to a client when they register."""
from datetime import datetime

from sqlalchemy.orm import Session

from backend import models, workflow

DEFAULT_MANAGER_EMAIL = "victor.zamora@csic.es"


def claim_prepared_offers(db: Session, client: models.Client) -> int:
    """Create the accepted offers prepared for the client's email. Returns how many were created."""
    pending = (
        db.query(models.PreparedOffer)
        .filter(
            models.PreparedOffer.email == client.email.strip().lower(),
            models.PreparedOffer.claimed_at.is_(None),
        )
        .all()
    )
    if not pending:
        return 0

    manager = db.query(models.Technician).filter(models.Technician.email == DEFAULT_MANAGER_EMAIL).first()
    now = datetime.now()
    for item in pending:
        catalog = db.query(models.ServiceCatalog).filter(models.ServiceCatalog.name == item.service_name).first()
        offer = models.Offer(
            reference=item.reference,
            status=workflow.ACCEPTED,
            client_id=client.id,
            manager_id=manager.id if manager else None,
            created_at=now,
        )
        offer.services.append(models.Service(
            service_name=item.service_name,
            hours=item.hours,
            original_hours=item.hours,
            consumed_hours=item.consumed_hours,
            quoted_price=item.price,
            status=workflow.PENDING,
            technician_id=manager.id if manager else None,
            catalog_id=catalog.id if catalog else None,
        ))
        db.add(offer)
        item.claimed_at = now
    db.commit()
    return len(pending)
