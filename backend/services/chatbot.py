"""
Chatbot service for RAG-powered property & market Q&A.
Uses OpenAI API with context from database.
"""

import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChatbotService:
    """RAG-powered chatbot for property inquiries."""
    
    def __init__(self, db_session: Session):
        """Initialize chatbot with database connection."""
        self.db = db_session
        if OPENAI_AVAILABLE:
            from ..config import get_settings
            settings = get_settings()
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
            self.model = "gpt-3.5-turbo"  # Cost-effective; upgrade to gpt-4-turbo if needed
            if not self.client:
                logger.warning("OPENAI_API_KEY not set; chatbot will return mock responses")
        else:
            self.client = None
            logger.warning("OpenAI not available; chatbot will return mock responses")

    def get_property_context(self, town: Optional[str] = None) -> str:
        """Retrieve property stats for RAG (Retrieval-Augmented Generation)."""
        try:
            from backend.db.models import Property
            
            query = self.db.query(Property)
            if town:
                query = query.filter(Property.town == town)
            
            props = query.all()
            
            if not props:
                return json.dumps({"message": "No properties found"})
            
            towns = sorted(set(p.town for p in props))
            flat_types = sorted(set(p.flat_type for p in props))
            
            stats = {
                "total_properties": len(props),
                "towns": towns,
                "flat_types": flat_types,
                "avg_floor_area": round(sum(p.floor_area_sqm for p in props) / len(props), 2),
                "avg_valuation": round(sum(p.avm_valuation_sgd for p in props) / len(props), 2),
                "price_range": {
                    "min": round(min(p.avm_valuation_sgd for p in props), 2),
                    "max": round(max(p.avm_valuation_sgd for p in props), 2),
                },
                "sample_properties": [
                    {
                        "address": f"Blk {p.block} {p.street_name}",
                        "town": p.town,
                        "flat_type": p.flat_type,
                        "area_sqm": p.floor_area_sqm,
                        "valuation_sgd": round(p.avm_valuation_sgd, 2)
                    }
                    for p in props[:3]
                ]
            }
            return json.dumps(stats)
        except Exception as e:
            logger.error(f"Error fetching property context: {e}")
            return json.dumps({"error": str(e)})

    def get_market_stats(self) -> str:
        """Get overall market statistics."""
        try:
            from backend.db.models import Property, Trade
            
            props = self.db.query(Property).all()
            trades = self.db.query(Trade).all()
            
            if not props:
                return json.dumps({"message": "No market data available"})
            
            total_trading_volume = sum(t.total_cost_sgd for t in trades if t.status == "settled") if trades else 0
            total_trades = len([t for t in trades if t.status == "settled"]) if trades else 0
            
            stats = {
                "total_properties_listed": len(props),
                "total_trading_volume_sgd": round(total_trading_volume, 2),
                "total_trades_settled": total_trades,
                "market_avg_price": round(sum(p.avm_valuation_sgd for p in props) / len(props), 2),
                "platform_info": "EstateX: fractional HDB ownership on XRPL"
            }
            return json.dumps(stats)
        except Exception as e:
            logger.error(f"Error fetching market stats: {e}")
            return json.dumps({"error": str(e)})

    def chat(self, user_message: str, property_id: Optional[str] = None) -> str:
        """Process user message and return LLM response with context."""
        
        if not self.client:
            return self._mock_response(user_message)
        
        # Build context from database
        property_context = self.get_property_context()
        market_stats = self.get_market_stats()
        
        system_prompt = f"""
You are an expert AI assistant for EstateX, a real-estate tokenization platform on XRPL.

You help users understand:
- Property valuations (powered by XGBoost AI model with SHAP explainability)
- How fractional ownership works (SGPROP tokens)
- Trading on the secondary market
- Portfolio performance
- XRPL settlement mechanics
- Trustlines and KYC requirements
- Investment recommendations based on market trends

Context - Market Data:
{market_stats}

Context - Property Statistics:
{property_context}

EXPLAINABILITY & TRANSPARENCY:
- When discussing prices, refer users to the "💡 Why This Price?" explainability section which shows:
  * Model Baseline: The starting price before feature adjustments
  * Feature Contributions: How individual factors (town, flat type, floor area, lease, etc.) increase or decrease the valuation
  * Confidence Band: The model's uncertainty range based on historical data
- Use SHAP values to explain which features most impact valuations
- Be transparent about limitations: "Our model is trained on historical HDB data; market conditions may vary"

INVESTMENT RECOMMENDATIONS:
- When users ask about buying/investing, provide insights on:
  * Price-to-area ratio vs. market average (value opportunity)
  * Lease remaining years (affects long-term value)
  * Town location and growth trends
  * Comparable properties in the area
  * Risk factors (e.g., short lease, older property)
- Always recommend checking the explainability breakdown before purchasing
- Suggest diversifying across towns/property types to reduce risk

Guidelines:
- Be concise, friendly, and accurate
- Always cite data sources (e.g., "Based on our AI model, ...")
- If unsure about something, say so clearly
- Explain technical concepts (XRPL, trustlines, SHAP, AVM) in plain language
- Current date is 2026-01-08; Singapore context

Format responses with clear structure and bullet points when appropriate.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                timeout=10,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.exception(f"OpenAI API error: {e}")
            return f"Sorry, I encountered an error: {str(e)}. Please try again or contact support."

    def answer_property_question(self, property_id: str, question: str) -> str:
        """Answer questions about a specific property."""
        try:
            from backend.db.models import Property
            
            prop = self.db.query(Property).filter(Property.id == property_id).first()
            
            if not prop:
                return "Property not found."
            
            property_detail = f"""
