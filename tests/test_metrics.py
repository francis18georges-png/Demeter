from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_healthz_ok():
    c = TestClient(app)
    r = c.get("/healthz")
    assert r.status_code == 200
    assert r.text.strip() == "ok"

def test_metrics_and_counter_increment():
    c = TestClient(app)

    # métriques avant
    m0 = c.get("/metrics")
    assert m0.status_code == 200
    text0 = m0.text
    # on accepte "uploads_total" absent au tout début

    # faire 2 uploads
    files = [
        ("files", ("x.txt", b"x", "text/plain")),
        ("files", ("y.txt", b"y", "text/plain")),
    ]
    r = c.post("/upload", files=files)
    assert r.status_code == 200

    # métriques après
    m1 = c.get("/metrics")
    assert m1.status_code == 200
    text1 = m1.text
    assert "uploads_total" in text1
    # valeur >= 2 (peut être >2 si d'autres tests ont déjà incrémenté)
    # on vérifie juste la présence d’une ligne de compteur avec un total non négatif
    lines = [ln for ln in text1.splitlines() if ln.startswith("uploads_total ")]
    assert lines, "uploads_total gauge line not found"
    val = float(lines[0].split()[-1])
    assert val >= 2.0
