from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import csv
import io

from backend import models, schemas, auth as auth_service, workflow
from backend.dependencies import get_db

"""
Traceability Module (Quality Control & Auditing)
This module replaces a simple "text comment" with a structured database record
for each individual service within an offer. It is designed to comply with 
laboratory quality standards (e.g., ISO 9001, RG-12 forms) by tracking 
essential dates, verification status, conformity, and observations.
"""

router = APIRouter(prefix="/api/technician", tags=["traceability"])


def _csv_safe(value):
    if value is None:
        return ""
    text = str(value)
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _traceability_response(offer: models.Offer, service: models.Service, entry: models.TraceabilityEntry | None):
    client = offer.client
    return {
        "id": entry.id if entry else None,
        "offer_id": offer.id,
        "service_id": service.id,
        "service_name": service.service_name,
        "client_name": f"{client.first_name} {client.last_name}" if client else "",
        "client_type": client.entity if client else "",
        "group_internal": client.grupo if client else None,
        "internal_account": client.cuenta_interna if client else None,
        "project_code": client.codigo_proyecto if client else None,
        "quoted_price": service.quoted_price,
        "hours": service.hours,
        "request_date": entry.request_date if entry else offer.created_at,
        "acceptance_date": entry.acceptance_date if entry else None,
        "delivery_date": entry.delivery_date if entry else None,
        "mina_autoservicio": entry.mina_autoservicio if entry else None,
        "sample_provided": entry.sample_provided if entry else None,
        "verification": entry.verification if entry else None,
        "charge_note": entry.charge_note if entry else None,
        "conformity": entry.conformity if entry else None,
        "observations": entry.observations if entry else None,
    }


@router.get("/offers/{offer_id}/traceability", response_model=List[schemas.TraceabilityEntryResponse])
def get_offer_traceability(
    offer_id: int,
    current_user=Depends(auth_service.require_technician_or_higher),
    db: Session = Depends(get_db),
):
    """Return one RG-12-style traceability row per active service in an offer."""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    workflow.ensure_manager_or_admin(offer, current_user, "Only the assigned manager or an Admin can view this traceability")

    rows = []
    for service in workflow.active_services(offer):
        entry = db.query(models.TraceabilityEntry).filter(models.TraceabilityEntry.service_id == service.id).first()
        rows.append(_traceability_response(offer, service, entry))
    return rows


@router.put("/offers/{offer_id}/traceability", response_model=List[schemas.TraceabilityEntryResponse])
def update_offer_traceability(
    offer_id: int,
    payload: schemas.TraceabilityBulkUpdate,
    current_user=Depends(auth_service.require_technician_or_higher),
    db: Session = Depends(get_db),
):
    """
    Create or update traceability rows for active services in an offer.
    This allows technicians to fill in the RG-12 form data incrementally.
    """
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    workflow.ensure_manager_or_admin(offer, current_user, "Only the assigned manager or an Admin can update this traceability")
    if offer.status in [workflow.INVOICED, workflow.PAID]:
        raise HTTPException(status_code=400, detail="Traceability for invoiced or paid offers is locked")

    active_service_ids = {service.id for service in workflow.active_services(offer)}
    submitted_service_ids = {entry.service_id for entry in payload.entries}
    if not submitted_service_ids.issubset(active_service_ids):
        raise HTTPException(status_code=400, detail="Traceability contains services outside this offer")

    for entry_data in payload.entries:
        service = db.query(models.Service).filter(models.Service.id == entry_data.service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {entry_data.service_id} not found")
        workflow.ensure_service_belongs_to_offer(service, offer_id)
        if service.is_deleted:
            raise HTTPException(status_code=400, detail=f"Service {entry_data.service_id} is deleted")

        entry = db.query(models.TraceabilityEntry).filter(
            models.TraceabilityEntry.service_id == entry_data.service_id
        ).first()
        if not entry:
            entry = models.TraceabilityEntry(offer_id=offer.id, service_id=service.id)
            db.add(entry)

        entry.request_date = entry_data.request_date
        entry.acceptance_date = entry_data.acceptance_date
        entry.delivery_date = entry_data.delivery_date
        entry.mina_autoservicio = entry_data.mina_autoservicio
        entry.sample_provided = entry_data.sample_provided
        entry.verification = entry_data.verification
        entry.charge_note = entry_data.charge_note
        entry.conformity = entry_data.conformity
        entry.observations = entry_data.observations

    db.commit()
    return get_offer_traceability(offer_id, current_user, db)


@router.get("/offers/{offer_id}/traceability.csv")
def export_offer_traceability_csv(
    offer_id: int,
    current_user=Depends(auth_service.require_technician_or_higher),
    db: Session = Depends(get_db),
):
    """Export offer traceability as a spreadsheet-friendly CSV."""
    rows = get_offer_traceability(offer_id, current_user, db)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow([
        "Codigo",
        "Cliente",
        "Tipo cliente",
        "Grupo cliente interno",
        "Cuenta interna",
        "Proyecto",
        "Fecha peticion",
        "Fecha aceptacion",
        "MiNa/Autoservicio",
        "Aporta muestra",
        "Verificacion",
        "Servicio",
        "Fecha de entrega",
        "Precio",
        "Horas",
        "Nota de cargo / Hoja de servicio",
        "Realizado y conforme",
        "Observaciones",
    ])

    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    code = offer.reference if offer else str(offer_id)
    for row in rows:
        writer.writerow([
            _csv_safe(code),
            _csv_safe(row["client_name"]),
            _csv_safe(row["client_type"]),
            _csv_safe(row["group_internal"]),
            _csv_safe(row["internal_account"]),
            _csv_safe(row["project_code"]),
            _csv_safe(row["request_date"]),
            _csv_safe(row["acceptance_date"]),
            _csv_safe(row["mina_autoservicio"]),
            _csv_safe(row["sample_provided"]),
            _csv_safe(row["verification"]),
            _csv_safe(row["service_name"]),
            _csv_safe(row["delivery_date"]),
            _csv_safe(row["quoted_price"]),
            _csv_safe(row["hours"]),
            _csv_safe(row["charge_note"]),
            _csv_safe(row["conformity"]),
            _csv_safe(row["observations"]),
        ])

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="trazabilidad_{offer_id}.csv"'},
    )
