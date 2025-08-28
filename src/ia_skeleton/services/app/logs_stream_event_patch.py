from . import webui as _webui
app = _webui.app

import json
from starlette.responses import StreamingResponse

@app.middleware("http")
async def filter_stream_by_event(request, call_next):
    try:
        if request.method == "GET" and (request.url.path or "") == "/logs/stream":
            wanted = request.query_params.get("event")
            if wanted:
                resp = await call_next(request)
                if resp.status_code == 200 and "text/event-stream" in resp.headers.get("content-type",""):
                    async def gen():
                        buf = b""
                        async for chunk in resp.body_iterator:
                            buf += chunk
                            while b"\n\n" in buf:
                                event, buf = buf.split(b"\n\n", 1)
                                keep = True
                                for ln in event.split(b"\n"):
                                    if ln.startswith(b"data:"):
                                        data = ln[5:].strip()
                                        try:
                                            obj = json.loads(data.decode("utf-8"))
                                            if isinstance(obj, dict) and obj.get("event") != wanted:
                                                keep = False
                                        except Exception:
                                            pass
                                if keep:
                                    yield event + b"\n\n"
                    return StreamingResponse(gen(), media_type="text/event-stream")
                return resp
    except Exception:
        pass
    return await call_next(request)
