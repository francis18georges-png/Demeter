from . import webui as _webui
app = _webui.app

import json
from starlette.responses import JSONResponse

@app.middleware("http")
async def filter_logs_by_event(request, call_next):
    try:
        if request.method == "GET" and (request.url.path or "") == "/logs":
            wanted = request.query_params.get("event")
            if wanted:
                resp = await call_next(request)
                ctype = resp.headers.get("content-type","")
                if resp.status_code == 200 and "application/json" in ctype:
                    body = b"".join([chunk async for chunk in resp.body_iterator])
                    try:
                        data = json.loads(body.decode("utf-8"))
                        if isinstance(data, list):
                            data = [e for e in data if isinstance(e, dict) and e.get("event") == wanted]
                            return JSONResponse(data, status_code=200)
                        return JSONResponse(data, status_code=resp.status_code)
                    except Exception:
                        return JSONResponse({"detail":"malformed JSON"}, status_code=500)
                return resp
    except Exception:
        pass
    return await call_next(request)
