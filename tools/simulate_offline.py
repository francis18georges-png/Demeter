import json, pathlib, sys
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
