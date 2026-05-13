from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from backend import models, schemas, auth as auth_service
from backend.dependencies import get_db
from backend import workflow

logger = logging.getLogger("sgo")
router = APIRouter(prefix="/api", tags=["invoice"])

@router.get("/technician/billing-clients", response_model=List[schemas.ClientResponse])
def get_billing_clients(current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Return clients who have active offers managed by the current technician.
    
    Security: Uses current_user.id from JWT instead of a query parameter
    to prevent IDOR (a technician querying another technician's clients).
    """
    clients = db.query(models.Client).join(models.Offer).filter(
        models.Offer.manager_id == current_user.id,
        models.Offer.status.in_(workflow.BILLABLE_OFFER_STATUSES)
    ).distinct().all()
    return clients

@router.get("/technician/billing-offers", response_model=List[schemas.OfferResponse])
def get_billing_offers(client_id: int, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Return billable offers for a specific client managed by the current technician.
    
    Security: Uses current_user.id from JWT instead of a query parameter
    to prevent IDOR (a technician viewing another technician's billable offers).
    """
    offers = db.query(models.Offer).filter(
        models.Offer.client_id == client_id,
        models.Offer.manager_id == current_user.id,
        models.Offer.status.in_(workflow.BILLABLE_OFFER_STATUSES)
    ).all()
    return offers

@router.post("/technician/invoices")
def create_invoice(invoice_data: schemas.InvoiceCreate, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Create an invoice grouping offers.
    
    Security: Verifies that the technician creating the invoice is the one
    specified in the data (or is an Admin). Also validates that all offers
    belong to this technician.
    """
    # IDOR Protection: only the technician themselves (or Admin) can create their invoice
    if invoice_data.technician_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="You can only create invoices for yourself")

    client = db.query(models.Client).filter(models.Client.id == invoice_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    technician = db.query(models.Technician).filter(models.Technician.id == invoice_data.technician_id).first()
    if not technician:
        raise HTTPException(status_code=404, detail="Technician not found")

    validated_offers = []
    # SECURITY FIX: Never trust the total_price sent by the frontend.
    # A malicious user could send a total of 0.0 for 10 offers.
    # We always recalculate the total price on the server side before creating the invoice.
    recalculated_total = 0.0

    # Validate that all offers belong to the invoicing technician and client.
    for o_id in invoice_data.offer_ids:
        offer = db.query(models.Offer).filter(models.Offer.id == o_id).first()
        if not offer:
            raise HTTPException(status_code=404, detail=f"Offer {o_id} not found")
        if offer.manager_id != invoice_data.technician_id:
            raise HTTPException(status_code=403, detail=f"Offer {o_id} is not managed by the selected technician")
        if offer.client_id != invoice_data.client_id:
            raise HTTPException(status_code=400, detail=f"Offer {o_id} does not belong to the selected client")
        if offer.invoice_id is not None:
            raise HTTPException(status_code=400, detail=f"Offer {o_id} is already linked to an invoice")
        if offer.status not in workflow.BILLABLE_OFFER_STATUSES:
            raise HTTPException(status_code=400, detail=f"Offer {o_id} is not in a billable status (current: '{offer.status}')")
        active_services = workflow.active_services(offer)
        if not active_services:
            raise HTTPException(status_code=400, detail=f"Offer {o_id} has no active services")
        if any(service.quoted_price is None for service in active_services):
            raise HTTPException(status_code=400, detail=f"Offer {o_id} has unpriced services")
        validated_offers.append(offer)
        recalculated_total += workflow.sum_offer_total(offer)

    recalculated_total = round(recalculated_total, 2)

    try:
        new_invoice = models.Invoice(
            client_id=invoice_data.client_id,
            technician_id=invoice_data.technician_id,
            total_price=recalculated_total,
            comment=invoice_data.comment,
            status=workflow.INVOICED
        )
        db.add(new_invoice)
        db.flush()
        db.refresh(new_invoice)

        for offer in validated_offers:
            offer.status = workflow.INVOICED
            offer.invoice_id = new_invoice.id

        db.commit()
        db.refresh(new_invoice)

        return {
            "id": new_invoice.id,
            "client_id": new_invoice.client_id,
            "technician_id": new_invoice.technician_id,
            "technician_first_name": technician.first_name,
            "technician_last_name": technician.last_name,
            "total_price": new_invoice.total_price,
            "comment": new_invoice.comment,
            "status": new_invoice.status,
            "created_at": new_invoice.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Invoice creation failed: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to create invoice")

@router.get("/technician/invoices/all")
def get_all_invoices(current_user = Depends(auth_service.require_admin), db: Session = Depends(get_db)):
    """Get the full invoice history (admin only)."""
    invoices = db.query(models.Invoice).order_by(models.Invoice.created_at.desc()).all()
    result = []
    for inv in invoices:
        tech = db.query(models.Technician).filter(models.Technician.id == inv.technician_id).first()
        client = db.query(models.Client).filter(models.Client.id == inv.client_id).first()
        offers_data = []
        for o in inv.offers:
            offers_data.append({
                "id": o.id, "status": o.status, "technician_comment": o.technician_comment,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "services": [{
                    "id": s.id, "service_name": s.service_name, "hours": s.hours,
                    "quoted_price": s.quoted_price, "comment": s.comment,
                    "technician": { "first_name": s.technician.first_name, "last_name": s.technician.last_name } if s.technician else None
                } for s in o.services if not s.is_deleted]
            })
        result.append({
            "id": inv.id, "client_id": inv.client_id, 
            "client_first_name": client.first_name if client else None, "client_last_name": client.last_name if client else None,
            "client_email": client.email if client else None, "client_entity": client.entity if client else None,
            "technician_id": inv.technician_id, "technician_first_name": tech.first_name if tech else None,
            "technician_last_name": tech.last_name if tech else None, "total_price": inv.total_price,
            "comment": inv.comment, "status": inv.status, "created_at": inv.created_at.isoformat(),
            "offers": offers_data
        })
    return result

@router.post("/technician/invoices/{invoice_id}/pay")
def pay_invoice(invoice_id: int, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Mark an invoice and all linked offers as paid.
    
    Security: Only the technician who owns the invoice or an Admin can mark it as paid.
    """
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # IDOR Protection: only the invoice owner or Admin can mark as paid
    if invoice.technician_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only the invoice owner or an Admin can mark this invoice as paid")

    if invoice.status == workflow.PAID:
        return {"message": "Invoice was already paid"}
    if invoice.status != workflow.INVOICED:
        raise HTTPException(status_code=400, detail=f"Cannot mark invoice with status '{invoice.status}' as paid")

    invoice.status = workflow.PAID
    for offer in invoice.offers:
        offer.status = workflow.PAID
    db.commit()
    return {"message": "Invoice and linked offers marked as paid successfully"}
