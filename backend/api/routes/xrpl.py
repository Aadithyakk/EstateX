"""
XRPL integration routes.
Exposes ledger info, transaction tracking, DEX prices, and trustline operations.
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from typing import List, Optional
import logging

from ...services.xrpl_ledger import get_ledger_service
from ...config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/xrpl", tags=["xrpl"])


# ============================================
# SCHEMAS
# ============================================

class LedgerInfoResponse(BaseModel):
    ledger_index: int
    network: str
    server: str
    status: str


class TransactionStatusResponse(BaseModel):
    tx_hash: str
    status: str  # submitted, pending, validated
    ledger_index: Optional[int] = None
    timestamp: Optional[str] = None


class TrustlineCreateRequest(BaseModel):
    account: str
    issuer: str
    currency: str = "SGPROP"
    limit: str = "1000000000"


class DEXPriceResponse(BaseModel):
    pair: str
    bid: float
    ask: float
    spread: float
    source: str


class ActivityEventResponse(BaseModel):
    title: str
    detail: str
    timestamp: str
    type: str  # ledger_closed, tx_validated, trustline_created, etc.


# ============================================
# ROUTES
# ============================================

@router.get("/info", response_model=LedgerInfoResponse)
async def get_ledger_info(request: Request):
    """Get current XRPL ledger information."""
    settings = get_settings()
    service = get_ledger_service(settings.XRPL_WS_URL)
    
    return LedgerInfoResponse(
        ledger_index=service.latest_ledger_index or 75000000,
        network="Testnet" if "testnet" in settings.XRPL_RPC_URL.lower() else "Mainnet",
        server=settings.XRPL_WS_URL,
        status="connected" if service.client else "disconnected"
    )


@router.get("/tx/{tx_hash}", response_model=TransactionStatusResponse)
async def get_transaction_status(tx_hash: str):
    """Get status of a submitted transaction."""
    service = get_ledger_service()
    
    # Check cache first
    cached = service.get_tracked_transaction(tx_hash)
    if cached:
        return TransactionStatusResponse(
            tx_hash=tx_hash,
            status=cached["status"],
            timestamp=cached["submitted_at"]
        )
    
    # Try to fetch from ledger
    try:
        status = await service.get_tx_status(tx_hash)
        return TransactionStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error fetching tx status: {e}")
        raise HTTPException(status_code=404, detail="Transaction not found")


@router.post("/trustline/create")
async def create_trustline(payload: TrustlineCreateRequest):
    """Generate a TrustSet transaction for trustline creation."""
    service = get_ledger_service()
    
    try:
        tx_obj = await service.create_trustline_tx(
            account=payload.account,
            issuer=payload.issuer,
            currency=payload.currency,
            limit=payload.limit
        )
        
        return {
            "success": True,
            "message": "Trustline transaction generated",
            "transaction": tx_obj,
            "next_step": "Sign and submit this transaction to XRPL"
        }
    except Exception as e:
        logger.error(f"Error creating trustline: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dex/price", response_model=DEXPriceResponse)
async def get_dex_price(pair: str = Query("SGPROP/XRP")):
    """Get current DEX/AMM price for trading pair."""
    service = get_ledger_service()
    
    try:
        price_info = await service.get_dex_prices(pair)
        return DEXPriceResponse(**price_info)
    except Exception as e:
        logger.error(f"Error fetching DEX price: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch price")


@router.get("/activity/recent", response_model=List[ActivityEventResponse])
async def get_recent_activity(limit: int = Query(10, le=50)):
    """Get recent XRPL activity (mock for demo)."""
    # In production, this would come from ledger stream
    events = [
        ActivityEventResponse(
            title="Ledger Validated",
            detail="#75000042",
            timestamp="2026-01-09T10:00:00Z",
            type="ledger_closed"
        ),
        ActivityEventResponse(
            title="Trustline Authorized",
            detail="SGPROP token now holdable",
            timestamp="2026-01-09T09:59:30Z",
            type="trustline_created"
        ),
        ActivityEventResponse(
            title="Payment Validated",
            detail="5000 XRP to issuer",
            timestamp="2026-01-09T09:59:00Z",
            type="tx_validated"
        ),
    ]
    return events[:limit]


@router.post("/tx/submit-mock")
async def submit_transaction_mock(payload: dict):
    """Submit a mock transaction (for demo/dry-run)."""
    import uuid
    
    service = get_ledger_service()
    mock_hash = "3A" + "".join(f"{x:02x}" for x in uuid.uuid4().bytes)[:54].upper()
    
    service.track_transaction(
        mock_hash,
        payload.get("type", "unknown"),
        payload.get("metadata")
    )
    
    return {
        "success": True,
        "tx_hash": mock_hash,
        "status": "submitted",
        "message": "Transaction submitted (mock mode)",
        "explorer_url": f"https://testnet.xrpl.ws/?tx={mock_hash}"
    }


@router.get("/health")
async def xrpl_health():
    """Check XRPL service health."""
    service = get_ledger_service()
    settings = get_settings()
    
    return {
        "service": "xrpl",
        "status": "ok",
        "ledger_index": service.latest_ledger_index or 75000000,
        "network": "Testnet",
        "dry_run_mode": settings.XRPL_DRY_RUN,
        "ws_url": settings.XRPL_WS_URL
    }
