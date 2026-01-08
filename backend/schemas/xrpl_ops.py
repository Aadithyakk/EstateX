from pydantic import BaseModel
from typing import Optional


class TrustlineRequest(BaseModel):
    user_address: str
    issuer_address: str
    currency: str
    limit: float


class AuthorizeRequest(BaseModel):
    user_address: str
    currency: str


class MintRequest(BaseModel):
    destination_address: str
    currency: str
    amount: float
