from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_logs_params_limit_and_event(tmp_path):
    c = TestClient(app)

    # Génère quelques événements via l'app
    files = [
        ("files", ("a.txt", b"1", "text/plain")),
        ("files", ("b.txt", b"2", "text/plain")),
        ("files", ("c.txt", b"3", "text/plain")),
    ]
    r = c.post("/upload", files=files)
    assert r.status_code == 200
    p = c.get("/preview/a.txt")
    assert p.status_code == 200

    # 1) limit
    lg1 = c.get("/logs?limit=1")
    assert lg1.status_code == 200
    events1 = lg1.json()
    assert len(events1) == 1

    # 2) filter by event=upload
    lgu = c.get("/logs?event=upload&limit=1000")
    assert lgu.status_code == 200
    evu = lgu.json()
    assert len(evu) >= 1
    assert all(e.get("event") == "upload" for e in evu)

    # 3) chaque événement expose level (par défaut "info")
    assert all("level" in e for e in events1)
    assert all(e.get("level") in ("info","warning","error","debug","trace","critical") or e.get("level") == "info" for e in evu)
