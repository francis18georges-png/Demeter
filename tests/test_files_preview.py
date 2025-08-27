from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app, INGEST
from pathlib import Path

def test_files_listing_and_preview(tmp_path: Path):
    # préparer 2 fichiers texte
    (INGEST / "note.txt").write_text("hello world", encoding="utf-8")
    (INGEST / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    # simuler manifest
    (INGEST / "manifest.jsonl").write_text("", encoding="utf-8")
    with (INGEST / "manifest.jsonl").open("a", encoding="utf-8") as w:
        w.write('{"ts":1,"filename":"note.txt","bytes":11,"mime":"text/plain","path":"%s"}\n' % str(INGEST / "note.txt"))
        w.write('{"ts":2,"filename":"data.csv","bytes":6,"mime":"text/csv","path":"%s"}\n' % str(INGEST / "data.csv"))

    c = TestClient(app)
    r = c.get("/files")
    assert r.status_code == 200
    assert "note.txt" in r.text and "data.csv" in r.text

    r2 = c.get("/preview", params={"name":"note.txt"})
    assert r2.status_code == 200
    assert "hello world" in r2.text
