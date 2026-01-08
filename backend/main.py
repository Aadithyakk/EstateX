from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from pydantic import BaseModel
from .config import Settings, get_settings
from .db.session import engine, Base, get_db_session
from .api.routes import health as health_route
from .api.routes import avm as avm_route
from .api.routes import properties as properties_route
from .api.routes import offerings as offerings_route
from .api.routes import xrpl_ops as xrpl_ops_route
from .api.routes import xrpl as xrpl_ledger_route
from .api.routes import trades as trades_route
from .api.routes import auth as auth_route
from .api.routes import quotes as quotes_route
from .api.routes import admin as admin_route
from .api.routes import chatbot as chatbot_route
from .services.avm import AVMService
import joblib
import os

app = FastAPI(title="XRPL RWA Liquidity MVP (SGPROP Tokens)")

# CORS - allow future frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Load DB metadata
    Base.metadata.create_all(bind=engine)

    # Load settings
    settings = get_settings()

    # Load AVM model bundle into app.state
    model_path = os.path.join(os.getcwd(), "xgb_hdb_bundle.joblib")
    if os.path.exists(model_path):
        try:
            raw = joblib.load(model_path)
            # normalize bundle into dict with keys: preprocessor, model, feature_columns, metadata
            # also preserve numeric_cols and categorical_cols if present
            bundle = {"preprocessor": None, "model": None, "feature_columns": [], "metadata": {}, "numeric_cols": [], "categorical_cols": []}
            if isinstance(raw, dict):
                # common layout: {'preprocessor':..., 'model':..., 'feature_columns':..., 'metadata':...}
                # preserve all keys from raw, then update with normalized defaults
                bundle.update(raw)
                # ensure critical keys exist
                if 'preprocessor' not in bundle:
                    bundle['preprocessor'] = None
                if 'model' not in bundle:
                    bundle['model'] = None
                if 'feature_columns' not in bundle:
                    bundle['feature_columns'] = []
                if 'metadata' not in bundle:
                    bundle['metadata'] = {}
                # also allow model under 'estimator' or 'model'
                if bundle['model'] is None and raw.get('estimator') is not None:
                    bundle['model'] = raw.get('estimator')
            else:
                # could be a sklearn Pipeline or tuple
                try:
                    from sklearn.pipeline import Pipeline
                    if isinstance(raw, Pipeline):
                        # assume last step is model and a step named 'preprocessor' may exist
                        steps = raw.named_steps
                        bundle['model'] = raw
                        if 'preprocessor' in steps:
                            bundle['preprocessor'] = steps['preprocessor']
                    elif isinstance(raw, (list, tuple)) and len(raw) >= 2:
                        # (preprocessor, model, feature_columns?)
                        bundle['preprocessor'] = raw[0]
                        bundle['model'] = raw[1]
                        if len(raw) > 2:
                            bundle['feature_columns'] = raw[2]
                    else:
                        # fallback: if raw has predict and transform methods, treat as model
                        if hasattr(raw, 'predict'):
                            bundle['model'] = raw
                except Exception:
                    # best-effort fallback
                    if hasattr(raw, 'predict'):
                        bundle['model'] = raw

            # if we have a preprocessor and model, store bundle; otherwise mark as unavailable
            if bundle.get('model') is not None:
                app.state.avm_bundle = bundle
                app.state.avm_load_error = None
            else:
                app.state.avm_bundle = None
                app.state.avm_load_error = f"Could not normalize AVM bundle of type {type(raw)}"
        except Exception as e:
            app.state.avm_bundle = None
            app.state.avm_load_error = str(e)
    else:
        app.state.avm_bundle = None
        app.state.avm_load_error = "bundle file not found"


@app.get("/health")
def health():
    return {"status": "ok"}


# include routers
app.include_router(health_route.router)
app.include_router(avm_route.router)
app.include_router(properties_route.router)
app.include_router(offerings_route.router)
app.include_router(xrpl_ops_route.router)
app.include_router(xrpl_ledger_route.router)
app.include_router(trades_route.router)
app.include_router(auth_route.router)
app.include_router(quotes_route.router)
app.include_router(admin_route.router)
app.include_router(chatbot_route.router)

