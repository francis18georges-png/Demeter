from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app, INGEST, MANIFEST
from pathlib import Path

def test_index_ok():
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200

def test_multi_upload_manifest(tmp_path: Path):
    c = TestClient(app)
    files = [
        ("files", ("a.txt", b"hello", "text/plain")),
        ("files", ("b.txt", b"world", "text/plain")),
    ]
    r = c.post("/upload", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["count"] == 2
    assert (INGEST / "a.txt").exists() and (INGEST / "b.txt").exists()
    assert MANIFEST.exists()
