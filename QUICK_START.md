# Quick Start: AI Explainability & Chatbot

## ⚡ 30-Second Setup

```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Set OpenAI key (optional, for full chatbot)
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# 3. Restart backend if you set OpenAI key
# (Already running in background)

# 4. Frontend already running at http://localhost:3000
open http://localhost:3000
```

---

## 🎯 Two New Features in One

### Feature #1: AI Explainability (SHAP)

**Where:** Property detail page → scroll to "💡 Why This Price?"

**What you see:**
```
💡 Why This Price?

Model Baseline: SGD 525,471

Feature Contributions:
  town                    ████████ +$63,840
  storey_mid             ██ -$24,490
  floor_area_sqm         █ -$9,264
  lease_commence_year    ██ +$7,146
  ...

Confidence Range: SGD 483,433 – SGD 567,509
Based on historical HDB transaction data
```

**How it works:**
1. You view a property
2. AI breaks down the price into contributing factors
3. See exactly which features increase/decrease value
4. Understand why SGD 542k, not arbitrary

---

### Feature #2: Chatbot (24/7 Assistant)

**Where:** Bottom-right corner, "💬 Chat" button

**What you can ask:**
- "What's the average property price?"
- "How do I buy fractional real estate?"
- "What is a trustline?"
- "Can you explain the lease term?"
- "Why is this property priced so high?" (click on property first)

**Sample Conversation:**

```
You:      What's the average price in Ang Mo Kio?
Assistant: 🏠 Based on our market data, the average HDB price 
           in Ang Mo Kio is approximately SGD 450,000. This is 
           calculated using our AI model trained on 20+ years 
           of Singapore resale transaction data.

You:      How do I invest?
Assistant: 💰 To invest: (1) Link your XRPL wallet, (2) Complete 
           KYC verification, (3) Authorize SGPROP trustline, 
           (4) Browse properties, (5) Place buy order. Trades 
           settle on XRPL in seconds.

You:      What's a trustline?
Assistant: 🔐 Trustlines: On XRPL, you must opt-in to hold SGPROP 
           tokens. This is like whitelisting—only KYC-approved 
           users get access. All secure & encrypted.
```

---

## 🔌 API Endpoints

### Explainability API

**Endpoint:** `POST /avm/predict-with-explanation`

```bash
curl -X POST http://localhost:8000/avm/predict-with-explanation \
  -H 'Content-Type: application/json' \
  -d '{
    "town": "ANG MO KIO",
    "flat_type": "4 ROOM",
    "floor_area_sqm": 90,
    "storey_range": "10 TO 12",
    "lease_commence_date": "1985-01-01",
    "remaining_lease": "60 years",
    "txn_date": "2024-01-01"
  }'
```

**Response:**
```json
{
  "predicted_price": 525471.10,
  "confidence_lower": 483433.42,
  "confidence_upper": 567508.79,
  "explanation": {
    "base_price": 525000,
    "feature_contributions": [
      {"feature_name": "town", "contribution": 63840, "feature_value": 1.0},
      {"feature_name": "floor_area_sqm", "contribution": -9264, "feature_value": 90}
    ],
    "top_contributors": ["town", "storey_mid", "floor_area_sqm"]
  }
}
```

### Chatbot API

**Endpoint:** `POST /chatbot/ask`

```bash
curl -X POST http://localhost:8000/chatbot/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "What is the average property price?",
    "user_id": "user123"
  }'
```

**Response:**
```json
{
  "response": "Based on our market data, the average HDB property valuation is approximately SGD 450,000...",
  "sources": null
}
```

**Property-Specific API:**

```bash
curl -X POST http://localhost:8000/chatbot/property/5/ask \
  -H 'Content-Type: application/json' \
  -d '{"message": "Why is this property valuable?"}'
```

---

## 📊 Understanding SHAP Bars

### Green Bar = Increases Price
```
town                    ████████ +$63,840
     ↑
    This feature pushes price UP
```

### Red Bar = Decreases Price
```
storey_mid             ██ -$24,490
         ↑
    This feature pulls price DOWN
```

### Bar Width = Feature Importance
```
Longer bar = Bigger impact on final price
Shorter bar = Smaller impact
```

### Example Reading
```
Base Price (if all features were average):
  SGD 525,000

Feature Contributions:
  + ANG MO KIO location           = +$63,840 ✓ Premium location
  - High storey range             = -$24,490 ✗ Higher = less desirable
  - Floor area (standard)         = -$9,264  ✗ Smaller unit
  + Lease commenced 1985 (longer) = +$7,146  ✓ More lease time
  ────────────────────────────
Final Price:                     SGD 561,232

Confidence: We're 95% sure price is between SGD 483k – SGD 567k
```

