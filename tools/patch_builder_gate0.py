#!/usr/bin/env python3
import os, sys, json, pathlib, textwrap, datetime, hashlib

ROOT = pathlib.Path(".").resolve()

FILES = {
# ---------- README / CHANGELOG ----------
"README.md": """# IA — Squelette Gate 0
Squelette minimal pour lancer le plan par étapes : policies, CI, observabilité, golden sets, simulateur, SBOM, snapshots.
""",
"CHANGELOG.md": """# Changelog
- {d} Init Gate 0 skeleton.
""".format(d=datetime.date.today().isoformat()),

# ---------- PYPROJECT / REQS / MAKE ----------
"pyproject.toml": """[project]
name = "ia-skeleton"
version = "0.0.1"
description = "Gate0 skeleton"
requires-python = ">=3.10"
dependencies = [
  "prometheus-client>=0.20.0",
  "opentelemetry-sdk>=1.26.0",
  "opentelemetry-exporter-otlp>=1.26.0",
  "pytest>=8.3.0",
  "flake8>=7.1.0",
]
[tool.pytest.ini_options]
pythonpath = ["."]
""",
"requirements-dev.txt": """cyclonedx-bom>=3.13.0
safety>=3.2.0
jsonschema>=4.23.0
""",
"Makefile": """.DEFAULT_GOAL:=all
all: lint test sbom
lint:
\tflake8
test:
\tpytest -q
sbom:
\tpython tools/sbom_gen.py && python tools/sbom_sign.py artifacts/sbom/sbom.json
""",

# ---------- POLICIES ----------
"policies/policy.yaml": """auto_editable:
  - services/retrieval/**
  - services/rag/**
blocked_areas:
  - services/auth/**
  - services/system/**
web_allowlist:
  - "docs.python.org"
  - "developer.mozilla.org"
  - "rfc-editor.org"
local_ingest:
  local_allowlist: ["datasets/**"]
  deny_ext: [".exe",".dll"]
  max_file_size_mb: 200
  pii_default: "mask"
quotas:
  patches_per_day: 5
  web_requests_per_task: 50
gates:
  coverage_min: 0.80
  sast_high_max: 0
  perf_p95_slowdown_max: 0.02
admin_mode:
  enabled: false
  kill_switch_file: "admin/KILL"
""",

# ---------- OBSERVABILITÉ (Prometheus + Traces) ----------
"observability/prometheus/prometheus.yml": """global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'app'
    static_configs: [{ targets: ['localhost:8000'] }]
""",
"services/common/tracing.py": """from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
def init_tracer(service_name="ia-skeleton"):
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
""",
"services/metrics/server.py": """from prometheus_client import start_http_server, Counter, Gauge
import time
REQS = Counter("app_requests_total","Total requests")
LAT  = Gauge("app_last_latency_seconds","Last latency")
def run(port=8000):
    start_http_server(port)
    while True:
        t0=time.perf_counter()
        time.sleep(1.0)
        LAT.set(time.perf_counter()-t0)
        REQS.inc()
if __name__=="__main__":
    run()
""",

# ---------- BENCH / GOLDEN SETS ----------
"bench/golden/queries.jsonl": """{"id":"ex1","q":"Ping","lang":"fr"}\n""",
"bench/golden/answers.jsonl": """{"id":"ex1","a":"Pong"}\n""",

# ---------- SIMULATEUR OFFLINE ----------
"tools/simulate_offline.py": """import json, pathlib, sys
def main():
    qf = pathlib.Path("bench/golden/queries.jsonl")
    af = pathlib.Path("bench/golden/answers.jsonl")
    assert qf.exists() and af.exists()
    qs = [json.loads(l) for l in qf.read_text(encoding="utf-8").splitlines() if l.strip()]
    ans= {json.loads(l)["id"]: json.loads(l)["a"] for l in af.read_text(encoding="utf-8").splitlines() if l.strip()}
    ok=0
    for q in qs:
        # écho minimal pour Gate0
        got = "Pong" if q["q"].lower()=="ping" else "UNKNOWN"
        if got == ans[q["id"]]: ok+=1
    print(f"OK {ok}/{len(qs)}")
    return 0 if ok==len(qs) else 2
if __name__=="__main__":
    sys.exit(main())
""",

# ---------- IMPORT LOCAL (manifest placeholder) ----------
"ingest/local/manifest.jsonl": "",
"tools/import_local.py": """# placeholder Gate0; version complète à livrer en LC
print("OK: manifest placeholder present")""",

# ---------- SNAPSHOT / RESTORE ----------
"tools/snapshot.py": """import tarfile, time, pathlib, os
OUT=pathlib.Path("snapshots"); OUT.mkdir(parents=True, exist_ok=True)
ts=time.strftime("%Y%m%d_%H%M%S")
name=OUT/f"snapshot_{ts}.tar.gz"
with tarfile.open(name, "w:gz") as tar:
    for p in ["policies","bench","services","observability",".github","tools","ingest"]:
        if pathlib.Path(p).exists(): tar.add(p, arcname=p)
print(f"SNAPSHOT {name}")
""",
"tools/restore.py": """import tarfile, sys, pathlib
if len(sys.argv)<2: 
    print("Usage: restore.py <snapshot.tar.gz>"); raise SystemExit(2)
snap=pathlib.Path(sys.argv[1])
with tarfile.open(snap,"r:gz") as tar:
    tar.extractall(".")
print(f"RESTORED {snap}")
""",

# ---------- SBOM + SIGNATURE HMAC ----------
"tools/sbom_gen.py": r"""import json, subprocess, pathlib, datetime
OUT=pathlib.Path("artifacts/sbom"); OUT.mkdir(parents=True, exist_ok=True)
sbom={"bomFormat":"CycloneDX","specVersion":"1.5","version":1,"metadata":{"timestamp":datetime.datetime.utcnow().isoformat()+"Z"},"components":[]}
try:
    pkgs=subprocess.check_output([sys.executable,"-m","pip","freeze"], text=True).splitlines()
except Exception:
    pkgs=[]
for line in pkgs:
    if "@" in line or "git+" in line: continue
    if "==" in line:
        n,v=line.split("==",1)
    else:
        n,v=line, "unknown"
    sbom["components"].append({"type":"library","name":n,"version":v})
path=OUT/"sbom.json"; path.write_text(json.dumps(sbom,indent=2),encoding="utf-8")
print(f"SBOM -> {path}")
""",
"tools/sbom_sign.py": """import os, hmac, hashlib, json, sys, pathlib, time
if len(sys.argv)<2: 
    print("Usage: sbom_sign.py <sbom.json>"); raise SystemExit(2)
secret=os.getenv("ADMIN_HMAC_SECRET","")
if not secret:
    print("Set ADMIN_HMAC_SECRET"); raise SystemExit(3)
p=pathlib.Path(sys.argv[1]); data=p.read_bytes()
sig=hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()
out=p.with_suffix(".sig")
out.write_text(json.dumps({"file":p.name,"alg":"HMAC-SHA256","sig":sig,"ts":int(time.time())},indent=2),encoding="utf-8")
print(f"SIG -> {out}")
""",

# ---------- TESTS (Go/No-Go) ----------
"tests/test_golden_exists.py": """from pathlib import Path
def test_golden_present():
    assert Path('bench/golden/queries.jsonl').exists()
    assert Path('bench/golden/answers.jsonl').exists()
""",
"tests/test_simulator.py": """import subprocess, sys
def test_simulate_offline_ok():
    r = subprocess.run([sys.executable,'tools/simulate_offline.py'], capture_output=True, text=True)
    assert r.returncode==0
""",
"tests/test_policy_yaml.py": """from pathlib import Path
def test_policy():
    txt = Path('policies/policy.yaml').read_text(encoding='utf-8')
    assert 'auto_editable' in txt and 'web_allowlist' in txt
""",

# ---------- GITHUB CI ----------
".github/workflows/ci.yml": """name: Gate0 CI
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: { python-version: '3.11' }
    - name: Install deps
      run: |
        python -m pip install --upgrade pip
        pip install -e . -r requirements-dev.txt
    - name: Lint
      run: flake8
    - name: Unit tests
      run: pytest -q
    - name: Simulate offline
      run: python tools/simulate_offline.py
    - name: SBOM
      run: |
        python tools/sbom_gen.py
        python tools/sbom_sign.py artifacts/sbom/sbom.json
      env:
        ADMIN_HMAC_SECRET: ${{ secrets.ADMIN_HMAC_SECRET || 'dev-secret' }}
    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      with:
        name: gate0-artifacts
        path: |
          artifacts/sbom/*
          snapshots/*
""",

# ---------- ADMIN / PLACEHOLDERS ----------
"admin/README.md": """Admin area: secrets in Vault/CI only. Kill-switch file: admin/KILL""",
"artifacts/.gitkeep": "",
"logs/.gitkeep": "",
"snapshots/.gitkeep": "",

# ---------- SIMPLE APP FOR TRACE/METRICS DEMO ----------
"services/app/min_echo.py": """from services.common.tracing import init_tracer
from prometheus_client import Counter
import time
TR=init_tracer("min-echo")
REQ=Counter("echo_requests_total","Echo requests")
def handle(msg:str)->str:
    with TR.start_as_current_span("echo"):
        REQ.inc()
        time.sleep(0.01)
        return "Pong" if msg.lower()=="ping" else "UNKNOWN"
if __name__=='__main__':
    print(handle("Ping"))
""",
}

