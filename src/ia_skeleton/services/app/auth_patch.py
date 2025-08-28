from . import webui as _webui
app = _webui.app

import os
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# --- CORS ---
_allowed = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in _allowed.split(",")] if _allowed else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth par header Bearer ---
PROTECT_PATHS = ("/logs",)  # protège /logs, /logs/stream, /logs/export
def _requires_auth(scope: dict) -> bool:
    path = scope.get("path") or ""
    return any(path.startswith(p) for p in PROTECT_PATHS)

@app.middleware("http")
async def token_guard(request, call_next):
    token = os.getenv("DEMETER_TOKEN")
    if token and _requires_auth(request.scope):
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer ") or auth.removeprefix("Bearer ").strip() != token:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    return await call_next(request)
