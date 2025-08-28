from . import webui as _webui
app = _webui.app

def __override_home_route__():
    try:
        kept = []
        for r in getattr(app.router, "routes", []):
            try:
                path = getattr(r, "path", None)
                methods = set(getattr(r, "methods", set()) or [])
                if not (path == "/" and "GET" in methods):
                    kept.append(r)
            except Exception:
                kept.append(r)
        app.router.routes = kept
    except Exception:
        pass

    from starlette.responses import HTMLResponse

    @app.get("/")
    def logs_home():
        return HTMLResponse("""<!doctype html><meta charset='utf-8'>
<title>Logs viewer</title>
<h1>Logs viewer</h1>
<p><a href='/logs/export'>Exporter les logs (.tar.gz)</a></p>
<p>Endpoints utiles : <code>/logs?limit=...</code> · <code>/logs?since_ts=...</code> · SSE: <code>/logs/stream</code></p>
""")

# appliquer au chargement
__override_home_route__()
