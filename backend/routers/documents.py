import io
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from docxtpl import DocxTemplate

from backend import models, auth as auth_service
from backend.dependencies import get_db

router = APIRouter(prefix="/api/technician", tags=["documents"])

TEMPLATE_PATH = Path("docs_oficiales/CSS_RG-10. Oferta Ed.05_ES.docx")


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
