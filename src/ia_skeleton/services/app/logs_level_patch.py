from . import webui as _webui
app = _webui.app

import json
from starlette.responses import JSONResponse

@app.middleware("http")
async def filter_logs_by_level(request, call_next):
    # On ne s’applique qu’à GET /logs avec un param level
    try:
        if request.method == "GET" and (request.url.path or "") == "/logs":
            level = request.query_params.get("level")
            if level:
                # Laisser le handler original s'exécuter
                resp = await call_next(request)

                # On ne traite que le JSON (pas les streams/fichiers)
                ctype = resp.headers.get("content-type","")
                if resp.status_code == 200 and "application/json" in ctype:
                    # Lire le corps
                    body = b"".join([chunk async for chunk in resp.body_iterator])
                    try:
                        data = json.loads(body.decode("utf-8"))
                        if isinstance(data, list):
                            data = [e for e in data if isinstance(e, dict) and e.get("level") == level]
                            return JSONResponse(data, status_code=200)
                    except Exception:
                        pass
                    # Si parsing échoue, on renvoie la réponse intacte
                    return JSONResponse(content=json.loads(body.decode("utf-8")), status_code=resp.status_code)
                return resp
    except Exception:
        # En cas de souci, ne pas casser la route
        pass
    return await call_next(request)
