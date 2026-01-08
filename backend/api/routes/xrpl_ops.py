from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.xrpl_ops import TrustlineRequest, AuthorizeRequest, MintRequest
from backend.services.xrpl import XRPLClient
from backend.config import get_settings

router = APIRouter(prefix="/xrpl")

settings = get_settings()


@router.post("/trustline")
def create_trustline(req: TrustlineRequest):
    client = XRPLClient(dry_run=settings.XRPL_DRY_RUN)
    res = client.create_trustline_tx(account=req.user_address, issuer=req.issuer_address, currency=req.currency, limit=str(req.limit))
    return res


@router.post("/authorize_trustline")
def authorize(req: AuthorizeRequest):
    client = XRPLClient(dry_run=settings.XRPL_DRY_RUN)
    res = client.authorize_trustline_tx(issuer_seed=settings.ISSUER_SEED, account=req.user_address, currency=req.currency)
    return res


@router.post("/mint")
def mint(req: MintRequest):
    client = XRPLClient(dry_run=settings.XRPL_DRY_RUN)
    res = client.send_issued_currency(issuer_seed=settings().ISSUER_SEED, destination=req.destination_address, currency=req.currency, amount=str(req.amount))
    return res
