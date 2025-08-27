@echo off
python -m pip install --upgrade pip
pip install -r requirements-dev.txt || exit /b 1

flake8 || exit /b 1
pytest -q || exit /b 1

python tools\simulate_offline.py || exit /b 1
python tools\sbom_gen.py || exit /b 1

if "%ADMIN_HMAC_SECRET%"=="" set ADMIN_HMAC_SECRET=dev-secret
python tools\sbom_sign.py artifacts\sbom\sbom.json || exit /b 1
echo OK: Go/No-Go passed
