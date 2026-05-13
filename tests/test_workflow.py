from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend import workflow


def test_active_services_ignore_deleted_services():
    offer = SimpleNamespace(
        services=[
            SimpleNamespace(is_deleted=False, quoted_price=10.0),
            SimpleNamespace(is_deleted=True, quoted_price=999.0),
            SimpleNamespace(is_deleted=False, quoted_price=5.5),
        ]
    )

    assert len(workflow.active_services(offer)) == 2
    assert workflow.sum_offer_total(offer) == 15.5


def test_only_requested_offers_are_editable():
    workflow.ensure_offer_editable(SimpleNamespace(status=workflow.REQUESTED))

    with pytest.raises(HTTPException):
        workflow.ensure_offer_editable(SimpleNamespace(status=workflow.QUOTED))


def test_manager_or_admin_permission():
    offer = SimpleNamespace(manager_id=10)
    manager = SimpleNamespace(id=10, app_role="technician", privilege_level="Technician")
    stranger = SimpleNamespace(id=11, app_role="technician", privilege_level="Technician")
    admin = SimpleNamespace(id=99, app_role="technician", privilege_level="Admin")

    workflow.ensure_manager_or_admin(offer, manager)
    workflow.ensure_manager_or_admin(offer, admin)

    with pytest.raises(HTTPException):
        workflow.ensure_manager_or_admin(offer, stranger)


def test_invalid_offer_status_is_rejected():
    workflow.ensure_valid_offer_status(workflow.COMPLETED)

    with pytest.raises(HTTPException):
        workflow.ensure_valid_offer_status("finished")
