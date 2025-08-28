from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_header_overrides_query(monkeypatch):
    monkeypatch.setenv("DEMETER_TOKEN", "s3cr3t")
    c = TestClient(app)

    # Header faux + query correct => doit être rejeté (header prioritaire)
    r = c.get("/logs?limit=1&access_token=s3cr3t",
              headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401

    # Header correct + query faux => doit passer
    r = c.get("/logs?limit=1&access_token=nope",
              headers={"Authorization": "Bearer s3cr3t"})
    assert r.status_code in (200, 204)
