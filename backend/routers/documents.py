import io
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from docxtpl import DocxTemplate

from backend import models, auth as auth_service, workflow
from backend.dependencies import get_db
from backend.pdf_documents import generate_invoice_pdf, generate_offer_pdf, generate_request_pdf, latest_document

router = APIRouter(prefix="/api/technician", tags=["documents"])
client_router = APIRouter(prefix="/api/client", tags=["documents"])

TEMPLATE_PATH = Path("docs_oficiales/CSS_RG-10. Oferta Ed.05_ES.docx")


def _latest_existing_document(db, *, document_type, offer_id=None, invoice_id=None):
    record = latest_document(db, document_type=document_type, offer_id=offer_id, invoice_id=invoice_id)
    if record and Path(record.file_path).exists():
        return record
    return None


def _build_services_list(services):
    """Build a list of dicts with service data for the template context."""
    items = []
    total = 0.0
    for s in services:
        if s.is_deleted:
            continue
        price = s.quoted_price or 0.0
        total += price
        items.append({
            "name": s.service_name,
            "hours": s.hours,
            "price": f"{price:.2f}" if s.quoted_price is not None else "—",
            "comment": s.comment or "",
            "technician": (
                f"{s.technician.first_name} {s.technician.last_name}"
                if s.technician else "Unassigned"
            ),
        })
    return items, total


@router.get("/offers/{offer_id}/document")
def generate_offer_document(
    offer_id: int,
    current_user=Depends(auth_service.require_technician_or_higher),
    db: Session = Depends(get_db),
):
    """Generate a pre-filled Word document (.docx) from the official MiNa template.

    Uses docxtpl (Jinja2 syntax) instead of fragile run-splitting replacements.
    The Word template should use {{ variable_name }} placeholders, for example:
      {{ QUOTE }}, {{ TECHNICIAN }}, {{ DATE }}, {{ CLIENT }}, etc.
    """

    if not TEMPLATE_PATH.exists():
        raise HTTPException(status_code=500, detail="Document template not found on server")

    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    client = offer.client
    manager = offer.manager

    services_list, total_price = _build_services_list(offer.services)

    # Template context — these keys must match the {{ }} placeholders in the .docx
    context = {
        "QUOTE": offer.reference or str(offer.id),
        "TECHNICIAN": f"{manager.first_name} {manager.last_name}" if manager else "Not assigned",
        "DATE": offer.created_at.strftime("%d/%m/%Y") if offer.created_at else datetime.now().strftime("%d/%m/%Y"),
        "CLIENT": f"{client.first_name} {client.last_name}" if client else "Unknown",
        "CLIENT_EMAIL": client.email if client else "—",
        "PROJECT_CODE": client.codigo_proyecto or "—" if client else "—",
        "CCII": client.cuenta_interna or "—" if client else "—",
        "IIPP": client.investigador_principal or "—" if client else "—",
        "GRUPO": client.grupo or "—" if client else "—",
        "ENTITY": client.entity if client else "—",
        "TITLE": f"Offer {offer.reference or offer.id}",
        "SERVICES": services_list,
        "TOTAL": f"{total_price:.2f}",
        "DELIVERY": "To be confirmed",
    }

    # Load the template and render with context
    doc = DocxTemplate(str(TEMPLATE_PATH))
    doc.render(context)

    # Stream the filled document back
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    filename = f"Oferta_{offer.reference or offer.id}.docx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


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
    if offer.status == workflow.REQUESTED:
        raise HTTPException(status_code=400, detail="Cannot generate an offer PDF before it is quoted")

    record = _latest_existing_document(db, document_type="offer", offer_id=offer.id)
    if not record:
        record = generate_offer_pdf(db, offer, technician_id=current_user.id)
    return FileResponse(
        record.file_path,
        media_type="application/pdf",
        filename=Path(record.file_path).name,
    )


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

    record = _latest_existing_document(db, document_type="request", offer_id=offer.id)
    if not record:
        record = generate_request_pdf(db, offer, technician_id=current_user.id)
    return FileResponse(
        record.file_path,
        media_type="application/pdf",
        filename=Path(record.file_path).name,
    )


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

    record = _latest_existing_document(db, document_type="invoice", invoice_id=invoice.id)
    if not record:
        record = generate_invoice_pdf(db, invoice, technician_id=current_user.id)
    return FileResponse(
        record.file_path,
        media_type="application/pdf",
        filename=Path(record.file_path).name,
    )


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
    return FileResponse(
        record.file_path,
        media_type="application/pdf",
        filename=Path(record.file_path).name,
    )


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
    return FileResponse(
        record.file_path,
        media_type="application/pdf",
        filename=Path(record.file_path).name,
    )


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
    return FileResponse(
        record.file_path,
        media_type="application/pdf",
        filename=Path(record.file_path).name,
    )
