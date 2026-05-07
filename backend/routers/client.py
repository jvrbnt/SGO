from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime
from typing import List

from backend import models, schemas, auth as auth_service
from backend.dependencies import get_db

router = APIRouter(prefix="/api/client", tags=["client"])

@router.post("/offers")
def create_offer(offer_in: schemas.OfferCreate, current_user = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """Create a new offer request from a client.
    
    Uses a PostgreSQL Sequence (offer_ref_seq) for concurrency-safe reference
    code generation instead of the fragile 'find last + 1' pattern.
    """
    # Ensure current client doesn't spawn offers for other emails
    if current_user.app_role == "client" and current_user.email != offer_in.client_email:
        raise HTTPException(status_code=403, detail="Unauthorized client email")
        
    client = db.query(models.Client).filter(models.Client.email == offer_in.client_email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found in database")

    current_year = datetime.now().year

    # Atomically get the next value from the database sequence (concurrency-safe)
    next_seq = db.execute(models.offer_ref_seq)
    reference_code = f"{next_seq:03d}_{current_year}"

    new_offer = models.Offer(client_id=client.id, status="requested", reference=reference_code)
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)

    for s in offer_in.services:
        catalog_item = db.query(models.ServiceCatalog).filter(
            models.ServiceCatalog.name == s.service_name
        ).first()

        new_service = models.Service(
            service_name=s.service_name,
            hours=s.hours,
            original_hours=s.hours,
            comment=s.comment,
            offer_id=new_offer.id,
            catalog_id=catalog_item.id if catalog_item else None
        )
        db.add(new_service)

    db.commit()
    return {"message": "Offer requested successfully", "offer_id": new_offer.id}

@router.get("/my-offers", response_model=List[schemas.OfferResponse])
def get_client_offers(email: str, current_user = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """Get all offers for a specific client by email."""
    if current_user.app_role == "client" and current_user.email != email:
        raise HTTPException(status_code=403, detail="Unauthorized request")
        
    client = db.query(models.Client).filter(models.Client.email == email).first()
    if not client:
        return []
    return db.query(models.Offer).filter(models.Offer.client_id == client.id).all()

@router.patch("/offers/{offer_id}/accept")
def client_accept_offer(offer_id: int, current_user = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """Allow a client to accept a quoted offer."""
    if current_user.app_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can accept offers")

    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="This offer does not belong to you")

    if offer.status != "quoted":
        raise HTTPException(status_code=400, detail=f"Cannot accept an offer with status '{offer.status}'")

    offer.status = "accepted"
    db.commit()
    return {"message": "Offer accepted successfully"}

@router.get("/invoices")
def get_client_invoices(email: str, current_user = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """Get all invoices for a client."""
    if current_user.app_role == "client" and current_user.email != email:
        raise HTTPException(status_code=403, detail="Unauthorized request")
    client = db.query(models.Client).filter(models.Client.email == email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    invoices = db.query(models.Invoice).filter(models.Invoice.client_id == client.id).all()
    result = []
    for inv in invoices:
        tech = db.query(models.Technician).filter(models.Technician.id == inv.technician_id).first()
        offers_data = []
        for o in inv.offers:
            offers_data.append({
                "id": o.id, "status": o.status, "technician_comment": o.technician_comment,
                "services": [{
                    "id": s.id, "service_name": s.service_name, "hours": s.hours,
                    "quoted_price": s.quoted_price, "is_deleted": s.is_deleted,
                    "added_by_technician": s.added_by_technician, "original_hours": s.original_hours,
                    "comment": s.comment
                } for s in o.services if not s.is_deleted]
            })
        result.append({
            "id": inv.id, "client_id": inv.client_id, "technician_id": inv.technician_id,
            "technician_first_name": tech.first_name if tech else None,
            "technician_last_name": tech.last_name if tech else None,
            "total_price": inv.total_price, "comment": inv.comment,
            "status": inv.status, "created_at": inv.created_at.isoformat(),
            "offers": offers_data
        })
    return result
