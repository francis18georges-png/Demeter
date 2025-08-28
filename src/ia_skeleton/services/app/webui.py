from __future__ import annotations

import json
import time
import mimetypes
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

# --- Dossiers / manifest (exportés pour les tests) ---
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3] if (HERE.parts and "site-packages" in HERE.parts) else Path.cwd()
INGEST = (ROOT / "ingest" / "local")
INGEST.mkdir(parents=True, exist_ok=True)
MANIFEST = INGEST / "manifest.jsonl"
MANIFEST.touch(exist_ok=True)

app = FastAPI(title="Demeter WebUI")


# -------- Helpers --------
def _append_manifest(filename: str, byte_count: int, mime: str, path: Path) -> None:
    rec = {
        "ts": int(time.time()),
        "filename": filename,
        "bytes": byte_count,
        "mime": mime,
        "path": str(path),
    }
    with MANIFEST.open("a", encoding="utf-8") as w:
        w.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _iter_manifest():
    if not MANIFEST.exists():
        return
    with MANIFEST.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                # Ligne invalide (ex: chemins Windows non échappés) -> on ignore
                continue


def _find_in_manifest(filename: str) -> Optional[dict]:
    for rec in _iter_manifest():
        if rec.get("filename") == filename:
            return rec
    return None


# -------- Routes --------
@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(
        "<!doctype html><meta charset='utf-8'>"
        "<h1>Demeter – Import</h1>"
        "<form action='/upload' method='post' enctype='multipart/form-data'>"
        "<input type='file' name='file' required>"
        "<button type='submit'>Uploader</button>"
        "</form>"
        "<p><a href='/files'>Voir les fichiers importés</a></p>"
    )


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    dest = INGEST / file.filename
    dest.write_bytes(data)

    mime = file.content_type or "application/octet-stream"
    _append_manifest(file.filename, len(data), mime, dest)

    return JSONResponse(
        {"ok": True, "filename": file.filename, "bytes": len(data), "mime": mime}
    )


@app.get("/files", response_class=HTMLResponse)
def list_files():
    # 1) Essayer via manifest
    rows = []
    for rec in _iter_manifest():
        rows.append(
            "<tr>"
            f"<td>{rec.get('filename','')}</td>"
            f"<td>{rec.get('bytes','')}</td>"
            f"<td>{rec.get('mime','')}</td>"
            f"<td><a href='/preview/{rec.get('filename','')}'>voir</a></td>"
            "</tr>"
        )
    # 2) Fallback: scanner le dossier si le manifest est vide/invalide
    if not rows:
        for p in sorted(INGEST.glob("*")):
            if p.name == "manifest.jsonl" or not p.is_file():
                continue
            size = p.stat().st_size
            mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            rows.append(
                "<tr>"
                f"<td>{p.name}</td>"
                f"<td>{size}</td>"
                f"<td>{mime}</td>"
                f"<td><a href='/preview/{p.name}'>voir</a></td>"
                "</tr>"
            )

    body = "".join(rows)
    return HTMLResponse(
        "<!doctype html><meta charset='utf-8'>"
        "<h2>Fichiers importés</h2>"
        "<table border=1 cellpadding=6 cellspacing=0>"
        "<tr><th>fichier</th><th>octets</th><th>mime</th><th>actions</th></tr>"
        f"{body}</table>"
        "<p><a href='/'>← retour</a></p>"
    )


@app.get("/preview/{filename}")
def preview(filename: str):
    # 1) Manifest si possible
    rec = _find_in_manifest(filename)
    if rec:
        p = Path(rec.get("path", ""))
        mime = rec.get("mime", "application/octet-stream")
    else:
        # 2) Fallback direct sur le disque
        p = INGEST / filename
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    if not p.exists():
        raise HTTPException(status_code=404, detail="Fichier introuvable.")

    # Aperçu simple pour texte/csv (limite taille)
    if mime.startswith("text/") or mime.endswith("/csv") or p.suffix.lower() in {".txt", ".csv", ".md"}:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = p.read_bytes()[:4096].decode("utf-8", errors="replace")
        head = text[:4000]
        return HTMLResponse(
            "<!doctype html><meta charset='utf-8'>"
            f"<h2>Aperçu: {filename}</h2>"
            "<pre style='white-space:pre-wrap;border:1px solid #ccc;padding:8px;'>"
            f"{head}</pre>"
            "<p><a href='/files'>← fichiers</a></p>"
        )

    # Fallback brut
    return PlainTextResponse(
        f"Aperçu non supporté pour {filename} (mime={mime})", status_code=200
    )
from fastapi import HTTPException
import json

@app.get("/preview/{filename}")
def preview_file(filename: str):
    manifest_path = INGEST / "manifest.jsonl"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="manifest not found")

    # Chercher le fichier dans le manifest
    try:
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("filename") == filename:
                try:
                    return (INGEST / filename).read_text(encoding="utf-8")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"invalid manifest: {e}")

    raise HTTPException(status_code=404, detail="file not found")


from fastapi import Form

@app.post("/chat")
def chat(q: str = Form(...)):
    text = (q or "")
    low = text.lower()
    if ("csv" in low) or ("import" in low) or ("fichier" in low):
        return {"intent": "upload", "hint": "/files"}
    return {"intent": "chat", "echo": text}