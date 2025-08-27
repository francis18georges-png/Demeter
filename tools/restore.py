import tarfile, sys, pathlib
if len(sys.argv)<2: 
    print("Usage: restore.py <snapshot.tar.gz>"); raise SystemExit(2)
snap=pathlib.Path(sys.argv[1])
with tarfile.open(snap,"r:gz") as tar:
    tar.extractall(".")
print(f"RESTORED {snap}")
