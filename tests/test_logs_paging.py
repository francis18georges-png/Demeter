from fastapi.testclient import TestClient
from ia_skeleton.services.app.webui import app

def test_logs_paging_and_order(tmp_path):
    c = TestClient(app)

    files = [
        ("files", ("p690_a.txt", b"1", "text/plain")),
        ("files", ("p690_b.txt", b"2", "text/plain")),
        ("files", ("p690_c.txt", b"3", "text/plain")),
    ]
    r = c.post("/upload", files=files)
    assert r.status_code == 200
    assert c.get("/preview/p690_a.txt").status_code == 200
    assert c.get("/preview/p690_b.txt").status_code == 200

    r1 = c.get("/logs?limit=2")
    assert r1.status_code == 200
    ev1 = r1.json()
    assert len(ev1) == 2
    assert ev1[0]["ts"] >= ev1[1]["ts"]

    r2 = c.get("/logs?limit=2&offset=2")
    assert r2.status_code == 200
    ev2 = r2.json()
    if len(ev1) == 2 and len(ev2) == 2:
        ids1 = [(e["ts"], e.get("event")) for e in ev1]
        ids2 = [(e["ts"], e.get("event")) for e in ev2]
        assert not set(ids1) & set(ids2)

    r3 = c.get("/logs?limit=3&order=asc")
    assert r3.status_code == 200
    ev3 = r3.json()
    if len(ev3) >= 2:
        assert ev3[0]["ts"] <= ev3[1]["ts"]

    rp = c.get("/logs?event=preview&order=desc&limit=1")
    assert rp.status_code == 200
    evp = rp.json()
    assert all(e.get("event") == "preview" for e in evp)
