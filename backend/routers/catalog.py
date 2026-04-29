from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas, auth as auth_service
from backend.dependencies import get_db

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

@router.get("", response_model=List[schemas.ServiceCatalogResponse])
def get_catalog(current_user = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """Return the full service catalog with pricing tiers."""
    return db.query(models.ServiceCatalog).all()

@router.put("/{item_id}", response_model=schemas.ServiceCatalogResponse)
def update_catalog_price(item_id: int, price_update: schemas.ServiceCatalogPriceUpdate, current_user = Depends(auth_service.require_technician_or_higher), db: Session = Depends(get_db)):
    """Update pricing tiers for a catalog item. Requires Technician role."""
    catalog_item = db.query(models.ServiceCatalog).filter(models.ServiceCatalog.id == item_id).first()
    if not catalog_item:
        raise HTTPException(status_code=404, detail="Catalog item not found")

    if price_update.price_internal is not None:
        catalog_item.price_internal = price_update.price_internal
    if price_update.price_csic is not None:
        catalog_item.price_csic = price_update.price_csic
    if price_update.price_public is not None:
        catalog_item.price_public = price_update.price_public
    if price_update.price_private is not None:
        catalog_item.price_private = price_update.price_private

    db.commit()
    db.refresh(catalog_item)
    return catalog_item
