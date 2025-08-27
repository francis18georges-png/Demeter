from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
from pathlib import Path
from .intent_router import route

app = FastAPI(title="Demeter UI")
BASE = Path(__file__).resolve().parents[4]
INGEST = BASE / "ingest" / "local"
INGEST.mkdir(parents=True, exist_ok=True)

HTML = """<!doctype html><html><head><meta charset="utf-8"><title>Demeter</title></head>
<body style="font-family:system-ui;max-width:760px;margin:40px auto">
  <h2>Demeter — Import & Chat</h2>
  <form action="/upload" method="post" enctype="multipart/form-data" style="margin-bottom:24px">
    <input type="file" name="file" required>
    <button type="submit">Uploader</button>
  </form>
  <form action="/chat" method="post">
    <input type="text" name="q" placeholder="Posez une question" style="width:70%">
    <button type="submit">Envoyer</button>
  </form>
</body></html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

@app.post("/upload")
async def upload(file: UploadFile):
    out = INGEST / file.filename
    out.write_bytes(await file.read())
    return {"status":"ok","saved": str(out)}

@app.post("/chat", response_class=PlainTextResponse)
async def chat(q: str = Form("")):
    intent = route(q)
    if intent == "upload_file":
        return "Intent: upload_file → utilisez le formulaire ci-dessus."
    if intent == "ask_question":
        return f"Intent: ask_question → echo: {q}"
    return "Intent: unknown"
