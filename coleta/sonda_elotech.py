"""Sonda (temporária): API de servidores do portal Elotech com os cabeçalhos entidade/exercicio."""
import requests, json, re
B = "https://cmcuritiba.eloweb.net/portaltransparencia-api"
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0", "accept": "application/json", "entidade": "1", "exercicio": "2026"}
def g(u, h=None):
    try:
        r = requests.get(B + u, headers=h or H, timeout=60); print("==", u, r.status_code, r.text[:1200]); return r
    except Exception as e: print(u, e)
ex = requests.get(B + "/api/exercicios/entidade/1", headers=H, timeout=60).json()
print("exercicios:", [ (x.get("id") or {}).get("exercicio") if isinstance(x.get("id"), dict) else x.get("id") for x in ex][:10], json.dumps({k: v for k, v in ex[0].items() if k != "id"})[:300])
g("/api/servidores?entidade=1&exercicio=2026&page=0&size=3")
g("/api/servidores?page=0&size=3")
g("/api/servidores/situacoes")
g("/api/estrutura-organizacional/lotacoes?page=0&size=5")
js = requests.get("https://cmcuritiba.eloweb.net/portaltransparencia/static/js/main.0d4cf918.chunk.js", timeout=90).text
for pat in ("SERVIDORES_LIST", "mesCompetencia", "tipoEvento", "headers"):
    for m in list(re.finditer(pat, js))[:2]:
        print("##", pat, js[max(0, m.start() - 300): m.start() + 500].replace("\n", " ")); print()
