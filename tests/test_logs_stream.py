from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app
import json as _json

def test_logs_since_ts_and_stream(tmp_path):
    c = TestClient(app)

    # Génère des événements
    files = [
        ("files", ("p700_a.txt", b"1", "text/plain")),
        ("files", ("p700_b.txt", b"2", "text/plain")),
    ]
    r = c.post("/upload", files=files)
    assert r.status_code == 200
    assert c.get("/preview/p700_a.txt").status_code == 200

    # Snapshot du dernier ts
    lg = c.get("/logs?limit=1")
    assert lg.status_code == 200
    last = lg.json()
    assert len(last) == 1
    ts0 = int(last[0]["ts"])

    # since_ts -> aucun nouvel event pour l'instant
    r0 = c.get(f"/logs?since_ts={ts0}")
    assert r0.status_code == 200
    assert r0.json() == []

    # Provoque un nouvel event
    assert c.get("/preview/p700_b.txt").status_code == 200

    # since_ts -> maintenant on a au moins un event
    r1 = c.get(f"/logs?since_ts={ts0}")
    assert r1.status_code == 200
    newer = r1.json()
    assert len(newer) >= 1
    assert all(int(e["ts"]) > ts0 for e in newer)

    # SSE: on lit 1 event et on ferme (limit=1)
    with c.stream("GET", "/logs/stream?since_ts=0&limit=1") as resp:
        assert resp.status_code == 200
        got = None
        for line in resp.iter_lines():
            if not line:
                continue
            assert line.startswith("data:")
            payload = line.split("data:", 1)[1].strip()
            obj = _json.loads(payload)
            assert isinstance(obj, dict)
            assert "event" in obj
            got = obj
            break
        assert got is not None
