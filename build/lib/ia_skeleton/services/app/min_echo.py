from ia_skeleton.services.common.tracing import init_tracer
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

