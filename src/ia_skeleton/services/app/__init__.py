# package init
try:
    from . import home_patch  # applique la route "/" minimale
except Exception:
    pass
