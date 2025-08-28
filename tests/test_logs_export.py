from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app
import io, tarfile, json as _json

def test_logs_export_tar(tmp_path):
    c = TestClient(app)

    # Génère quelques events
    files = [
        ("files", ("p710_a.txt", b"1", "text/plain")),
        ("files", ("p710_b.txt", b"2", "text/plain")),
    ]
    r = c.post("/upload", files=files)
    assert r.status_code == 200
    assert c.get("/preview/p710_a.txt").status_code == 200

    # Appelle l'export
    resp = c.get("/logs/export")
    assert resp.status_code == 200
    # Contenu est bien un gzip/tar
    body = resp.content
    tf = tarfile.open(fileobj=io.BytesIO(body), mode="r:gz")

    names = tf.getnames()
    assert any(n.endswith("logs.jsonl") for n in names) or any(n.endswith("snapshot.jsonl") for n in names)

    # Au moins un enregistrement lisible dans l'un des deux
    picked = None
    for n in names:
        if n.endswith("logs.jsonl") or n.endswith("snapshot.jsonl"):
            picked = n
            break
    assert picked is not None

    f = tf.extractfile(picked)
    assert f is not None
    # lire au moins une ligne JSON valide
    line = f.readline().decode("utf-8").strip()
    assert line != ""
    obj = _json.loads(line)
    assert isinstance(obj, dict)
    assert "ts" in obj
    assert "event" in obj
