from fastapi import APIRouter

router = APIRouter(prefix="/auth")


@router.post("/mock_login")
def mock_login(email: str):
    # dev-only fake token
    return {"access_token": f"fake-token-for-{email}", "token_type": "bearer"}
