"""Sonda temporária: lista de servidores Elotech com os cabeçalhos certos."""
import sys, re, requests, json, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://maringa.oxy.elotech.com.br/portaltransparencia-api"
ex = requests.get(B + "/api/exercicios/entidade/1", headers={**H, "accept": "application/json", "entidade": "1"}, timeout=40).json()
print("EX", json.dumps(ex, ensure_ascii=False)[:500], flush=True)
eid = next((x.get("id") for x in (ex if isinstance(ex, list) else ex.get("content", [])) if str(x.get("ano") or x.get("exercicio")) == "2026"), 2026)
hd = {**H, "accept": "application/json", "entidade": "1", "exercicio": str(eid)}
r = requests.get(B + f"/api/servidores?entidade=1&exercicio={eid}&page=0&size=3", headers=hd, timeout=60)
print("SV", r.status_code, r.text[:1800], flush=True)
