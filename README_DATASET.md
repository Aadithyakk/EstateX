# **EstateX: AI-powered, valuation-anchored real estate tokenization & settlement on the XRP Ledger (XRPL)**


A sophisticated FastAPI-based Real-World Assets (RWA) liquidity platform featuring AI-powered property valuation, explainability, and XRPL blockchain integration. Predict Singapore HDB flat prices with XGBoost, understand predictions via SHAP explanations, chat with an AI assistant, and trade property-backed tokens on the XRP Ledger.


## 🎯 Overview

**Eigenrestarea** is a production-ready MVP that demonstrates:

- **AI Valuation Model (AVM)** — XGBoost-based property price prediction for Singapore HDB flats
- **Explainability (SHAP)** — Understand exactly which factors drive property valuations
- **RAG Chatbot** — 24/7 AI assistant powered by OpenAI with market context
- **XRPL Integration** — Issue and trade property-backed tokens on the XRP Ledger
- **KYC & Compliance** — User authentication, KYC verification, and wallet management
- **Market Intelligence** — Real-time property analytics and trading data


**AI MODEL TRAINING** - was performed in housing_price_prediction.ipynb, producing the joblib and state.db, csv dataset used is in ResaleFlatPrices.zip and was obtained from https://data.gov.sg/datasets?agencies=Housing+%26+Development+Board+(HDB)&resultId=189


## ⚡ Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- `pip` and `venv`
- `.env` file with optional keys (see [Configuration](#configuration))

### 1. Setup Backend

```bash
# Clone and enter repo
git clone <repo>
cd "Eigenrestarea 2"

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start API Server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Server running at `http://localhost:8000`

### 3. Start Frontend (New Terminal)

```bash
cd frontend
python -m http.server 3000
# On macOS: open http://localhost:3000
```

### 4. Test Health

```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

## 📋 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# XRPL Configuration
XRPL_RPC_URL=https://s.altnet.rippletest.net:51234/
XRPL_WS_URL=wss://s.altnet.rippletest.net:51233/
XRPL_DRY_RUN=true  # Set to false for real transactions

# Wallets & Issuer (for trading features)
ISSUER_SEED=                    # Leave empty for dry-run
OPERATOR_SEED=                  # Leave empty for dry-run
STABLECOIN_ISSUER=              # Leave empty for dry-run

# Database
DB_URL=sqlite:///./dev.db      # or postgresql://user:password@localhost/dbname

# AI Features
OPENAI_API_KEY=                 # Leave empty for mock chatbot responses
ENV=dev                         # or 'prod'
```

**Note:** Chatbot and OpenAI features gracefully degrade if `OPENAI_API_KEY` is not set.

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (HTML/JS)                │
│            http://localhost:3000                     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼ REST API
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend                         │
│     http://localhost:8000 (with auto-reload)        │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ Core Services                              │    │
│  │ • AVM (XGBoost prediction + SHAP)          │    │
│  │ • Chatbot (OpenAI RAG)                     │    │
│  │ • XRPL Integration (Token trading)         │    │
│  │ • Auth & KYC                               │    │
│  └────────────────────────────────────────────┘    │
└────────┬──────────────┬──────────────┬──────────────┘
         │              │              │
    ┌────▼──┐    ┌─────▼──┐     ┌────▼──────┐
    │  DB   │    │ OpenAI │     │ XRPL      │
    │SQLite │    │  API   │     │ Testnet   │
    └───────┘    └────────┘     └───────────┘
```

### Four Core Subsystems

#### 1. **AVM (Automated Valuation Model)**
- **Routes:** `/avm/predict`, `/avm/batch_predict`, `/avm/predict-with-explanation`
- **Model:** XGBoost trained on 20+ years of Singapore HDB data
- **Features:** Town, flat type, area, storey, lease term, transaction date
- **Output:** Price prediction with confidence intervals
- **Location:** `backend/services/avm.py`, `backend/api/routes/avm.py`

#### 2. **SHAP Explainability**
- **What:** Understand prediction drivers via SHapley Additive exPlanations
- **Output:** Feature contributions showing which factors increase/decrease price
- **Integration:** Automatic in AVM predictions
- **Location:** `backend/services/avm.py` (`_init_shap_explainer()`, `get_explanation()`)

#### 3. **RAG Chatbot**
- **Routes:** `/chatbot/ask`, `/chatbot/recommendations`
- **Data Source:** Property database (market stats, valuations)
- **LLM:** OpenAI GPT-3.5-turbo (configurable)
- **Fallback:** Template responses if OpenAI unavailable
- **Location:** `backend/services/chatbot.py`, `backend/api/routes/chatbot.py`

#### 4. **XRPL Integration**
- **Routes:** `/xrpl/info`, `/xrpl/tx/submit`, `/xrpl/trustline/create`, `/trades`, `/offerings`
- **Features:** Token issuance, trading, trustline management
- **Dry-Run Mode:** Default ON (no real transactions); set `XRPL_DRY_RUN=false` for live
- **Location:** `backend/services/xrpl.py`, `backend/api/routes/xrpl*.py`, `backend/api/routes/trades.py`

## 📚 API Endpoints

### AVM Prediction

**POST** `/avm/predict`

```bash
curl -X POST http://localhost:8000/avm/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "town": "ANG MO KIO",
    "flat_type": "4 ROOM",
    "floor_area_sqm": 90,
    "storey_range": "10 TO 12",
    "lease_commence_date": "1985-01-01",
    "txn_date": "2024-01-01"
  }'
```

**Response:**
```json
{
  "predicted_price": 525471.10,
  "confidence_lower": 483433.42,
  "confidence_upper": 567508.79,
  "shap_base_value": 13.11,
  "shap_values": [0.0638, -0.0245, ...],
  "features_used": ["town", "storey_mid", "floor_area_sqm", ...]
}
```

### Chatbot

**POST** `/chatbot/ask`

```bash
curl -X POST http://localhost:8000/chatbot/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "What is the average property price in Ang Mo Kio?",
    "user_id": "user123"
  }'
