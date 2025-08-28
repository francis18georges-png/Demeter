import os
from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_logs_requires_token_when_set(monkeypatch):
    monkeypatch.setenv("DEMETER_TOKEN", "s3cr3t")
    c = TestClient(app)
    # sans token
    r = c.get("/logs?limit=1")
    assert r.status_code == 401
    # avec mauvais token
    r = c.get("/logs?limit=1", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401
    # avec bon token
    r = c.get("/logs?limit=1", headers={"Authorization": "Bearer s3cr3t"})
    assert r.status_code in (200, 204)

def test_no_token_env_allows_access(monkeypatch):
    monkeypatch.delenv("DEMETER_TOKEN", raising=False)
    c = TestClient(app)
    r = c.get("/logs?limit=1")
    assert r.status_code in (200, 204)
