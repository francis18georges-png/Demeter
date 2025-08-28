# package init
try:
    from . import home_patch  # applique la route "/" minimale
except Exception:
    pass
try:
    from . import logs_viewer  # expose /logs/viewer
except Exception:
    pass
try:
    from . import auth_patch  # protège /logs*
except Exception:
    pass
try:
    from . import logs_level_patch  # filtre /logs par ?level=
except Exception:
    pass
try:
    from . import logs_stream_level_patch  # filtre SSE /logs/stream par ?level=
except Exception:
    pass
try:
    from . import logs_stream_event_patch  # filtre SSE /logs/stream par ?event=
except Exception:
    pass
try:
    from . import logs_event_patch  # filtre /logs par ?event=
except Exception:
    pass
