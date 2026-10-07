from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend import models, auth as auth_service, workflow
from backend.dependencies import get_db
from backend.pdf_documents import (
    generate_acceptance_pdf,
    generate_invoice_pdf,
    generate_offer_pdf,
    generate_request_pdf,
    latest_document,
    load_document_bytes,
)

router = APIRouter(prefix="/api/technician", tags=["documents"])
client_router = APIRouter(prefix="/api/client", tags=["documents"])


def _latest_existing_document(db, *, document_type, offer_id=None, invoice_id=None):
    record = latest_document(db, document_type=document_type, offer_id=offer_id, invoice_id=invoice_id)
    if not record:
        return None
    content = load_document_bytes(record.file_path)
    if content is None:
        return None
    record._content = content
    return record


def _pdf_response(record):
    content = getattr(record, "_content", None)
    if content is None:
        content = load_document_bytes(record.file_path)
    if content is None:
        raise HTTPException(status_code=404, detail="Stored document not found")
    name = Path(record.file_path).name
    return Response(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


def _ensure_offer_document_access(offer, current_user):
    if offer.manager_id is None and offer.status == workflow.REQUESTED:
        return
    workflow.ensure_manager_or_admin(
        offer,
        current_user,
        "Only the assigned manager or an Admin can download this offer document",
    )


def _ensure_invoice_document_access(invoice, current_user):
    if invoice.technician_id != current_user.id and not workflow.is_admin(current_user):
        raise HTTPException(status_code=403, detail="Only the invoice owner or an Admin can download this invoice")


@router.get("/offers/{offer_id}/document.pdf")
def generate_offer_pdf_document(
    offer_id: int,
    current_user=Depends(auth_service.require_technician_or_higher),
    db: Session = Depends(get_db),
):
    """
    Generate, store, and return a PDF offer document.
    This replaces the older Word document flow by providing a final, immutable
    PDF. The generated PDF is automatically registered in the database with a 
    SHA-256 hash for auditing purposes.
    """
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    _ensure_offer_document_access(offer, current_user)
    if offer.status == workflow.REQUESTED:
        raise HTTPException(status_code=400, detail="Cannot generate an offer PDF before it is quoted")

    record = _latest_existing_document(db, document_type="offer", offer_id=offer.id)
    if not record:
        record = generate_offer_pdf(db, offer, technician_id=current_user.id)
    return _pdf_response(record)


@router.get("/offers/{offer_id}/request.pdf")
def generate_request_pdf_document(
    offer_id: int,
    current_user=Depends(auth_service.require_technician_or_higher),
    db: Session = Depends(get_db),
):
    """Return the stored service request PDF for an offer."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    _ensure_offer_document_access(offer, current_user)

    record = _latest_existing_document(db, document_type="request", offer_id=offer.id)
    if not record:
        record = generate_request_pdf(db, offer, technician_id=current_user.id)
    return _pdf_response(record)


@router.get("/offers/{offer_id}/acceptance.pdf")
def generate_acceptance_pdf_document(
    offer_id: int,
    current_user=Depends(auth_service.require_technician_or_higher),
    db: Session = Depends(get_db),
):
    """Return the stored offer acceptance PDF."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    _ensure_offer_document_access(offer, current_user)
    if offer.status not in {workflow.ACCEPTED, workflow.COMPLETED, workflow.INVOICED, workflow.PAID}:
        raise HTTPException(status_code=400, detail="Cannot generate an acceptance PDF before the offer is accepted")

    record = _latest_existing_document(db, document_type="acceptance", offer_id=offer.id)
    if not record:
        record = generate_acceptance_pdf(db, offer, technician_id=current_user.id)
    return _pdf_response(record)


@router.get("/invoices/{invoice_id}/document.pdf")
def generate_invoice_pdf_document(
    invoice_id: int,
    current_user=Depends(auth_service.require_technician_or_higher),
    db: Session = Depends(get_db),
):
    """Generate, store, and return a PDF invoice document."""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    _ensure_invoice_document_access(invoice, current_user)

    record = _latest_existing_document(db, document_type="invoice", invoice_id=invoice.id)
    if not record:
        record = generate_invoice_pdf(db, invoice, technician_id=current_user.id)
    return _pdf_response(record)


@client_router.get("/offers/{offer_id}/acceptance.pdf")
def generate_client_acceptance_pdf_document(
    offer_id: int,
    current_user=Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Return the stored acceptance PDF for the authenticated client."""
    if current_user.app_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can download their acceptance PDFs")

    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="This offer does not belong to you")
    if offer.status not in {workflow.ACCEPTED, workflow.COMPLETED, workflow.INVOICED, workflow.PAID}:
        raise HTTPException(status_code=400, detail="Cannot generate an acceptance PDF before the offer is accepted")

    record = _latest_existing_document(db, document_type="acceptance", offer_id=offer.id)
    if not record:
        record = generate_acceptance_pdf(db, offer)
    return _pdf_response(record)


@client_router.get("/offers/{offer_id}/request.pdf")
def generate_client_request_pdf_document(
    offer_id: int,
    current_user=Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Return the stored request PDF for the authenticated client."""
    if current_user.app_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can download their request PDFs")

    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="This offer does not belong to you")

    record = _latest_existing_document(db, document_type="request", offer_id=offer.id)
    if not record:
        record = generate_request_pdf(db, offer)
    return _pdf_response(record)


@client_router.get("/offers/{offer_id}/document.pdf")
def generate_client_offer_pdf_document(
    offer_id: int,
    current_user=Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Return a stored offer PDF for the authenticated client."""
    if current_user.app_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can download their offer PDFs")

    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    if offer.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="This offer does not belong to you")
    if offer.status == workflow.REQUESTED:
        raise HTTPException(status_code=400, detail="Cannot generate an offer PDF before it is quoted")

    record = _latest_existing_document(db, document_type="offer", offer_id=offer.id)
    if not record:
        record = generate_offer_pdf(db, offer)
    return _pdf_response(record)


@client_router.get("/invoices/{invoice_id}/document.pdf")
def generate_client_invoice_pdf_document(
    invoice_id: int,
    current_user=Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Return a stored invoice PDF for the authenticated client."""
    if current_user.app_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can download their invoice PDFs")

    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="This invoice does not belong to you")

    record = _latest_existing_document(db, document_type="invoice", invoice_id=invoice.id)
    if not record:
        record = generate_invoice_pdf(db, invoice)
    return _pdf_response(record)
