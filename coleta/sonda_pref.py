"""Sonda temporária: API do portal da transparência Elotech (Maringá)."""
import sys, re, requests, json
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
B = "https://maringa.oxy.elotech.com.br"
def g(u, **k):
    try:
        r = requests.get(u, headers={**H, **k.get("h", {})}, timeout=30)
        if r.ok: return r
    except Exception: pass
    return gbr(u, headers={**H, **k.get("h", {})}, timeout=60)
t = g(B + "/portaltransparencia/1/servidores").text
js = re.findall(r'src="([^"]+\.js)"', t); print("JS", js[:8], flush=True)
for j in js:
    s = g(j if j.startswith("http") else B + "/portaltransparencia/" + j.lstrip("/")).text if j else ""
    apis = sorted(set(re.findall(r'["\'`](/?portaltransparencia-api/[\w/{}$.-]*)', s)))
    sv = sorted(set(re.findall(r'["\'`]([\w/-]*servidor[\w/-]*)["\'`]', s)))[:30]
    if apis or sv: print("API", j[-40:], apis[:20], sv, flush=True)
for u in [B + "/portaltransparencia-api/api/servidores?entidade=1&exercicio=2026&page=0&size=2", B + "/portaltransparencia-api/api/entidades",
          B + "/portaltransparencia-api/api/servidores/folha?entidade=1&exercicio=2026&mes=10&page=0&size=2"]:
    r = g(u, h={"accept": "application/json"}); print("TRY", u[len(B):], r.status_code if r is not None else None, (r.text[:500] if r is not None else "").replace("\n", " "), flush=True)
