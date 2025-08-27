import os, hmac, hashlib, json, sys, pathlib, time
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
