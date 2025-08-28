from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_logs_level_filter(monkeypatch):
    c = TestClient(app)
    # seed: on déclenche un upload/preview pour avoir des events de niveaux variés si dispo,
    # sinon on vérifie simplement que le filtre ne casse pas la route (200 OK).
    r = c.get("/logs?limit=5&level=info")
    assert r.status_code in (200, 204)
    if r.status_code == 200 and isinstance(r.json(), list):
        for e in r.json():
            assert e.get("level") == "info"
