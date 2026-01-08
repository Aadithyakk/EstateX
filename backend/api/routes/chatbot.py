"""
Chatbot routes for RAG-powered property & market Q&A.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.db.session import get_db_session
from backend.services.chatbot import ChatbotService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatMessage(BaseModel):
    """Chat message from user."""
    message: str
    user_id: Optional[str] = None
    property_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from chatbot."""
    response: str
    sources: Optional[list] = None


class TradeRecommendation(BaseModel):
    """Property recommendation for trading."""
    property_id: str
    block: str
    street: str
    town: str
    flat_type: str
    area_sqm: float
    price_sgd: float
    remaining_lease: Optional[str] = None
    reason: str
    buy_url: str


class RecommendationRequest(BaseModel):
    """Request for trading recommendations."""
    budget_sgd: float
    risk_profile: str = "medium"  # 'low', 'medium', 'high'
    limit: int = 5


class RecommendationResponse(BaseModel):
    """Response with trading recommendations."""
    recommendations: List[TradeRecommendation]
    message: str


@router.post("/ask", response_model=ChatResponse)
def ask_chatbot(payload: ChatMessage, db: Session = Depends(get_db_session)):
    """
    General chatbot query.
    
    Accepts a user message and returns AI-generated response with market context.
    """
    try:
        svc = ChatbotService(db)
        response = svc.chat(payload.message, payload.user_id)
        return ChatResponse(response=response)
    except Exception as e:
        logger.exception(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.post("/property/{property_id}/ask", response_model=ChatResponse)
def ask_about_property(property_id: str, payload: ChatMessage, db: Session = Depends(get_db_session)):
    """
    Ask question about a specific property.
    
    Provides property-specific context and answers questions about valuation, lease, etc.
    """
    try:
        svc = ChatbotService(db)
        response = svc.answer_property_question(property_id, payload.message)
        return ChatResponse(response=response)
    except Exception as e:
        logger.exception(f"Property chatbot error: {e}")
        raise HTTPException(status_code=500, detail=f"Property question error: {str(e)}")


@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest, db: Session = Depends(get_db_session)):
    """
    Get property recommendations based on budget and risk profile.
    
    Returns a list of properties recommended for purchase with "Buy Now" buttons.
    """
    try:
        if payload.budget_sgd <= 0:
            raise ValueError("Budget must be positive")
        
        svc = ChatbotService(db)
        recommendations = svc.get_trading_recommendations(
            budget_sgd=payload.budget_sgd,
            risk_profile=payload.risk_profile,
            limit=payload.limit
        )
        
        message = f"Found {len(recommendations)} properties matching your criteria."
        if not recommendations:
            message = f"No properties found within your budget of SGD {payload.budget_sgd:,.0f}. Try increasing your budget."
        
        return RecommendationResponse(
            recommendations=recommendations,
            message=message
        )
    except Exception as e:
        logger.exception(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@router.get("/health")
def chatbot_health(db: Session = Depends(get_db_session)):
    """Health check for chatbot service."""
    try:
        svc = ChatbotService(db)
        has_openai = svc.client is not None
        return {
            "status": "ok",
            "openai_available": has_openai,
            "message": "Chatbot service running"
        }
    except Exception as e:
        logger.exception(f"Chatbot health check failed: {e}")
        return {
            "status": "error",
            "openai_available": False,
            "message": str(e)
        }
