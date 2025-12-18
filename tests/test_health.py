from fastapi.testclient import TestClient
from ai_os.api import create_app

def test_health():
    app = create_app()
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
