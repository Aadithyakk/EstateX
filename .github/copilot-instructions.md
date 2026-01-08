## Purpose
Actionable guidance for AI coding agents working on Eigenrestarea—a FastAPI-based XRPL RWA (Real-World Assets) liquidity MVP with Singapore property (HDB flat) price prediction and token trading.

## Architecture Overview

**Core Stack:** FastAPI + SQLAlchemy + XGBoost AVM (Automated Valuation Model) + XRPL integration  
**Key Entry Point:** [backend/main.py](backend/main.py) — startup loads AVM bundle into `app.state.avm_bundle`

### Three Core Subsystems

1. **AVM (Automated Valuation Model)** — predict HDB flat prices
   - Route: [backend/api/routes/avm.py](backend/api/routes/avm.py) — `/avm/predict`, `/avm/batch_predict`
   - Service: [backend/services/avm.py](backend/services/avm.py) — featurization and prediction; handles variant field names (e.g., `lease_commence_date` → `lease_commence_year`)
   - Schema: [backend/schemas/avm.py](backend/schemas/avm.py) — `AVMPredictRequest`, `AVMPredictResponse`
   - Bundle loading: flexible deserialization in [backend/main.py](backend/main.py#L45-L85) (handles dict, Pipeline, tuple formats)
   - Admin reload: [backend/api/routes/admin.py](backend/api/routes/admin.py) — `POST /admin/reload_avm` for hot-reloading model at runtime

2. **User & KYC Management**
   - Models: [backend/db/models.py](backend/db/models.py) — `User` (email, role enum), `KYCStatus`, `Wallet` (custody types), `Property` (HDB attributes)
   - Routes: [backend/api/routes/auth.py](backend/api/routes/auth.py), [admin.py](backend/api/routes/admin.py)

3. **Trading & Offerings** — XRPL token issuance and trades
   - Routes: [backend/api/routes/trades.py](backend/api/routes/trades.py), [offerings.py](backend/api/routes/offerings.py), [xrpl_ops.py](backend/api/routes/xrpl_ops.py)
   - Config: [backend/config.py](backend/config.py) — `XRPL_RPC_URL`, `XRPL_WS_URL`, `ISSUER_SEED`, `DB_URL`, `XRPL_DRY_RUN` (all via `.env` or env vars)

## Developer Workflow

### Setup & Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # Or: fastapi uvicorn sqlalchemy pydantic joblib scikit-learn xgboost xrpl-py psycopg2-binary pandas
```

Start the API server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Serve static frontend (separate terminal):
```bash
cd frontend
python -m http.server 3000
# Open http://localhost:3000
```

### Quick Manual Tests

```bash
# Health check
curl http://localhost:8000/health

# AVM prediction
curl -X POST http://localhost:8000/avm/predict \
  -H 'Content-Type: application/json' \
  -d '{"town":"ANG MO KIO","flat_type":"4 ROOM","floor_area_sqm":90,"storey_range":"10 TO 12","lease_commence_date":"1985-01-01","txn_date":"2024-01-01"}'

# Reload AVM model at runtime
curl -X POST http://localhost:8000/admin/reload_avm
```

## Code Patterns & Conventions

### Route Structure (Clean Separation)
- Routes in [backend/api/routes/](backend/api/routes/) — handle HTTP concerns (validation, error codes)
- Services in [backend/services/](backend/services/) — core business logic, testable in isolation
- Schemas in [backend/schemas/](backend/schemas/) — Pydantic models for request/response validation
- **Pattern:** Route imports service, calls service method, raises `HTTPException` on error

Example: [backend/api/routes/avm.py](backend/api/routes/avm.py#L15-L24):
```python
@router.post("/predict", response_model=AVMPredictResponse)
def predict(payload: AVMPredictRequest, request: Request):
    bundle = request.app.state.avm_bundle
    if not bundle:
        raise HTTPException(status_code=500, detail="AVM model not available")
    svc = AVMService(bundle)
    # ... service call, error handling
```

### AVM Featurization (Field Mapping Resilience)
The featurization step in [backend/services/avm.py](backend/services/avm.py#L24-L68) derives new fields from raw inputs and normalizes them to match bundle feature columns:
- Parses `storey_range` (e.g., "10 TO 12") → `storey_mid` (float)
- Parses `remaining_lease` (e.g., "60 years") → `remaining_lease_years` (int)
- Derives `lease_commence_year`, `txn_year`, `txn_month`, `txn_quarter` from dates
- Maps variant field names (case-insensitive) to expected column names

**When adding new features:** ensure parsing logic is added to `parse_*` functions in [backend/utils/parsing.py](backend/utils/parsing.py) and featurization is updated.

### Model Bundle Format Flexibility
[backend/main.py](backend/main.py#L45-L85) and [backend/api/routes/admin.py](backend/api/routes/admin.py#L7-L26) accept multiple bundle serialization formats:
- **Dict**: `{"preprocessor": ..., "model": ..., "feature_columns": [...], "metadata": {...}}`
- **sklearn Pipeline**: auto-extracts `preprocessor` step and model
- **Tuple**: `(preprocessor, model, [feature_columns])`
- **Single estimator**: if `predict` method exists, treat as model directly

**Implication:** Bundle shape may vary; always check `bundle.get('model')` and `bundle.get('preprocessor')` before use.

### Database Session & Models
- Session factory: [backend/db/session.py](backend/db/session.py)
- Models: [backend/db/models.py](backend/db/models.py) (User, KYCStatus, Wallet, Property, ...)
- Default DB: SQLite (`dev.db`); can override with `DB_URL` env var (e.g., PostgreSQL via `psycopg2`)
- **Pattern in routes**: Inject `db_session: Session = Depends(get_db_session)` to access DB

### XRPL Configuration & DRY-RUN Mode
[backend/config.py](backend/config.py) provides:
- `XRPL_RPC_URL`, `XRPL_WS_URL` — defaults to rippletest.net altnet
- `XRPL_DRY_RUN` (default `True`) — when True, skip real on-chain transactions
- `ISSUER_SEED`, `OPERATOR_SEED`, `STABLECOIN_ISSUER` — expected as env vars; leave empty for dry-run

**Safe practice:** Always check `XRPL_DRY_RUN` before posting transactions; log which mode is active.

## When Adding or Modifying Routes

1. **Define schema** in [backend/schemas/](backend/schemas/) (Pydantic `BaseModel`)
2. **Add service method** in appropriate [backend/services/](backend/services/) file (business logic, DB queries)
3. **Create route** in [backend/api/routes/](backend/api/routes/) (HTTP handler, validation, error mapping)
4. **Include router** in [backend/main.py](backend/main.py#L104+) via `app.include_router()`
5. **Test endpoint** via curl or pytest

## Important Files (First-Read Priority)
- [backend/main.py](backend/main.py) — FastAPI app, startup hooks, router registration
- [backend/config.py](backend/config.py) — environment variables and settings
- [backend/services/avm.py](backend/services/avm.py) — core AVM logic and feature engineering
- [backend/db/models.py](backend/db/models.py) — SQLAlchemy schema
- [requirements.txt](requirements.txt) — all dependencies

## Common Tasks & Patterns

| Task | Where | Pattern |
|------|-------|---------|
| Add new prediction endpoint | `backend/api/routes/new_route.py`, `backend/services/new_service.py`, `backend/schemas/new_schema.py` | Follow AVM pattern: schema → service → route |
| Add new DB model | [backend/db/models.py](backend/db/models.py) | Inherit from `Base`; use `Column()`, relationships |
| Hot-reload ML model | POST `/admin/reload_avm` | Already implemented; use as template for other model endpoints |
| Change database | `.env` or env var `DB_URL` | Default SQLite; supports PostgreSQL, MySQL, etc. (update `psycopg2` requirement if needed) |
| Debug featurization | Add logging in [backend/services/avm.py](backend/services/avm.py#L35) | Print intermediate `features` dict before normalization |

## Safety & Guardrails

- **No side-effects at import time** — all Wallet creation, transaction submission must be inside route handlers or service methods
- **Dry-run by default** — `XRPL_DRY_RUN=True` in config; gate real transactions behind explicit user action
- **Error responses** — use `HTTPException(status_code=..., detail=...)` for consistent client error handling
- **Logging** — use `import logging; logger = logging.getLogger(__name__)` in routes/services; log exceptions at level `exception`

## Known Limitations & TODOs

- `backend/fair_pricing.py`, `backend/liquidity_model.py` — currently placeholders; implement pricing/liquidity logic as needed
- `xrpl_client.py`, `xrpl_client_testnet.py` — not currently used in routes; XRPL integration routed through [backend/services/xrpl.py](backend/services/xrpl.py) instead
- Frontend (`frontend/`) — minimal static HTML/JS; no build step; BASE_URL hardcoded in `main.js`
