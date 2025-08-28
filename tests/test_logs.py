from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_logs_capture_upload_and_preview(tmp_path):
    c = TestClient(app)

    # Upload de 2 fichiers
    files = [
        ("files", ("u1.txt", b"a", "text/plain")),
        ("files", ("u2.txt", b"b", "text/plain")),
    ]
    r = c.post("/upload", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert body.get("count", 0) >= 2

    # Preview d'un fichier
    p = c.get("/preview/u1.txt")
    assert p.status_code == 200

    # Récupérer les logs
    lg = c.get("/logs")
    assert lg.status_code == 200
    events = lg.json()
    kinds = [e.get("event") for e in events]
    assert "upload" in kinds
    assert "preview" in kinds
