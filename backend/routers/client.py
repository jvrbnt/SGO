from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from typing import List

from backend import models, schemas, auth as auth_service
from backend.dependencies import get_db
from backend import workflow
from backend.pdf_documents import generate_acceptance_pdf, generate_request_pdf

router = APIRouter(prefix="/api/client", tags=["client"])

@router.post("/offers")
def create_offer(offer_in: schemas.OfferCreate, current_user = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """Create a new offer request from a client.
    
    Uses a PostgreSQL Sequence (offer_ref_seq) for concurrency-safe reference
    code generation instead of the fragile 'find last + 1' pattern.
    """
    if current_user.app_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can create offer requests")

    # Ensure current client doesn't spawn offers for other emails
    if current_user.email != offer_in.client_email:
        raise HTTPException(status_code=403, detail="Unauthorized client email")
        
    client = db.query(models.Client).filter(models.Client.email == offer_in.client_email).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found in database")

    current_year = datetime.now().year

    # Atomically get the next value from the database sequence (concurrency-safe)
    next_seq = db.execute(select(models.offer_ref_seq.next_value())).scalar_one()
    reference_code = f"{next_seq:03d}_{current_year}"

    try:
        new_offer = models.Offer(client_id=client.id, status=workflow.REQUESTED, reference=reference_code)
        db.add(new_offer)
        db.flush()

        for s in offer_in.services:
            catalog_item = db.query(models.ServiceCatalog).filter(
                models.ServiceCatalog.name == s.service_name
            ).first()
            if not catalog_item:
                raise HTTPException(status_code=400, detail=f"Unknown service '{s.service_name}'")

            new_service = models.Service(
                service_name=catalog_item.name,
                hours=s.hours,
                original_hours=s.hours,
                comment=s.comment,
                offer_id=new_offer.id,
                catalog_id=catalog_item.id
            )
            db.add(new_service)

        db.flush()
        db.refresh(new_offer)
        generate_request_pdf(db, new_offer)
        db.refresh(new_offer)
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

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

    # SECURITY FIX: Ensure the offer is in a valid state to be accepted.
    if offer.status != workflow.QUOTED:
        raise HTTPException(status_code=400, detail=f"Cannot accept an offer with status '{offer.status}'")

    active_services = workflow.active_services(offer)
    # SECURITY FIX: Prevent accepting an offer that has no services or unpriced services.
    # This prevents edge cases where an empty offer or an offer with missing prices enters the active workflow.
    if not active_services:
        raise HTTPException(status_code=400, detail="Cannot accept an offer without active services")
    if any(service.quoted_price is None for service in active_services):
        raise HTTPException(status_code=400, detail="Cannot accept an offer with unpriced services")

    offer.status = workflow.ACCEPTED
    for service in active_services:
        entry = db.query(models.TraceabilityEntry).filter(
            models.TraceabilityEntry.service_id == service.id
        ).first()
        if not entry:
            entry = models.TraceabilityEntry(
                offer_id=offer.id,
                service_id=service.id,
                request_date=offer.created_at,
            )
            db.add(entry)
        entry.acceptance_date = datetime.now()

    generate_acceptance_pdf(db, offer)
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
