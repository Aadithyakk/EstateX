# scripts/inspect_bundle.py
import os, joblib, json
p = "xgb_hdb_bundle.joblib"
print("exists:", os.path.exists(p))
try:
    raw = joblib.load(p)
    print("type:", type(raw))
    if isinstance(raw, dict):
        print("dict keys:", list(raw.keys()))
    else:
        # heuristics
        try:
            from sklearn.pipeline import Pipeline
            print("has predict:", hasattr(raw, "predict"))
            print("has transform:", hasattr(raw, "transform"))
            if isinstance(raw, Pipeline):
                print("Pipeline named_steps:", list(raw.named_steps.keys()))
        except Exception as e:
            print("sklearn introspect error:", e)
        # try attr keys
        try:
            print("repr (head):", repr(raw)[:400])
            if hasattr(raw, "__dict__"):
                print("__dict__ keys:", list(raw.__dict__.keys()))
        except Exception as e:
            print("repr/error:", e)
except Exception as e:
    print("load error:", repr(e))