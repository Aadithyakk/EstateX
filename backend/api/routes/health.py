from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request):
    avm_loaded = getattr(request.app.state, 'avm_bundle', None) is not None
    avm_error = getattr(request.app.state, 'avm_load_error', None)
    return {"status": "ok", "avm_loaded": avm_loaded, "avm_load_error": avm_error}
