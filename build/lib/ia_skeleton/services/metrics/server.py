from prometheus_client import start_http_server, Counter, Gauge
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

