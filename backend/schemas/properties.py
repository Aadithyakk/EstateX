from pydantic import BaseModel
from typing import Optional


class PropertyCreate(BaseModel):
    town: Optional[str]
    flat_type: Optional[str]
    block: Optional[str]
    street_name: Optional[str]
    storey_range: Optional[str]
    floor_area_sqm: Optional[float]
    flat_model: Optional[str]
    lease_commence_date: Optional[str]


class PropertyOut(PropertyCreate):
    id: int

    class Config:
        orm_mode = True