Property: Block {prop.block} {prop.street_name}, {prop.town}
Type: {prop.flat_type}
Area: {prop.floor_area_sqm} sqm
Storey: {prop.storey_range}
Lease commenced: {prop.lease_commence_date}
Remaining lease: {prop.remaining_lease}
AI Valuation: SGD {prop.avm_valuation_sgd:,.2f} (as of {prop.avm_valuation_date})
"""
            
            if not self.client:
                return self._mock_property_response(question, property_detail)
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a real estate expert assistant. Answer questions about this property factually and helpfully."
                },
                {
                    "role": "user",
                    "content": f"{property_detail}\n\nUser question: {question}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=300,
                timeout=10,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.exception(f"Property question error: {e}")
            return f"Sorry, I couldn't answer that question. Error: {str(e)}"

    def _mock_response(self, message: str) -> str:
        """Return mock response when OpenAI is unavailable."""
        keywords = message.lower()
        
        if any(kw in keywords for kw in ["price", "valuation", "cost"]):
            return (
                "🏠 Our properties range from SGD 300k to SGD 600k based on AI valuation. "
                "Each price is calculated using a XGBoost model trained on 20+ years of HDB market data. "
                "You can see the full breakdown of how we arrived at each price on the property detail page."
            )
        elif any(kw in keywords for kw in ["buy", "purchase", "invest", "trade"]):
            return (
                "💰 To invest: (1) Link your XRPL wallet, (2) Complete KYC verification, "
                "(3) Authorize SGPROP trustline, (4) Browse properties, (5) Place buy order. "
                "Trades settle on XRPL in seconds. You can also sell your holdings anytime on the secondary market."
            )
        elif any(kw in keywords for kw in ["lease", "remaining", "60 years", "99 years"]):
            return (
                "🏛️ Most HDB flats have 99-year leases starting from the 1980s. "
                "Remaining lease affects price significantly—shorter leases = lower value. "
                "Our AI model factors in lease length and age of property."
            )
        elif any(kw in keywords for kw in ["trustline", "kyc", "verify", "wallet"]):
            return (
                "🔐 Trustlines: On XRPL, you must opt-in to hold SGPROP tokens. "
                "KYC: You need identity verification (2-5 min upload) to trade. "
                "Wallet: Link your XRPL address (self-custody or managed). All secure & encrypted."
            )
        else:
            return (
                "👋 Hi! I'm here to help with questions about EstateX. "
                "Ask me about: property valuations, how to invest, lease terms, trustlines, or market trends. "
                "💡 For detailed price reasoning, check the 'Why This Price?' breakdown on any property page."
            )

    def _mock_property_response(self, question: str, property_detail: str) -> str:
        """Return mock property response when OpenAI is unavailable."""
        keywords = question.lower()
        if any(kw in keywords for kw in ["price", "worth", "valuation"]):
            return "Based on the valuation shown, this property's price reflects its size, location, and remaining lease term. Check the explainability breakdown to see exactly which factors drove the AI's valuation."
        elif any(kw in keywords for kw in ["lease", "age"]):
            return "The lease term is critical for pricing. Longer remaining lease = higher value. Our AI model penalizes properties with short lease terms."
        else:
            return f"Here's the property info: {property_detail}\n\nFeel free to ask specific questions about it!"

    def get_trading_recommendations(self, budget_sgd: float, risk_profile: str = "medium", limit: int = 5) -> list:
        """
        Get property recommendations based on budget and risk profile.
        
        Args:
            budget_sgd: Budget in SGD
            risk_profile: 'low' (premium/safe), 'medium' (balanced), 'high' (value/growth)
            limit: Number of recommendations
            
        Returns:
            List of recommended properties with buy buttons
        """
        try:
            from backend.db.models import Property
            
            # Query all available properties
            all_props = self.db.query(Property).all()
            
            if not all_props:
                return []
            
            # Filter by budget
            candidates = [
                p for p in all_props 
                if p.avm_valuation_sgd and p.avm_valuation_sgd <= budget_sgd
            ]
            
            if not candidates:
                # If no properties within budget, suggest cheapest
                candidates = sorted(all_props, key=lambda p: p.avm_valuation_sgd or float('inf'))[:limit]
            
            # Rank by risk profile
            if risk_profile == "low":
                # Prefer longer remaining lease, lower risk
                candidates.sort(key=lambda p: (
                    -(p.remaining_lease or 0),  # Higher lease remaining = safer
                    p.avm_valuation_sgd or float('inf')  # Lower price = safer
                ), reverse=False)
            elif risk_profile == "high":
                # Prefer growth potential (newer builds, good location)
                candidates.sort(key=lambda p: (
                    p.avm_valuation_sgd or float('inf'),  # Cheaper = more upside
                    -(p.lease_commence_date.year if p.lease_commence_date else 0)  # Newer = better
                ), reverse=False)
            else:  # medium
                # Balanced: good value in prime locations
                candidates.sort(key=lambda p: (
                    p.avm_valuation_sgd or float('inf') if p.avm_valuation_sgd and p.avm_valuation_sgd <= budget_sgd else float('inf'),
                    p.town  # Alphabetical for consistency
                ), reverse=False)
            
            # Build recommendation objects
            recommendations = []
            for prop in candidates[:limit]:
                rec = {
                    "property_id": str(prop.id),
                    "block": prop.block,
                    "street": prop.street_name,
                    "town": prop.town,
                    "flat_type": prop.flat_type,
                    "area_sqm": prop.floor_area_sqm,
                    "price_sgd": round(prop.avm_valuation_sgd, 2) if prop.avm_valuation_sgd else None,
                    "remaining_lease": prop.remaining_lease,
                    "reason": self._get_recommendation_reason(prop, budget_sgd, risk_profile),
                    "buy_url": f"/trades/create?property_id={prop.id}&price={prop.avm_valuation_sgd}"
                }
                recommendations.append(rec)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    def _get_recommendation_reason(self, prop, budget_sgd: float, risk_profile: str) -> str:
        """Generate human-readable reason for recommendation."""
        reasons = []
        
        if prop.avm_valuation_sgd and prop.avm_valuation_sgd <= budget_sgd * 0.7:
            reasons.append("✓ Great value within budget")
        
        if prop.remaining_lease and prop.remaining_lease >= "60 years":
            reasons.append("✓ Strong remaining lease")
        elif risk_profile == "low" and prop.remaining_lease and prop.remaining_lease >= "50 years":
            reasons.append("✓ Acceptable lease term")
        
        if risk_profile == "high" and prop.avm_valuation_sgd and prop.avm_valuation_sgd <= budget_sgd * 0.5:
            reasons.append("✓ Strong upside potential")
        
        # Location popularity heuristic
        prime_towns = {"MARINE PARADE", "BUKIT MERAH", "CLEMENTI", "ANG MO KIO", "BEDOK"}
        if prop.town in prime_towns:
            reasons.append(f"✓ Prime location ({prop.town})")
        
        return "; ".join(reasons) if reasons else "Matches your criteria"
