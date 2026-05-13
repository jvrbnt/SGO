"""
Workflow State Machine and Authorization Rules.
This module centralizes all business logic regarding Offer states and user permissions.
It prevents IDOR (Insecure Direct Object Reference) attacks by ensuring only authorized
users (the assigned manager or an Admin) can modify specific objects.

Offer State Flow:
1. 'requested': The client has created the offer but it hasn't been processed yet.
2. 'quoted': A technician has assigned prices and hours, and sent it back to the client.
3. 'accepted': The client has accepted the quotation. Work can begin.
4. 'completed': All services inside the offer are marked as 'done' by the technicians.
5. 'invoiced': The offer has been included in an invoice. It is now locked.
6. 'paid': The invoice has been marked as paid.
"""
from fastapi import HTTPException


REQUESTED = "requested"
QUOTED = "quoted"
ACCEPTED = "accepted"
COMPLETED = "completed"
INVOICED = "invoiced"
PAID = "paid"

OFFER_STATUSES = {REQUESTED, QUOTED, ACCEPTED, COMPLETED, INVOICED, PAID}
EDITABLE_OFFER_STATUSES = {REQUESTED}
BILLABLE_OFFER_STATUSES = {ACCEPTED, COMPLETED}
LOCKED_OFFER_STATUSES = {INVOICED, PAID}

PENDING = "pending"
DONE = "done"
SERVICE_STATUSES = {PENDING, DONE}


def is_admin(user) -> bool:
    # Helper to check if a user is a technician with Admin privileges
    return getattr(user, "app_role", None) == "technician" and getattr(user, "privilege_level", None) == "Admin"


def ensure_valid_offer_status(status: str) -> None:
    if status not in OFFER_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid offer status '{status}'")


def ensure_offer_editable(offer) -> None:
    # Security check: Prevent modifications to offers that have already been quoted or accepted
    if offer.status not in EDITABLE_OFFER_STATUSES:
        raise HTTPException(status_code=400, detail=f"Offer '{offer.status}' cannot be edited")


def ensure_offer_not_locked(offer) -> None:
    if offer.status in LOCKED_OFFER_STATUSES:
        raise HTTPException(status_code=400, detail=f"Offer '{offer.status}' is locked")


def ensure_manager_or_admin(offer, user, message: str = "Only the assigned manager or an Admin can modify this offer") -> None:
    # Core IDOR protection: only the assigned technician (manager) or an Admin can perform this action
    if offer.manager_id != user.id and not is_admin(user):
        raise HTTPException(status_code=403, detail=message)


def ensure_service_belongs_to_offer(service, offer_id: int) -> None:
    # Security check: Ensure a service is actually part of the target offer before modifying it
    if service.offer_id != offer_id:
        raise HTTPException(status_code=400, detail="Service does not belong to this offer")


def active_services(offer):
    return [service for service in offer.services if not service.is_deleted]


def sum_offer_total(offer) -> float:
    return round(sum((service.quoted_price or 0.0) for service in active_services(offer)), 2)
