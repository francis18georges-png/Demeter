from pathlib import Path
from fastapi.testclient import TestClient
import json

from ia_skeleton.services.app.webui import app, INGEST

def test_files_listing_and_preview(tmp_path: Path):
    # préparer 2 fichiers texte
    (INGEST / "note.txt").write_text("hello world", encoding="utf-8")
    (INGEST / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")

    # manifest JSON Lines valide
    rows = [
        {"ts": 1, "filename": "note.txt", "bytes": 11, "mime": "text/plain", "path": str(INGEST / "note.txt")},
        {"ts": 2, "filename": "data.csv", "bytes": 6, "mime": "text/csv", "path": str(INGEST / "data.csv")},
    ]
    (INGEST / "manifest.jsonl").write_text("", encoding="utf-8")
    with (INGEST / "manifest.jsonl").open("a", encoding="utf-8") as w:
        for r in rows:
            w.write(json.dumps(r, ensure_ascii=False) + "\n")

    c = TestClient(app)
    r = c.get("/files")
    assert r.status_code == 200
    assert "note.txt" in r.text and "data.csv" in r.text

    # preview note.txt
    rp = c.get("/preview/note.txt")
    assert rp.status_code == 200
    assert "hello world" in rp.text
