# package init
try:
    from . import home_patch  # applique la route "/" minimale
except Exception:
    pass
try:
    from . import logs_viewer  # expose /logs/viewer
except Exception:
    pass
