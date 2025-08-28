from . import webui as _webui
app = _webui.app

import json
from starlette.responses import StreamingResponse

@app.middleware("http")
async def filter_stream_by_level(request, call_next):
    try:
        if request.method == "GET" and (request.url.path or "") == "/logs/stream":
            level = request.query_params.get("level")
            if level:
                resp = await call_next(request)
                ctype = resp.headers.get("content-type","")
                if resp.status_code == 200 and "text/event-stream" in ctype:
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
                                            if isinstance(obj, dict) and obj.get("level") != level:
                                                keep = False
                                        except Exception:
                                            pass
                                if keep:
                                    yield event + b"\n\n"
                        # (fin de stream) on ignore un éventuel fragment incomplet
                    return StreamingResponse(gen(), media_type="text/event-stream")
                return resp
    except Exception:
        pass
    return await call_next(request)