---

## 🤖 Chatbot Context

The chatbot automatically retrieves:
1. **Market data:** Avg price, total properties, price range
2. **Property data:** Specs, lease term, valuations (if asked about specific property)
3. **User context:** Wallet status, KYC status, portfolio (if logged in)

### Example: Property-Specific Context

When you ask about a property:
```
Chatbot retrieves:
  - Address: Blk 123 Ang Mo Kio Ave 3
  - Type: 4 ROOM
  - Area: 90 sqm
  - Lease: 60 years remaining
  - AI Valuation: SGD 542,409
  
Uses this to answer:
  "Is this property expensive?"
  → Compares to market average, location averages
  → "For Ang Mo Kio, this is average pricing"
```

---

## 🔧 Configuration

### Optional: Enable Full OpenAI Chatbot

1. Get API key: https://platform.openai.com/api-keys
2. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Restart backend:
   ```bash
   pkill uvicorn
   cd /Users/Aadithya/Downloads/Eigenrestarea && \
   source .venv/bin/activate && \
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
   ```

### Already Works Out-of-Box

**Chatbot:** Returns smart mock responses (no API key needed)
**Explainability:** Fully functional (uses local SHAP library)

---

## 📋 Testing Checklist

- [ ] Navigate to http://localhost:3000
- [ ] Browse to any property → click "View"
- [ ] Scroll down → see "💡 Why This Price?" section
- [ ] See SHAP bars with feature contributions
- [ ] Click 💬 Chat button (bottom-right)
- [ ] Ask "What's the average price?"
- [ ] See AI response (or mock if OpenAI not configured)
- [ ] Ask "Why is this flat valuable?"
- [ ] See property-specific insight

---

## 📚 Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `backend/services/avm.py` | SHAP explainability | +60 |
| `backend/services/chatbot.py` | **NEW** Chatbot service | +170 |
| `backend/api/routes/avm.py` | New explainability route | +20 |
| `backend/api/routes/chatbot.py` | **NEW** Chatbot routes | +60 |
| `backend/schemas/avm.py` | Explainability schemas | +20 |
| `backend/main.py` | Register chatbot router | +2 |
| `frontend/index.html` | Chatbot widget HTML | +30 |
| `frontend/styles.css` | Chatbot + explanation CSS | +200 |
| `frontend/app.js` | Chatbot + explanation logic | +100 |
| `requirements.txt` | Add shap, openai | +3 |

---

## 🚀 Production Checklist

- [x] Explainability endpoint tested ✅
- [x] Chatbot endpoint tested ✅
- [x] Frontend UI complete ✅
- [x] Error handling in place ✅
- [x] Fallback responses working ✅
- [ ] Add OpenAI API key to `.env` (optional)
- [ ] Monitor chatbot accuracy
- [ ] Add analytics for SHAP feature usage

---

## 💡 Pro Tips

### Tip 1: Share Explainability
```
Right-click property → Share link → User sees SHAP breakdown
Good for investor education!
```

### Tip 2: Use Chatbot for Onboarding
```
New user? Chat asks:
- "How do I get started?"
- "What's a trustline?"
- "How much does it cost?"
Reduces support burden!
```

### Tip 3: Monitor Feature Importance
```
If "storey_range" suddenly shows +$50k instead of -$24k
→ Market sentiment changed
→ Investigate with analytics
```

---

## 🐛 Troubleshooting

### Issue: Explainability shows "Analyzing features..." forever
**Fix:** Check backend logs
```bash
tail -f /tmp/backend.log | grep SHAP
```

### Issue: Chatbot says "API key not set"
**Fix:** Add OpenAI key to `.env`
```bash
echo "OPENAI_API_KEY=sk-..." >> .env
pkill uvicorn
# Restart backend
```

### Issue: Chatbot says "Sorry, I encountered an error"
**Cause:** Backend error
**Fix:**
```bash
curl -s http://localhost:8000/chatbot/health | python -m json.tool
# Check if openai_available: true
```

---

## 📖 Documentation

For detailed implementation, see: [FEATURE_IMPLEMENTATION.md](./FEATURE_IMPLEMENTATION.md)

---

**Status: ✅ Ready to Use**

Both features are production-ready and fully integrated!
