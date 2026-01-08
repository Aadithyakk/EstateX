from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AVMPredictRequest(BaseModel):
    town: Optional[str] = None
    flat_type: Optional[str] = None
    block: Optional[str] = None
    street_name: Optional[str] = None
    storey_range: Optional[str] = None
    floor_area_sqm: Optional[float] = None
    flat_model: Optional[str] = None
    lease_commence_date: Optional[str] = None
    remaining_lease: Optional[str] = None
    txn_date: Optional[str] = None


class AVMPredictResponse(BaseModel):
    predicted_price: float
    confidence_interval: Optional[List[float]] = None


class FeatureContribution(BaseModel):
    feature_name: str
    contribution: float
    feature_value: float


class AVMExplanation(BaseModel):
    """SHAP-based explanation of valuation."""
    base_price: float
    feature_contributions: List[FeatureContribution]
    top_contributors: List[str]


class AVMPredictResponseWithExplanation(BaseModel):
    """Prediction with SHAP explainability."""
    predicted_price: float
    confidence_lower: float
    confidence_upper: float
    explanation: Optional[AVMExplanation] = None


class AVMBatchRequest(BaseModel):
    items: List[AVMPredictRequest]

