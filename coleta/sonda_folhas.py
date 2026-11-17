"""Sonda temporária: unidades da Secretaria de Governo, Casa Militar e Vice-Governadoria da Paraíba (09/2026)."""
import sys, json, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
A = "https://api.dadosabertos.codata.pb.gov.br/api/v1/remuneracao/servidor"
for cnpj in ("08761124000100", "08761124000363", "08761124000282"):
    L = []; p = 1
    while True:
        r = requests.get(A, params={"ano": 2026, "mes": 9, "cnpjOrgao": cnpj, "page": p, "per_page": 500}, headers=H, timeout=90).json()
        L += r["dados"]; pg = r["paginacao"]
        if p >= pg["total_paginas"] or p > 30: break
        p += 1
    print("ORG", cnpj, len(L), pg["total"], collections.Counter(x["orgaoLotacao"] for x in L).most_common(3), flush=True)
    print("UNI", cnpj, collections.Counter(x["nomeUnidadeTrabalho"] for x in L).most_common(25), flush=True)
    print("CHEFE", cnpj, [(x["nomeServidor"], x["nomeCargo"], x["nomeUnidadeTrabalho"], x["valorBruto"]) for x in L if "GOVERNADOR" in (x["nomeCargo"] or "").upper()][:6], flush=True)
