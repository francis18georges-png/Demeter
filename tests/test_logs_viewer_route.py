from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_logs_viewer_route():
    c = TestClient(app)
    r = c.get("/logs/viewer")
    assert r.status_code == 200
    assert b"Logs viewer" in r.content
