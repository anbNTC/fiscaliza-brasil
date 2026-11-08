"""Exploração (temporária): lista links e respostas das fontes de PE, RS e ES pela saída do Brasil."""
import re, sys, json
sys.path.insert(0, __import__("os").path.dirname(__file__))
from saida_br import get
ALVOS = sys.argv[1:] or ["https://dadosabertos.alepe.pe.gov.br/", "https://ww4.al.rs.gov.br/", "https://www3.al.es.gov.br/", "https://www.al.es.gov.br/"]
for u in ALVOS:
    raw = u.startswith("RAW:"); u = u[4:] if raw else u
    pad = None
    if u.startswith("GREP:"): pad, u = u[5:].split("|", 1)
    r = get(u, tentativas=1)
    print("=" * 8, u, r.status_code if r is not None else None, r.headers.get("content-type") if r is not None else "")
    if r is None: continue
    t = r.text
    if pad:
        vis = set()
        for m in re.finditer(pad, t, re.I):
            a = max(0, m.start() - 120); trecho = re.sub(r"\s+", " ", t[a:m.end() + 180])
            if trecho[:60] in vis: continue
            vis.add(trecho[:60]); print("  ..", trecho)
            if len(vis) > 60: break
        continue
    if raw:
        t2 = re.sub(r"<style[\s\S]*?</style>|<svg[\s\S]*?</svg>", "", t)
        for m in re.finditer(r"https?://[^\s\"'<>]+|/[A-Za-z0-9_\-/.]*(api|json|ashx|asmx|svc|Proposic|propos|Handler|WebService)[A-Za-z0-9_\-/.?=&]*", t2, re.I):
            print("  ", m.group(0)[:200])
        print(t2[:3000]); continue
    if "json" in (r.headers.get("content-type") or "") or t[:1] in "[{":
        print(t[:2500]); continue
    links = sorted(set(re.findall(r'href="([^"#]+)"', t)))
    print("title:", (re.search(r"<title>([\s\S]*?)</title>", t) or [None, ""])[1].strip()[:120])
    print("\n".join(l for l in links if re.search(r"dado|api|propos|deput|parlament|projet|vota|materia|lei|swagger|json|csv", l, re.I))[:4000])
