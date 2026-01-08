from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.offerings import OfferingCreate, OfferingOut
from backend.db.session import get_db_session
from backend.db import models

router = APIRouter(prefix="/offerings")


@router.post("/", response_model=OfferingOut)
def create_offering(payload: OfferingCreate, db=Depends(get_db_session)):
    off = models.Offering(**payload.dict())
    db.add(off)
    db.commit()
    db.refresh(off)
    return off