```

**Response:**
```json
{
  "response": "Based on our market data, the average HDB price in Ang Mo Kio is approximately SGD 450,000...",
  "sources": ["market_stats", "property_database"]
}
```

### XRPL Operations

**GET** `/xrpl/info`
```bash
curl http://localhost:8000/xrpl/info
```

**POST** `/xrpl/tx/submit`
```bash
curl -X POST http://localhost:8000/xrpl/tx/submit \
  -H 'Content-Type: application/json' \
  -d '{"tx_type":"TrustSet","destination":"rN7n7otQDd6FczFgLdlqtyMVrn3R5eD...","limit":"1000000"}'
```

**POST** `/trades` — Create a trade order
**POST** `/offerings` — Create a new property offering

See [full endpoint documentation](QUICK_START.md) for examples.

## 🚀 Key Features

### 1. AI-Powered Price Prediction
- Real-time XGBoost valuation of Singapore HDB properties
- Automatic feature engineering from user inputs
- Confidence intervals for uncertainty quantification
- Batch prediction support for large datasets

### 2. Explainability with SHAP
- **Why This Price?** section on property detail pages
- Feature contribution breakdown (top 10 drivers)
- Visual bar chart showing feature impact
- Base value + individual contributions = predicted price

### 3. 24/7 Chatbot Assistant
- Answer questions about properties, market trends, pricing, and trading
- Context-aware responses using database data (RAG)
- Graceful fallback if OpenAI unavailable
- Sample conversations in [QUICK_START.md](QUICK_START.md)

### 4. XRPL Token Trading
- Issue property-backed SGPROP tokens on XRP Ledger
- Create trustlines for whitelisting
- Execute buy/sell trades with settlement tracking
- Dry-run mode for safe testing

### 5. KYC & Compliance
- User authentication and role-based access
- KYC verification workflows
- Wallet management (custody types)
- Compliance-ready audit trail

## 🗄️ Database Models

### User & Authentication
- `User` — Email, role (admin/user), created_at
- `KYCStatus` — User ID, verification status, provider reference
- `Wallet` — User wallet address, custody type

### Properties & Valuations
- `Property` — HDB attributes (town, block, flat type, lease, area)
- `Valuation` — Predicted price, SHAP features/explanation JSON, timestamp
- `Offering` — Property token offering (total supply, status, created_at)
- `Trade` — Buy/sell orders with settlement status

Default DB: SQLite (`dev.db`). Switch to PostgreSQL by setting `DB_URL`.

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_health.py -v

# Run with coverage
pytest --cov=backend tests/
```

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/health

# Batch AVM prediction
curl -X POST http://localhost:8000/avm/batch_predict \
  -H 'Content-Type: application/json' \
  -d '[{"town":"TAMPINES","flat_type":"5 ROOM","floor_area_sqm":120},...]'

