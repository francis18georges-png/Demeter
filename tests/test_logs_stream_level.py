from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_sse_respects_level(monkeypatch):
    # pas de token nécessaire si votre middleware protège déjà via env
    c = TestClient(app)
    with c.stream("GET", "/logs/stream?since_ts=0&limit=1&level=info") as resp:
        assert resp.status_code == 200
        got_info = False
        for line in resp.iter_lines():
            if line and line.startswith("data:"):
                import json
                payload = json.loads(line[len("data:"):].strip())
                # si on reçoit un event, il doit être level=info
                if isinstance(payload, dict):
                    assert payload.get("level") == "info"
                    got_info = True
                break
        # on ne force pas la présence d'un event (environnement de test variable)
        # mais si un event arrive, il doit correspondre au filtre
