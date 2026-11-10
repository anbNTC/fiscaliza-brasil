"""Sonda (temporária): parâmetros da API de servidores do portal Elotech."""
import requests, re
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0", "accept": "application/json"}
B = "https://cmcuritiba.eloweb.net"
js = requests.get(B + "/portaltransparencia/static/js/main.0d4cf918.chunk.js", headers=H, timeout=90).text
for pat in ("api/servidores/", "api/servidores/verbas/", "api/estrutura-organizacional/lotacoes/", "api/exercicios/entidade/", "api/entidades/"):
    for m in list(re.finditer(re.escape(pat), js))[:3]:
        print("##", pat, js[max(0, m.start() - 350): m.start() + 450].replace("\n", " ")); print()
for u in ("/portaltransparencia-api/api/entidades/", "/portaltransparencia-api/api/exercicios/entidade/1", "/portaltransparencia-api/api/servidores/situacoes",
          "/portaltransparencia-api/api/servidores/?entidade=1&exercicio=2026&mes=9&page=0&size=3",
          "/portaltransparencia-api/api/servidores/?entidade=1&exercicio=2026&page=0&size=3"):
    try:
        r = requests.get(B + u, headers=H, timeout=60); print("==", u, r.status_code, r.text[:900])
    except Exception as e: print(u, e)
