from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_logs_event_filter(monkeypatch):
    c = TestClient(app)
    r = c.get("/logs?limit=10&event=preview")
    assert r.status_code in (200, 204)
    if r.status_code == 200:
        assert isinstance(r.json(), list)
        for e in r.json():
            assert e.get("event") == "preview"
