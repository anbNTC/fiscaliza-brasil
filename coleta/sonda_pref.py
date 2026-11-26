"""Sonda temporária: parâmetros da lista de servidores Elotech."""
import sys, re, requests, json
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://maringa.oxy.elotech.com.br/portaltransparencia-api"
s = requests.get("https://maringa.oxy.elotech.com.br/portaltransparencia/static/js/main.ad8f87f3.chunk.js", headers=H, timeout=60).text
print("EXJS", sorted(set(re.findall(r'"(/api/[\w/-]*exercici[\w/?=-]*)', s)))[:10], flush=True)
j = s.find("SERVIDORES_OXY_LIST")
for k in [m.start() for m in re.finditer(r"\bkl\(", s)][:4]: print("KL", s[max(0, k - 900):k + 200].replace("\n", " "), flush=True)
r = requests.get(B + "/api/servidores?entidade=1&exercicio=2026&page=0&size=3", headers={**H, "accept": "application/json"}, timeout=40)
print("ERR", r.text[:800], flush=True)
