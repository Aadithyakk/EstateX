from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.properties import PropertyCreate, PropertyOut
from backend.db.session import get_db_session
from backend.db import models

router = APIRouter(prefix="/properties")


@router.post("/", response_model=PropertyOut)
def create_property(payload: PropertyCreate, db=Depends(get_db_session)):
    prop = models.Property(**payload.dict())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("/{property_id}")
def get_property(property_id: int, db=Depends(get_db_session)):
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.get("/{property_id}/valuation/latest")
def latest_valuation(property_id: int, db=Depends(get_db_session)):
    val = db.query(models.Valuation).filter(models.Valuation.property_id == property_id).order_by(models.Valuation.created_at.desc()).first()
    if not val:
        raise HTTPException(status_code=404, detail="Valuation not found")
    return {"predicted_price": val.predicted_price, "created_at": val.created_at}
