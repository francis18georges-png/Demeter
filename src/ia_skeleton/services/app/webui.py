from fastapi import FastAPI, UploadFile, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pathlib import Path
from .intent_router import route
import hashlib, json, time, mimetypes, html

app = FastAPI(title="Demeter UI")
BASE = Path(__file__).resolve().parents[4]
INGEST = BASE / "ingest" / "local"
INGEST.mkdir(parents=True, exist_ok=True)
MANIFEST = INGEST / "manifest.jsonl"

HTML = """<!doctype html><html><head><meta charset="utf-8"><title>Demeter</title></head>
<body style="font-family:system-ui;max-width:900px;margin:40px auto">
  <h2>Demeter — Import & Chat</h2>
  <form action="/upload" method="post" enctype="multipart/form-data" style="margin-bottom:24px">
    <input type="file" name="files" multiple required>
    <button type="submit">Uploader</button>
  </form>
  <form action="/chat" method="post" style="margin-bottom:24px">
    <input type="text" name="q" placeholder="Posez une question" style="width:70%">
    <button type="submit">Envoyer</button>
  </form>
  <a href="/files">Voir les fichiers importés</a>
</body></html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

@app.post("/upload")
async def upload(files: list[UploadFile]):
    saved = []
    for f in files:
        data = await f.read()
        if len(data) > 20*1024*1024:
            return {"status":"error","reason":f"{f.filename} > 20MB"}
        out = INGEST / Path(f.filename).name
        out.write_bytes(data)
        meta = {
            "ts": int(time.time()),
            "filename": Path(f.filename).name,
            "bytes": len(data),
            "sha256": _sha256_bytes(data),
            "mime": f.content_type or mimetypes.guess_type(f.filename)[0] or "application/octet-stream",
            "path": str(out)
        }
        MANIFEST.touch()
        with MANIFEST.open("a", encoding="utf-8") as w:
            w.write(json.dumps(meta, ensure_ascii=False) + "\n")
        saved.append(meta)
    return {"status":"ok","count": len(saved), "files": saved}

def _read_manifest():
    if not MANIFEST.exists(): return []
    rows = []
    with MANIFEST.open("r", encoding="utf-8") as r:
        for line in r:
            line=line.strip()
            if not line: continue
            try: rows.append(json.loads(line))
            except Exception: pass
    return rows

@app.get("/files", response_class=HTMLResponse)
def files():
    rows = _read_manifest()
    rows.sort(key=lambda x: x.get("ts",0), reverse=True)
    def tr(m):
        name = html.escape(m["filename"])
        sz = m.get("bytes",0)
        mime = html.escape(m.get("mime",""))
        return f"<tr><td>{name}</td><td>{sz}</td><td>{mime}</td><td><a href='/preview?name={name}'>prévisualiser</a></td></tr>"
    table = "<table border=1 cellpadding=6 cellspacing=0><tr><th>fichier</th><th>octets</th><th>mime</th><th>actions</th></tr>" + "".join(tr(m) for m in rows) + "</table>"
    return f"<!doctype html><meta charset='utf-8'><h2>Fichiers importés</h2>{table}<p><a href='/'>← retour</a></p>"

_TEXT_EXTS = {".txt",".md",".csv",".json",".yaml",".yml",".log"}
_MAX_PREVIEW = 200_000

@app.get("/preview", response_class=HTMLResponse)
def preview(name: str = Query(..., min_length=1)):
    safe = Path(name).name
    file_path = INGEST / safe
    if not file_path.exists(): raise HTTPException(404, "fichier introuvable")
    if file_path.suffix.lower() not in _TEXT_EXTS:
        return HTMLResponse(f"Prévisualisation limitée pour {html.escape(safe)} (type non texte).", status_code=200)
    data = file_path.read_bytes()[:_MAX_PREVIEW]
    txt = data.decode("utf-8", errors="replace")
    escaped = html.escape(txt)
    return f"<!doctype html><meta charset='utf-8'><h3>Prévisualisation: {html.escape(safe)}</h3><pre style='white-space:pre-wrap'>{escaped}</pre><p><a href='/files'>← fichiers</a></p>"

@app.post("/chat", response_class=PlainTextResponse)
async def chat(q: str = Form("")):
    intent = route(q)
    if intent == "upload_file":
        return "Intent: upload_file → utilisez le formulaire ci-dessus."
    if intent == "ask_question":
        return f"Intent: ask_question → echo: {q}"
    return "Intent: unknown"
