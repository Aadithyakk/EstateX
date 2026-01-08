from pydantic import BaseModel


class TradeRequest(BaseModel):
    user_id: int
    offering_id: int
    side: str
    quantity: float
