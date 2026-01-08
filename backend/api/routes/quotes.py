from fastapi import APIRouter, HTTPException, Depends
from backend.db.session import get_db_session
from backend.db import models
from backend.services.pricing import PricingService

router = APIRouter(prefix="/quote")


@router.get("/")
def get_quote(offering_id: int, side: str = "buy", qty: float = 1.0, db=Depends(get_db_session)):
    offering = db.query(models.Offering).filter(models.Offering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Offering not found")
    val = db.query(models.Valuation).filter(models.Valuation.property_id == offering.property_id).order_by(models.Valuation.created_at.desc()).first()
    if not val:
        raise HTTPException(status_code=400, detail="No valuation available")
    pricing = PricingService()
    q = pricing.quote(predicted_price=val.predicted_price, side=side, qty=qty)
    return q
