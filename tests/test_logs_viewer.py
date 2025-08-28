from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_home_page_ok():
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200
    assert b"Logs viewer" in r.content
