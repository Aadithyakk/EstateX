from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from backend.schemas.trades import TradeRequest
from backend.db.session import get_db_session
from backend.db import models
from backend.services.xrpl import XRPLClient
from backend.config import get_settings

router = APIRouter(prefix="/trade")

settings = get_settings()


@router.post("/")
def execute_trade(req: TradeRequest, background_tasks: BackgroundTasks, db=Depends(get_db_session)):
    # Minimal checks: KYC and offering existence
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    kyc = db.query(models.KYCStatus).filter(models.KYCStatus.user_id == user.id).first()
    if not kyc or kyc.status != "approved":
        raise HTTPException(status_code=403, detail="KYC not approved")
    offering = db.query(models.Offering).filter(models.Offering.id == req.offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Offering not found")

    # price via simple anchor to latest valuation
    val = db.query(models.Valuation).filter(models.Valuation.property_id == offering.property_id).order_by(models.Valuation.created_at.desc()).first()
    if not val:
        raise HTTPException(status_code=400, detail="No valuation available")

    price = val.predicted_price
    xrpl = XRPLClient(dry_run=settings.XRPL_DRY_RUN)

    # find wallet for user
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user.id).first()
    if not wallet:
        raise HTTPException(status_code=400, detail="User wallet not found")

    # create payment (issued currency send) - simplified
    res = xrpl.send_issued_currency(issuer_seed=settings.ISSUER_SEED, destination=wallet.xrpl_address, currency=offering.currency_code, amount=str(req.quantity))
    # persist trade
    trade = models.Trade(user_id=user.id, offering_id=offering.id, side=req.side, quantity=req.quantity, price=price, status="submitted", xrpl_tx_hash=res.get("tx_hash"))
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return {"success": True, "trade_id": trade.id, "xrpl": res}
