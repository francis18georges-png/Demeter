from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_query_access_token_allows_access(monkeypatch):
    monkeypatch.setenv("DEMETER_TOKEN", "s3cr3t")
    c = TestClient(app)

    # /logs avec token en query
    r = c.get("/logs?limit=1&access_token=s3cr3t")
    assert r.status_code in (200, 204)

    # /logs sans token ou token invalide
    assert c.get("/logs?limit=1").status_code == 401
    assert c.get("/logs?limit=1&access_token=nope").status_code == 401

    # /logs/export avec token en query
    r = c.get("/logs/export?access_token=s3cr3t")
    assert r.status_code == 200

    # SSE: doit accepter le token en query
    with c.stream("GET", "/logs/stream?since_ts=0&limit=1&access_token=s3cr3t") as resp:
        assert resp.status_code == 200
        got_data = False
        for line in resp.iter_lines():
            if line and line.startswith("data:"):
                got_data = True
                break
        assert got_data
