import json, subprocess, pathlib, datetime
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
