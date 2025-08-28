from . import webui as _webui
app = _webui.app

from starlette.responses import HTMLResponse

@app.get("/logs/viewer")
def logs_viewer():
    return HTMLResponse("""<!doctype html><meta charset='utf-8'>
<title>Logs viewer</title>
<style>
  body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:24px}
  h1{margin:0 0 12px}
  .row{display:flex;gap:8px;align-items:center;margin:12px 0}
  input,select,button{padding:6px 10px}
  table{border-collapse:collapse;width:100%;margin-top:12px}
  th,td{border:1px solid #ddd;padding:6px 8px;font-size:14px}
  th{background:#f7f7f7;text-align:left}
  .pill{display:inline-block;padding:2px 6px;border-radius:10px;background:#eee}
</style>
<h1>Logs viewer</h1>

<div class="row">
  <a href="/logs/export"><button>Exporter (.tar.gz)</button></a>
  <label>event: <input id="f-event" placeholder="upload / preview"></label>
  <label>since_ts(ms): <input id="f-since" type="number" placeholder="0"></label>
  <label>order: <select id="f-order"><option>desc</option><option>asc</option></select></label>
  <button id="btn-reload">Recharger</button>
  <span id="sse-state" class="pill">SSE: off</span>
  <button id="btn-sse">Live (SSE)</button>
</div>

<table id="tbl">
  <thead><tr><th>ts</th><th>event</th><th>level</th><th>fields</th></tr></thead>
  <tbody></tbody>
</table>

<script>
let es=null; const $=s=>document.querySelector(s); const tbody=$("#tbl tbody");
function row(e){
  const o={...e}; delete o.ts; delete o.event; delete o.level;
  const fields=Object.entries(o).map(([k,v])=>k+"="+JSON.stringify(v)).join(" ");
  const tr=document.createElement("tr");
  tr.innerHTML = "<td>"+e.ts+"</td><td>"+(e.event||"")+"</td><td>"+(e.level||"")+"</td><td>"+fields+"</td>";
  return tr;
}
async function reload(){
  const ev=$("#f-event").value.trim(), sn=$("#f-since").value.trim(), od=$("#f-order").value.trim();
  const qs=new URLSearchParams({limit:"200",order:od||"desc"}); if(ev) qs.set("event",ev); if(sn) qs.set("since_ts",sn);
  const r=await fetch("/logs?"+qs.toString()); const data=await r.json();
  tbody.innerHTML=""; for(const e of data){ tbody.appendChild(row(e)); }
}
function toggleSSE(){
  if(es){ es.close(); es=null; $("#sse-state").textContent="SSE: off"; return; }
  const ev=$("#f-event").value.trim(), sn=$("#f-since").value.trim(); const qs=new URLSearchParams();
  if(ev) qs.set("event",ev); qs.set("since_ts", sn||"0");
  es=new EventSource("/logs/stream?"+qs.toString()); $("#sse-state").textContent="SSE: on";
  es.onmessage = msg=>{ try{ const e=JSON.parse(msg.data); tbody.insertBefore(row(e), tbody.firstChild); $("#f-since").value=String(e.ts); }catch(_){} };
  es.onerror = ()=>{ $("#sse-state").textContent="SSE: error"; };
}
$("#btn-reload").onclick=reload; $("#btn-sse").onclick=toggleSSE; reload();
</script>
""")
