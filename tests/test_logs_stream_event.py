from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_sse_respects_event(monkeypatch):
    c = TestClient(app)
    with c.stream("GET", "/logs/stream?since_ts=0&limit=1&event=preview") as resp:
        assert resp.status_code == 200
        for line in resp.iter_lines():
            if line and line.startswith("data:"):
                import json
                payload = json.loads(line[len("data:"):].strip())
                if isinstance(payload, dict):
                    assert payload.get("event") == "preview"
                break
