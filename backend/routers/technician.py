from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from backend import models, schemas, auth as auth_service
from backend.dependencies import get_db
from backend import workflow
from backend.pdf_documents import generate_offer_pdf

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

    workflow.ensure_manager_or_admin(offer, current_user, "Only the assigned manager or an Admin can review this offer")
    workflow.ensure_offer_editable(offer)

    active_services = workflow.active_services(offer)
    if not active_services:
        raise HTTPException(status_code=400, detail="Cannot quote an offer without active services")
    if any(service.technician_id is None for service in active_services):
        raise HTTPException(status_code=400, detail="All active services must be assigned before quoting")

    submitted_service_ids = {service_data.id for service_data in review_data.services}
    active_service_ids = {service.id for service in active_services}
    if submitted_service_ids != active_service_ids:
        raise HTTPException(status_code=400, detail="Review must include every active service and no unrelated services")

    offer.status = workflow.QUOTED
    offer.technician_comment = review_data.technician_comment

    for s_data in review_data.services:
        service = db.query(models.Service).filter(models.Service.id == s_data.id).first()
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {s_data.id} not found")
        workflow.ensure_service_belongs_to_offer(service, offer_id)
        if service.is_deleted:
            raise HTTPException(status_code=400, detail=f"Service {s_data.id} is deleted")
        if s_data.quoted_price is None:
            raise HTTPException(status_code=400, detail=f"Service {s_data.id} is missing a quoted price")

        service.hours = s_data.hours
        service.comment = s_data.comment
        service.quoted_price = s_data.quoted_price

    generate_offer_pdf(db, offer, technician_id=current_user.id)
    return {"message": "Offer sent to client as QUOTED"}

@router.patch("/offers/{offer_id}")
def update_status_simple(offer_id: int, new_status: str, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Update an offer's status directly."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    workflow.ensure_valid_offer_status(new_status)
    workflow.ensure_manager_or_admin(offer, current_user, "Only the assigned manager or an Admin can update this offer's status")
    if not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Manual status changes require Admin privileges")
    if offer.status in workflow.LOCKED_OFFER_STATUSES and new_status != offer.status:
        raise HTTPException(status_code=400, detail="Locked offers cannot be manually changed")
        
    offer.status = new_status
    db.commit()
    return {"message": "Status updated"}

@router.patch("/offers/{offer_id}/assign")
def assign_offer(offer_id: int, tech_id: Optional[int] = None, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Assign a technician as manager of an offer and all pending offers."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    workflow.ensure_offer_editable(offer)

    target_tech_id = tech_id or current_user.id
    if target_tech_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only an Admin can assign offers to another technician")

    target_tech = db.query(models.Technician).filter(models.Technician.id == target_tech_id).first()
    if not target_tech:
        raise HTTPException(status_code=404, detail="Technician not found")

    if offer.manager_id is not None and offer.manager_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Offer is already assigned. Only the current manager or an Admin can reassign it.")

    offer.manager_id = target_tech_id
    db.commit()
    return {"message": "Offer assigned successfully"}

@router.patch("/services/{service_id}/assign")
def assign_service(service_id: int, tech_id: Optional[int] = None, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Assign a technician to a specific service within an offer."""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    workflow.ensure_offer_editable(service.offer)

    target_tech_id = tech_id or current_user.id
    if target_tech_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only an Admin can assign services to another technician")
    target_tech = db.query(models.Technician).filter(models.Technician.id == target_tech_id).first()
    if not target_tech:
        raise HTTPException(status_code=404, detail="Technician not found")
    if service.technician_id is not None and service.technician_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Service is already assigned")

    service.technician_id = target_tech_id
    db.commit()
    return {"message": "Service assigned successfully"}

@router.patch("/services/{service_id}/unassign")
def unassign_service(service_id: int, tech_id: Optional[int] = None, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Unassign a technician from a service."""
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if service.offer.status != workflow.REQUESTED:
        raise HTTPException(status_code=400, detail="Cannot unassign from an offer that is already quoted/accepted")
    target_tech_id = tech_id or current_user.id
    if target_tech_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only an Admin can unassign another technician")
    if service.technician_id != target_tech_id:
        raise HTTPException(status_code=403, detail="Only the assigned technician can unassign themselves")
    service.technician_id = None
    db.commit()
    return {"message": "Service unassigned successfully"}

@router.patch("/offers/{offer_id}/unassign")
def unassign_offer(offer_id: int, tech_id: Optional[int] = None, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Unassign a manager from an offer."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.status != workflow.REQUESTED:
        raise HTTPException(status_code=400, detail="Cannot unassign from quoted/accepted offers")
    target_tech_id = tech_id or current_user.id
    if target_tech_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only an Admin can unassign another technician")
    if offer.manager_id != target_tech_id:
        raise HTTPException(status_code=403, detail="Only the current manager can unassign themselves")

    offer.manager_id = None
    db.commit()
    return {"message": "Unassigned from offer successfully"}

@router.patch("/services/{service_id}/status")
def update_service_status(service_id: int, new_status: str, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Toggle a service status between 'pending' and 'done'. Auto-completes the offer when all services are done."""
    if new_status not in workflow.SERVICE_STATUSES:
        raise HTTPException(status_code=400, detail="Status must be 'pending' or 'done'")

    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    offer = service.offer
    if offer.status not in [workflow.ACCEPTED, workflow.COMPLETED]:
        raise HTTPException(status_code=400, detail=f"Cannot update service status on a '{offer.status}' offer")

    if service.technician_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only the assigned technician can change the service status")

    service.status = new_status
    db.commit()

    # SECURITY & WORKFLOW FIX: Check if all active services are done → auto-complete offer.
    # This prevents offers from getting stuck in "accepted" state forever.
    active_services = workflow.active_services(offer)
    all_done = len(active_services) > 0 and all(s.status == workflow.DONE for s in active_services)

    if all_done and offer.status == workflow.ACCEPTED:
        offer.status = workflow.COMPLETED
        db.commit()
        return {"message": "Service marked as done. All services completed — offer ready to be invoiced!", "offer_finished": True}
    elif not all_done and offer.status == workflow.COMPLETED:
        # Revert offer if a service goes back to pending
        offer.status = workflow.ACCEPTED
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

    workflow.ensure_manager_or_admin(service.offer, current_user, "Only the assigned manager or an Admin can delete services from this offer")

    workflow.ensure_offer_editable(service.offer)

    service.is_deleted = True
    db.commit()
    return {"message": "Service logically deleted"}

@router.post("/offers/{offer_id}/services")
def add_service_to_offer(offer_id: int, service_in: schemas.ServiceCreateInline, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Add a new service to an existing offer."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    workflow.ensure_manager_or_admin(offer, current_user, "Only the assigned manager or an Admin can add services to this offer")

    workflow.ensure_offer_editable(offer)

    catalog_item = db.query(models.ServiceCatalog).filter(
        models.ServiceCatalog.name == service_in.service_name
    ).first()
    if not catalog_item:
        raise HTTPException(status_code=400, detail=f"Unknown service '{service_in.service_name}'")

    new_service = models.Service(
        service_name=catalog_item.name,
        hours=service_in.hours,
        original_hours=service_in.hours,
        comment=service_in.comment,
        offer_id=offer.id,
        catalog_id=catalog_item.id,
        added_by_technician=True
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return {"message": "Service added successfully", "service_id": new_service.id}
