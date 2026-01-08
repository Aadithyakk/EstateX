from fastapi.testclient import TestClient
from backend.main import app


def test_create_and_get_property():
    client = TestClient(app)
    payload = {"town": "ANG MO KIO", "floor_area_sqm": 90}
    resp = client.post("/properties/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("id") is not None
    pid = data["id"]
    resp2 = client.get(f"/properties/{pid}")
    assert resp2.status_code == 200
    assert resp2.json().get("town") == "ANG MO KIO"
