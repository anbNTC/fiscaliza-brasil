"""Sonda (temporária): descobre a API do portal de transparência Elotech (eloweb) usado pela Câmara de Curitiba."""
import requests, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import saida_br
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}
B = "https://cmcuritiba.eloweb.net"
def g(u, br=False):
    try: return saida_br.get(u, headers=H, timeout=90, tentativas=1) if br else requests.get(u, headers=H, timeout=90)
    except Exception as e: print(u, repr(e)[:150]); return None
br = False
for br in (False, True):
    r = g(B + "/portaltransparencia/1/servidores", br); print("== pagina", "br" if br else "direto", r.status_code if r is not None else None, len(r.text) if r is not None else 0)
    if r is not None and r.ok: break
t = r.text if r is not None else ""
srcs = re.findall(r'src="([^"]+\.js)"', t); print("scripts", srcs)
achados = set()
for s in srcs:
    u = s if s.startswith("http") else B + (s if s.startswith("/") else "/portaltransparencia/" + s)
    j = g(u, br)
    if j is None or not j.ok: print("js falhou", u); continue
    js = j.text; print("js", u, len(js))
    for m in re.findall(r'["\'`](/?[a-zA-Z0-9_\-/]*(?:api|servidor|folha|remunera)[a-zA-Z0-9_\-/{}$.]*)["\'`]', js):
        if len(m) < 120: achados.add(m)
    for m in re.findall(r'https?://[a-zA-Z0-9.\-]+/[a-zA-Z0-9_\-/]*', js):
        if "api" in m.lower(): achados.add(m)
print("\n".join(sorted(achados)[:150]))
