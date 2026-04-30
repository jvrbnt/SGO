from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas, auth as auth_service
from backend.dependencies import get_db

router = APIRouter(prefix="/api/technician", tags=["technician"])

@router.get("/offers", response_model=List[schemas.OfferResponse])
def get_all_offers(current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Return all offers in the system."""
    return db.query(models.Offer).all()

@router.get("/offers/{offer_id}", response_model=schemas.OfferResponse)
def get_single_offer(offer_id: int, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Return a single offer by ID."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer

@router.put("/offers/{offer_id}/review")
def finalize_review_and_send(offer_id: int, review_data: schemas.OfferReviewUpdate, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Finalize a technician review and send the quotation to the client."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    offer.status = "quoted"
    offer.technician_comment = review_data.technician_comment

    for s_data in review_data.services:
        service = db.query(models.Service).filter(models.Service.id == s_data.id).first()
        if service and not service.is_deleted:
            service.hours = s_data.hours
            service.comment = s_data.comment
            if s_data.quoted_price is not None:
                service.quoted_price = s_data.quoted_price

    db.commit()
    return {"message": "Offer sent to client as QUOTED"}

@router.patch("/offers/{offer_id}")
def update_status_simple(offer_id: int, new_status: str, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Update an offer's status directly."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    offer.status = new_status
    db.commit()
    return {"message": "Status updated"}

@router.patch("/offers/{offer_id}/assign")
def assign_offer(offer_id: int, tech_id: int, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Assign a technician as manager of an offer and all pending offers."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    offer.manager_id = tech_id
    db.commit()
    return {"message": "Offer assigned successfully"}

@router.patch("/services/{service_id}/assign")
def assign_service(service_id: int, tech_id: int, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Assign a technician to a specific service within an offer."""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.technician_id = tech_id
    db.commit()
    return {"message": "Service assigned successfully"}

@router.patch("/services/{service_id}/unassign")
def unassign_service(service_id: int, tech_id: int, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Unassign a technician from a service."""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if service.offer.status != "requested":
        raise HTTPException(status_code=400, detail="Cannot unassign from an offer that is already quoted/accepted")
    if service.technician_id != tech_id:
        raise HTTPException(status_code=403, detail="Only the assigned technician can unassign themselves")
    service.technician_id = None
    db.commit()
    return {"message": "Service unassigned successfully"}

@router.patch("/offers/{offer_id}/unassign")
def unassign_offer(offer_id: int, tech_id: int, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Unassign a manager from an offer."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.status != "requested":
        raise HTTPException(status_code=400, detail="Cannot unassign from quoted/accepted offers")
    if offer.manager_id != tech_id:
        raise HTTPException(status_code=403, detail="Only the current manager can unassign themselves")

    offer.manager_id = None
    db.commit()
    return {"message": "Unassigned from offer successfully"}

@router.patch("/services/{service_id}/status")
def update_service_status(service_id: int, new_status: str, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Toggle a service status between 'pending' and 'done'. Auto-completes the offer when all services are done."""
    if new_status not in ["pending", "done"]:
        raise HTTPException(status_code=400, detail="Status must be 'pending' or 'done'")

    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    offer = service.offer
    if offer.status not in ["accepted", "finished"]:
        raise HTTPException(status_code=400, detail=f"Cannot update service status on a '{offer.status}' offer")

    if service.technician_id != current_user.id and current_user.privilege_level != "Admin":
        raise HTTPException(status_code=403, detail="Only the assigned technician can change the service status")

    service.status = new_status
    db.commit()

    # Check if all active services are done → auto-complete offer
    active_services = [s for s in offer.services if not s.is_deleted]
    all_done = len(active_services) > 0 and all(s.status == "done" for s in active_services)

    if all_done and offer.status == "accepted":
        offer.status = "completed"
        db.commit()
        return {"message": "Service marked as done. All services completed — offer ready to be invoiced!", "offer_finished": True}
    elif not all_done and offer.status == "completed":
        # Revert offer if a service goes back to pending
        offer.status = "accepted"
        db.commit()
        return {"message": "Service reverted to pending. Offer status reverted to accepted.", "offer_finished": False}

    db.commit()
    return {"message": f"Service status updated to '{new_status}'", "offer_finished": False}

@router.delete("/services/{service_id}")
def delete_service(service_id: int, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Logically delete a service."""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service.offer.status not in ["requested", "quoted"]:
        raise HTTPException(status_code=400, detail=f"Cannot delete services from '{service.offer.status}' offer")

    service.is_deleted = True
    db.commit()
    return {"message": "Service logically deleted"}

@router.post("/offers/{offer_id}/services")
def add_service_to_offer(offer_id: int, service_in: schemas.ServiceCreateInline, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Add a new service to an existing offer."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.status not in ["requested", "quoted"]:
        raise HTTPException(status_code=400, detail="Cannot add services to this offer")

    catalog_item = db.query(models.ServiceCatalog).filter(
        models.ServiceCatalog.name == service_in.service_name
    ).first()

    new_service = models.Service(
        service_name=service_in.service_name,
        hours=service_in.hours,
        original_hours=service_in.hours,
        comment=service_in.comment,
        offer_id=offer.id,
        catalog_id=catalog_item.id if catalog_item else None,
        added_by_technician=True
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return {"message": "Service added successfully", "service_id": new_service.id}
