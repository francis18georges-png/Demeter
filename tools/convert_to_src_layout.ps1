# --- Convertit le dépôt en layout src/ + package unique ia_skeleton ---

$ErrorActionPreference = "Stop"

# 0) SÉCURITÉ : snapshot
if (!(Test-Path snapshots)) { New-Item -ItemType Directory -Path snapshots | Out-Null }
python tools\snapshot.py

# 1) Arbo cible
New-Item -ItemType Directory -Path src\ia_skeleton -Force | Out-Null

# 2) Déplacer le code Python "paquetable" sous src/ia_skeleton
#    On prend tout ce qui est .py dans services/ et éventuellement libs réutilisables
$moveRoots = @("services")
foreach ($root in $moveRoots) {
  if (Test-Path $root) {
    Copy-Item $root src\ia_skeleton\ -Recurse -Force
    Remove-Item $root -Recurse -Force
  }
}

# 3) Créer __init__.py
New-Item -ItemType File -Path src\ia_skeleton\__init__.py -Force | Out-Null

# 4) Réécrire les imports "from services..." -> "from ia_skeleton.services..."
#    et "import services...." -> "import ia_skeleton.services..."
$pyFiles = Get-ChildItem -Path src\ia_skeleton -Recurse -Include *.py
foreach ($f in $pyFiles) {
  $c = Get-Content $f.FullName -Raw
  $c = $c -replace 'from\s+services(\S*)\s+import', 'from ia_skeleton.services$1 import'
  $c = $c -replace 'import\s+services(\S*)', 'import ia_skeleton.services$1'
  Set-Content $f.FullName -Value $c -Encoding UTF8
}

# 5) Mettre à jour pyproject.toml (ajoute la config setuptools find vers src)
$pp = "pyproject.toml"
if (-not (Test-Path $pp)) { throw "pyproject.toml introuvable" }
$txt = Get-Content $pp -Raw

# Ajoute setuptools dans build (si absent)
if ($txt -notmatch '\[build-system\]') {
  $txt = $txt + @"

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

"@
}

# Ajoute bloc find packages
if ($txt -notmatch '\[tool\.setuptools\.packages\.find\]') {
  $txt = $txt + @"

[tool.setuptools.packages.find]
where = ["src"]

"@
}

# Ajoute dépendances dev utiles si absentes
if ($txt -notmatch 'prometheus-client') {
  $txt = $txt -replace 'dependencies\s*=\s*\[', 'dependencies = [
  "prometheus-client>=0.20.0",
  "opentelemetry-sdk>=1.26.0",
  "opentelemetry-exporter-otlp>=1.26.0",'
}

Set-Content $pp -Value $txt -Encoding UTF8

# 6) Corriger chemins des scripts qui pointaient vers services/
#    Exemple: services\metrics\server.py déplacé -> src\ia_skeleton\services\metrics\server.py
#    Les lanceurs .cmd restent valides si on les appelle via "python -m ia_skeleton.services.metrics.server"
#    On met à jour LaunchMetricsServer.cmd si présent.
$launcher = "LaunchMetricsServer.cmd"
if (Test-Path $launcher) {
  $lc = Get-Content $launcher -Raw
  $lc = "@echo off`r`npython -m ia_skeleton.services.metrics.server`r`n"
  Set-Content $launcher -Value $lc -Encoding ASCII
}

# 7) Installer en editable propre (facultatif) + deps dev
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .

Write-Host "OK: conversion terminée. Package = ia_skeleton (src/)."
Write-Host "Exemples:"
Write-Host "  python -m ia_skeleton.services.app.min_echo"
Write-Host "  python -m ia_skeleton.services.metrics.server"
