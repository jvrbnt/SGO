import pytest
from pydantic import ValidationError

from backend import schemas


def test_offer_create_requires_services():
    with pytest.raises(ValidationError):
        schemas.OfferCreate(client_email="client@example.com", services=[])


def test_service_hours_must_be_positive():
    with pytest.raises(ValidationError):
        schemas.ServiceBase(service_name="SEM", hours=0)


def test_review_price_cannot_be_negative():
    with pytest.raises(ValidationError):
        schemas.ServiceUpdate(id=1, hours=1, quoted_price=-1)


def test_invoice_offer_ids_must_be_unique_and_non_empty():
    with pytest.raises(ValidationError):
        schemas.InvoiceCreate(client_id=1, technician_id=1, total_price=10, offer_ids=[])

    with pytest.raises(ValidationError):
        schemas.InvoiceCreate(client_id=1, technician_id=1, total_price=10, offer_ids=[1, 1])


def test_internal_profile_requires_billing_fields():
    with pytest.raises(ValidationError):
        schemas.ProfileUpdate(entity="Internal")

    profile = schemas.ProfileUpdate(
        entity="Internal",
        investigador_principal="Dra. Example",
        cuenta_interna="CI-001",
        codigo_proyecto="PID-001",
        grupo="FINGER",
    )

    assert profile.entity == "Internal"
