import tarfile, time, pathlib, os
OUT=pathlib.Path("snapshots"); OUT.mkdir(parents=True, exist_ok=True)
ts=time.strftime("%Y%m%d_%H%M%S")
name=OUT/f"snapshot_{ts}.tar.gz"
with tarfile.open(name, "w:gz") as tar:
    for p in ["policies","bench","services","observability",".github","tools","ingest"]:
        if pathlib.Path(p).exists(): tar.add(p, arcname=p)
print(f"SNAPSHOT {name}")
