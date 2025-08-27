import subprocess, sys
def test_simulate_offline_ok():
    r = subprocess.run([sys.executable,'tools/simulate_offline.py'], capture_output=True, text=True)
    assert r.returncode==0
