"""Sonda temporária: campos e órgãos da API de remuneração da Paraíba (09/2026)."""
import sys, json, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
A = "https://api.dadosabertos.codata.pb.gov.br/api/v1/remuneracao/"
r = requests.get(A + "servidor", params={"ano": 2026, "mes": 9, "page": 1, "per_page": 1}, headers=H, timeout=60).json()
print("REC", json.dumps({k: (v if "cpf" not in k.lower() else "...") for k, v in r["dados"][0].items()}, ensure_ascii=False), r["paginacao"], flush=True)
o = requests.get(A + "orgaos", params={"ano": 2026, "mes": 9}, headers=H, timeout=60).json()
print("ORGS", json.dumps(o, ensure_ascii=False)[:600], flush=True)
txt = json.dumps(o, ensure_ascii=False)
import re
print("GOV", re.findall(r'\{[^{}]*(?:GOVERN|CASA CIVIL|VICE)[^{}]*\}', txt)[:8], flush=True)
