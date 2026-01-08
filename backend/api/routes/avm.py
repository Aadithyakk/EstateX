from fastapi import APIRouter, Depends, HTTPException, Request
from backend.schemas.avm import (
    AVMPredictRequest, 
    AVMPredictResponse, 
    AVMBatchRequest,
    AVMPredictResponseWithExplanation
)
from typing import List
from backend.services.avm import AVMService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/avm")


@router.post("/predict", response_model=AVMPredictResponse)
def predict(payload: AVMPredictRequest, request: Request):
    bundle = request.app.state.avm_bundle
    if not bundle:
        raise HTTPException(status_code=500, detail="AVM model not available")
    svc = AVMService(bundle)
    feats = svc.featurize(payload.dict())
    try:
        out = svc.predict(feats)
        return out
    except Exception as e:
        logger.exception("AVM predict error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch_predict")
def batch_predict(req: AVMBatchRequest, request: Request):
    bundle = request.app.state.avm_bundle
    if not bundle:
        raise HTTPException(status_code=500, detail="AVM model not available")
    svc = AVMService(bundle)
    try:
        results = svc.batch_predict([i.dict() for i in req.items])
        return {"results": results}
    except Exception as e:
        logger.exception("AVM batch_predict error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-with-explanation", response_model=AVMPredictResponseWithExplanation)
def predict_with_explanation(payload: AVMPredictRequest, request: Request):
    """Predict price with SHAP-based explainability breakdown."""
    bundle = request.app.state.avm_bundle
    if not bundle:
        raise HTTPException(status_code=500, detail="AVM model not available")
    svc = AVMService(bundle)
    feats = svc.featurize(payload.dict())
    try:
        result = svc.predict_with_explanation(feats)
        return result
    except Exception as e:
        logger.exception("AVM predict_with_explanation error")
        raise HTTPException(status_code=500, detail=str(e))

