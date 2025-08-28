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
  .row{display:flex;gap:8px;align-items:center;margin:12px 0;flex-wrap:wrap}
  input,select,button{padding:6px 10px}
  table{border-collapse:collapse;width:100%;margin-top:12px}
  th,td{border:1px solid #ddd;padding:6px 8px;font-size:14px}
  th{background:#f7f7f7;text-align:left}
  .pill{display:inline-block;padding:2px 6px;border-radius:10px;background:#eee}
</style>
<h1>Logs viewer</h1>

<div class="row">
  <label>Access token:
    <input id="f-token" placeholder="Bearer token" style="min-width:240px">
  </label>
  <button id="btn-save-token">Enregistrer le token</button>
  <a id="btn-export" href="/logs/export"><button>Exporter (.tar.gz)</button></a>
</div>
<div class="row">
  <button id="btn-copy-link">Copier le lien partageable</button>
  <span id="copy-status" class="pill" style="display:none">copié ✓</span>
</div>

<div class="row">
  <label>event: <input id="f-event" placeholder="upload / preview"></label>
    <label>level: <select id="f-level">
      <option value="">(tous)</option>
      <option>critical</option><option>error</option><option>warning</option>
      <option>info</option><option>debug</option><option>trace</option>
    </select></label>
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
const qsTok = (new URLSearchParams(location.search)).get("access_token") || "";
const storedTok = localStorage.getItem("demeter_token") || "";
let TOK = storedTok || qsTok || "";
if(!storedTok && qsTok){ localStorage.setItem("demeter_token", qsTok); }
document.addEventListener("DOMContentLoaded", () => {
  document.querySelector("#f-token").value = TOK;
  syncExportLink();
});

function setTok(v){ TOK = (v||"").trim(); localStorage.setItem("demeter_token", TOK); syncExportLink(); }
function syncExportLink(){
  const a = document.querySelector("#btn-export");
  const u = new URL(a.getAttribute("href"), location.origin);
  if(TOK){ u.searchParams.set("access_token", TOK); } else { u.searchParams.delete("access_token"); }
  a.setAttribute("href", u.pathname + (u.search ? u.search : ""));
}
function addTok(url){
  if(!TOK) return url;
  const u=new URL(url, location.origin);
  u.searchParams.set("access_token", TOK);
  return u.pathname + "?" + u.searchParams.toString();
}
function authHeaders(){
  return TOK ? { "Authorization": "Bearer " + TOK } : {};
}
const $=s=>document.querySelector(s);
function row(e){
  const o={...e}; delete o.ts; delete o.event; delete o.level;
  const fields=Object.entries(o).map(([k,v])=>k+"="+JSON.stringify(v)).join(" ");
  const tr=document.createElement("tr");
  tr.innerHTML = "<td>"+e.ts+"</td><td>"+(e.event||"")+"</td><td>"+(e.level||"")+"</td><td>"+fields+"</td>";
  return tr;
}

async function reload(){
  const ev=$("#f-event").value.trim(), sn=$("#f-since").value.trim(), od=$("#f-order").value.trim();
  const qs=new URLSearchParams({limit:"200",order:od||"desc"});
 if(ev) qs.set("event",ev);
 const lv=$("#f-level").value.trim(); if(lv) qs.set("level",lv);
 if(sn) qs.set("since_ts",sn);
  const r=await fetch("/logs?"+qs.toString(), { headers: authHeaders() });
  if(!r.ok){ alert("Erreur "+r.status+" — pensez à remplir le token."); return; }
  const data=await r.json();
  const tbody=$("#tbl tbody"); tbody.innerHTML="";
  for(const e of data){ tbody.appendChild(row(e)); }
}

function toggleSSE(){
  const tbody=$("#tbl tbody");
  if(window.__es){ window.__es.close(); window.__es=null; $("#sse-state").textContent="SSE: off"; return; }
  let attempt=0, es=null;
  const connect=()=>{
    const ev=$("#f-event").value.trim(), sn=$("#f-since").value.trim(), lv=$("#f-level").value.trim();
    const qs=new URLSearchParams(); if(ev) qs.set("event",ev); if(lv) qs.set("level",lv); qs.set("since_ts", sn||"0");
    es = new EventSource(addTok("/logs/stream?"+qs.toString()));
    window.__es = es; $("#sse-state").textContent="SSE: on";
    es.onmessage=(msg)=>{ attempt=0; try{
      const e=JSON.parse(msg.data);
      tbody.insertBefore(row(e), tbody.firstChild);
      $("#f-since").value=String(e.ts);
    }catch(_){ }};
    es.onerror=()=>{ es.close(); $("#sse-state").textContent="SSE: reconnecting…";
      attempt++; const delay=Math.min(30000, 1000*Math.pow(2, attempt)); setTimeout(connect, delay);
    };
  };
  connect();
}const ev=$("#f-event").value.trim(), sn=$("#f-since").value.trim();
  const qs=new URLSearchParams(); if(ev) qs.set("event",ev); qs.set("since_ts", sn||"0");
  // EventSource => query token obligatoire (pas de headers possibles)
  window.__es=new EventSource(addTok("/logs/stream?"+qs.toString()));
  $("#sse-state").textContent="SSE: on";
  window.__es.onmessage=(msg)=>{ try{
    const e=JSON.parse(msg.data);
    tbody.insertBefore(row(e), tbody.firstChild);
    $("#f-since").value=String(e.ts);
  }catch(_){ }};
  window.__es.onerror=()=>{ $("#sse-state").textContent="SSE: error"; };
}

$("#btn-save-token").onclick=()=>{ setTok($("#f-token").value); alert("Token enregistré."); };
$("#btn-reload").onclick=reload;
$("#btn-sse").onclick=toggleSSE;
reload();
</script>
""")