WRAPPERS = {
"tools/run_gonogo.cmd": r"""@echo off
REM Run basic Go/No-Go locally on Windows
python -m pip install --upgrade pip
pip install -e . -r requirements-dev.txt
flake8 || exit /b 1
pytest -q || exit /b 1
python tools\simulate_offline.py || exit /b 1
python tools\sbom_gen.py || exit /b 1
set ADMIN_HMAC_SECRET=%ADMIN_HMAC_SECRET:=% 
if "%ADMIN_HMAC_SECRET%"=="" (
  set ADMIN_HMAC_SECRET=dev-secret
)
python tools\sbom_sign.py artifacts\sbom\sbom.json || exit /b 1
echo OK: Go/No-Go passed
""",
"LaunchMetricsServer.cmd": r"""@echo off
REM Start minimal Prometheus metrics endpoint on :8000
python services\metrics\server.py
""",
"Snapshot.cmd": r"""@echo off
python tools\snapshot.py
""",
"Restore.cmd": r"""@echo off
if "%~1"=="" (
  echo Usage: Restore.cmd snapshots\snapshot_YYYYMMDD_HHMMSS.tar.gz
  exit /b 2
)
python tools\restore.py %1
"""
}

def write_file(path, content, force=False):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and not force:
        return
    if isinstance(content, bytes):
        p.write_bytes(content)
    else:
        p.write_text(content, encoding="utf-8")

def main():
    force = "--force" in sys.argv
    for path, content in FILES.items():
        write_file(path, content, force)
    for path, content in WRAPPERS.items():
        write_file(path, content, force)
    print("Gate0 skeleton written.")
    print("Next: set env ADMIN_HMAC_SECRET and run tools/run_gonogo.cmd (Windows) or `make`.")

if __name__ == "__main__":
    main()
