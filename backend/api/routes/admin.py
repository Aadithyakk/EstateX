from fastapi import APIRouter, Request, HTTPException
import os, joblib

router = APIRouter(prefix="/admin")


def _normalize_bundle(raw):
    bundle = {"preprocessor": None, "model": None, "feature_columns": [], "metadata": {}, "numeric_cols": [], "categorical_cols": []}
    if isinstance(raw, dict):
        # preserve all keys from raw, then ensure critical keys exist
        bundle.update(raw)
        if 'preprocessor' not in bundle:
            bundle['preprocessor'] = None
        if 'model' not in bundle:
            bundle['model'] = None
        if 'feature_columns' not in bundle:
            bundle['feature_columns'] = []
        if 'metadata' not in bundle:
            bundle['metadata'] = {}
        if bundle['model'] is None and raw.get('estimator') is not None:
            bundle['model'] = raw.get('estimator')
    else:
        try:
            from sklearn.pipeline import Pipeline
            if isinstance(raw, Pipeline):
                bundle['model'] = raw
                steps = raw.named_steps
                if 'preprocessor' in steps:
                    bundle['preprocessor'] = steps['preprocessor']
        except Exception:
            if hasattr(raw, 'predict'):
                bundle['model'] = raw
    return bundle


@router.post('/reload_avm')
def reload_avm(request: Request):
    model_path = os.path.join(os.getcwd(), 'xgb_hdb_bundle.joblib')
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail='bundle file not found')
    import traceback
    try:
        raw = joblib.load(model_path)
        bundle = _normalize_bundle(raw)
        if bundle.get('model') is None:
            err = f'Could not normalize bundle of type {type(raw)}'
            request.app.state.avm_bundle = None
            request.app.state.avm_load_error = err
            raise HTTPException(status_code=500, detail=err)
        request.app.state.avm_bundle = bundle
        request.app.state.avm_load_error = None
        return {"success": True}
    except Exception as e:
        tb = traceback.format_exc()
        request.app.state.avm_bundle = None
        request.app.state.avm_load_error = str(e)
        # return detailed traceback in response for dev debugging
        raise HTTPException(status_code=500, detail={"error": str(e), "trace": tb})
