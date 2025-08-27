from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_index_ok():
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200

def test_router_chat():
    c = TestClient(app)
    r = c.post("/chat", data={"q":"importer un fichier csv"})
    assert r.status_code == 200
    assert "upload_file" in r.text