# Admin: reload AVM model at runtime
curl -X POST http://localhost:8000/admin/reload_avm
```

## 📂 Project Structure

```
Eigenrestarea/
├── backend/                    # FastAPI application
│   ├── main.py                # App initialization, startup hooks
│   ├── config.py              # Environment configuration
│   ├── db/
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   └── session.py         # Database session factory
│   ├── api/
│   │   └── routes/            # HTTP endpoint handlers
│   │       ├── avm.py         # /avm/* endpoints
│   │       ├── chatbot.py     # /chatbot/* endpoints
│   │       ├── xrpl.py        # /xrpl/* endpoints
│   │       ├── trades.py      # /trades endpoints
│   │       ├── auth.py        # /auth endpoints
│   │       └── ...
│   ├── services/              # Business logic layer
│   │   ├── avm.py             # Prediction, featurization, SHAP
│   │   ├── chatbot.py         # RAG context retrieval, OpenAI calls
│   │   ├── xrpl.py            # XRPL client interactions
│   │   └── pricing.py         # Pricing models
│   ├── schemas/               # Pydantic request/response models
│   │   ├── avm.py
│   │   ├── trades.py
│   │   └── ...
│   └── utils/
│       └── parsing.py         # Feature parsing utilities
├── frontend/                  # Static HTML/JS/CSS
│   ├── index.html            # Main page
│   ├── app.js                # Frontend logic & XRPL integration
│   ├── main.js               # API client, BASE_URL config
│   └── styles.css            # Styling
├── tests/                     # Pytest test suite
│   ├── test_health.py
│   ├── test_properties.py
│   └── ...
├── scripts/                   # Utility scripts
│   └── inspect_bundle.py     # Analyze ML model bundle
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker setup (optional)
├── .env.example              # Environment template
└── xgb_hdb_bundle.joblib    # Pre-trained XGBoost model
```

## 🔧 Development Workflow

### Adding a New Endpoint

1. **Define schema** in `backend/schemas/`
   ```python
   from pydantic import BaseModel
   class MyRequest(BaseModel):
       field: str
   class MyResponse(BaseModel):
       result: str
   ```

2. **Add service logic** in `backend/services/`
   ```python
   class MyService:
       def process(self, request: MyRequest) -> MyResponse:
           # Business logic here
           return MyResponse(result="...")
   ```

3. **Create route** in `backend/api/routes/`
   ```python
   from fastapi import APIRouter
   router = APIRouter(prefix="/myfeature", tags=["myfeature"])
   
   @router.post("/endpoint", response_model=MyResponse)
   def my_endpoint(payload: MyRequest):
       svc = MyService()
       return svc.process(payload)
   ```

4. **Register router** in `backend/main.py`
   ```python
   from .api.routes import myfeature
   app.include_router(myfeature.router)
   ```

5. **Test locally**
   ```bash
   curl -X POST http://localhost:8000/myfeature/endpoint
   ```

### Reloading the ML Model at Runtime

The AVM bundle (XGBoost + SHAP explainer) can be reloaded without restarting:

```bash
curl -X POST http://localhost:8000/admin/reload_avm
```

Replace `xgb_hdb_bundle.joblib` in the project root, then call the endpoint to load the new model.

## 🔐 Security & Guardrails

- **Dry-run by default**: XRPL transactions are disabled unless `XRPL_DRY_RUN=false`
- **No side-effects at import time**: All wallet creation and transaction submission happen inside route handlers
- **Graceful fallback**: OpenAI and SHAP features are optional; the system works without them
- **Error handling**: All routes return structured `HTTPException` responses
- **Logging**: Detailed logs for debugging; sensitive info is masked

## 📖 Learn More

- **[QUICK_START.md](QUICK_START.md)** — Step-by-step tutorial with UI screenshots
- **[FEATURE_IMPLEMENTATION.md](FEATURE_IMPLEMENTATION.md)** — Technical details on SHAP and Chatbot
- **[XRPL_INTEGRATION.md](XRPL_INTEGRATION.md)** — Blockchain features and transaction flows
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — AI coding agent guidelines

## 🛠️ Troubleshooting

### Port 8000 Already in Use
```bash
# Kill existing process
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use a different port
uvicorn backend.main:app --port 8001
```

### SHAP Import Error
```bash
pip install shap>=0.43.0
```

### OpenAI API Key Error
Leave `OPENAI_API_KEY` empty to disable chatbot (will use mock responses).

### Database Locked (SQLite)
Delete `dev.db` and restart:
```bash
rm dev.db
uvicorn backend.main:app --reload
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `sqlalchemy` | ORM |
| `pydantic` | Data validation |
| `xgboost` | ML model |
| `scikit-learn` | Feature preprocessing |
| `shap` | Model explainability |
| `openai` | Chatbot API |
| `xrpl-py` | XRPL client |
| `joblib` | Model serialization |
| `pandas` | Data manipulation |

## 🚢 Deployment

### Docker

```bash
docker-compose up --build
# API available at http://localhost:8000
```

### Manual (Production)

```bash
# Use gunicorn for production
pip install gunicorn
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 📝 License

[See LICENSE](LICENSE)

## 💬 Support

For questions or issues, refer to:
- [VISUAL_GUIDE_FOR_JUDGES.md](VISUAL_GUIDE_FOR_JUDGES.md) — UI walkthrough
- [TESTING_XRPL_FEATURES.md](TESTING_XRPL_FEATURES.md) — Blockchain testing guide
- [XRP_ROLE_EXPLAINED.md](XRP_ROLE_EXPLAINED.md) — XRP tokenomics explanation



