# XRPL RWA Liquidity MVP

Run locally (development, dry-run XRPL):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt || pip install fastapi uvicorn sqlalchemy pydantic joblib scikit-learn xgboost xrpl
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Health:

```bash
curl http://localhost:8000/health
```

AVM predict (example):

```bash
curl -X POST http://localhost:8000/avm/predict -H 'Content-Type: application/json' -d '{"town":"ANG MO KIO","floor_area_sqm":100}'
```

Frontend (static)

The repository includes a minimal static frontend under `frontend/`. To serve it locally:

```bash
# from project root
python -m http.server 3000 --directory frontend
# then open http://localhost:3000 in your browser
```

The frontend assumes the API is reachable at `http://localhost:8000`. Adjust `BASE_URL` in `frontend/main.js` if needed.
# Eigenrestarea 



