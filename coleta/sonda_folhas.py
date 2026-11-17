"""Sonda temporária: API de remuneração da Paraíba (órgãos e filtro por órgão)."""
import sys, json, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
A = "https://api.dadosabertos.codata.pb.gov.br/api/v1/remuneracao/"
for mes in (10, 9, 8):
    r = requests.get(A + "orgaos", params={"ano": 2026, "mes": mes}, headers=H, timeout=60)
    print("ORG", mes, r.status_code, r.text[:300].replace("\n", " "), flush=True)
    if r.ok and len(r.text) > 50: break
try:
    j = r.json(); L = j.get("data") or j.get("items") or j if isinstance(j, (list, dict)) else []
    L = L if isinstance(L, list) else L.get("data", [])
    print("GOV", [x for x in L if "GOVERN" in json.dumps(x, ensure_ascii=False).upper() or "CASA CIVIL" in json.dumps(x, ensure_ascii=False).upper()][:6], flush=True)
except Exception as e: print("ERRO", repr(e)[:200])
r = requests.get(A + "servidor", params={"ano": 2026, "mes": mes, "page": 1, "per_page": 3}, headers=H, timeout=60)
print("SERV", r.status_code, r.text[:1200].replace("\n", " "), flush=True)
