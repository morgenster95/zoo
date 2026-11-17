"""Bezpečné volání PixelLab MCP (https://api.pixellab.ai/mcp). Klíč NIKDY v repu: jen v prostředí  PIXELLAB_API_KEY=... python3 tools/pixellab.py ...

  tools                       seznam nástrojů (zdarma)
  balance                     zůstatek generací (zdarma)
  call <nástroj> '<json>'     obecné volání (např. get_image, list_jobs); u generování používej `gen`
  gen <název> <nástroj> '<json>'   generování s pojistkou: stejný název v ledgeru = NIC se neodešle, jedno odeslání, žádná opakování
Ledger: art/pixellab/ledger.jsonl (název, nástroj, parametry, job, čas). Opakovat odeslání po chybě ručně jen po kontrole, že se nic nepřijalo."""
import json, os, re, sys, time, urllib.request
URL = "https://api.pixellab.ai/mcp"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "art", "pixellab", "ledger.jsonl")
KEY = os.environ.get("PIXELLAB_API_KEY") or sys.exit("Chybí PIXELLAB_API_KEY v prostředí")
_sid = None

def _post(body, sid=None):
    h = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if sid: h["Mcp-Session-Id"] = sid
    req = urllib.request.Request(URL, json.dumps(body).encode(), h)
    with urllib.request.urlopen(req, timeout=600) as r:
        sid2 = r.headers.get("Mcp-Session-Id"); raw = r.read().decode()
    out = None
    for line in raw.splitlines():
        if line.startswith("data:"): out = json.loads(line[5:])
    if out is None and raw.strip().startswith("{"): out = json.loads(raw)
    return out, sid2

def rpc(method, params=None, id_=2):
    global _sid
    if not _sid:
        _, _sid = _post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "zoo", "version": "1"}}})
        if _sid: _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, _sid)
    r, _ = _post({"jsonrpc": "2.0", "id": id_, "method": method, "params": params or {}}, _sid)
    return r

def call(tool, args):
    r = rpc("tools/call", {"name": tool, "arguments": args})
    c = (r or {}).get("result", {}).get("content") or []
    out = "\n".join(x.get("text", "") for x in c if x.get("type") == "text")
    return out or json.dumps(r)[:2000]

def ledger():
    return [json.loads(l) for l in open(LEDGER) if l.strip()] if os.path.exists(LEDGER) else []

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "tools":
        r = rpc("tools/list")
        for t in (r or {}).get("result", {}).get("tools", []):
            print(f"- {t['name']}: {(t.get('description') or '')[:150].strip()}")
    elif a[0] == "balance":
        print(call("get_balance", {}))
    elif a[0] == "call":
        print(call(a[1], json.loads(a[2]) if len(a) > 2 else {}))
    elif a[0] == "gen":
        name, tool, args = a[1], a[2], json.loads(a[3])
        if any(e.get("name") == name for e in ledger()):
            sys.exit(f"STOP: {name} už je v ledgeru. Nic neodesláno.")
        jobs = call("list_jobs", {})
        m = re.match(r"(\d+) jobs", jobs.strip())
        if m and int(m.group(1)) >= 6: sys.exit("STOP: fronta PixelLabu je plná, počkej a spusť ručně.")
        out = call(tool, args)
        job = re.search(r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", out)
        with open(LEDGER, "a") as f:   # zapíše se vždy po odeslání, i když se výsledek nepodaří přečíst
            f.write(json.dumps({"name": name, "tool": tool, "args": {k: v for k, v in args.items() if k != "palette"}, "job": job and job.group(1), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")
        print(out[:1500])
    elif a[0] == "wait":   # wait <job_id> <soubor.png>  : čeká na hotový obrázek a stáhne ho (jen čtení, nic nevytváří)
        job, dst = a[1], a[2]
        for _ in range(60):
            r = call("get_image", {"job_id": job})
            m = re.search(r"https://\S+?\.png\S*", r) or re.search(r"download[^\n]*?(https://\S+)", r)
            if m:
                url = m.group(1) if m.lastindex else m.group(0)
                urllib.request.urlretrieve(url.rstrip(").,'\""), dst); print("uloženo", dst); break
            if re.search(r"fail|error", r, re.I): sys.exit(r[:600])
            time.sleep(10)
        else:
            sys.exit("ještě není hotovo: " + r[:300])
    else:
        sys.exit(__doc__)
