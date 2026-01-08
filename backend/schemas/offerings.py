from pydantic import BaseModel
from typing import Optional


class OfferingCreate(BaseModel):
    property_id: int
    issuer_address: str
    currency_code: str
    total_supply: float


class OfferingOut(OfferingCreate):
    id: int

    class Config:
        orm_mode = True
