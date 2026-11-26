"""Sonda temporária: JSON das emendas estaduais de Alagoas."""
import sys, re, json, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
B = "https://transparencia.al.gov.br/despesa/json-emendas-parlamentares/"
for q in ["", "?ano=2025", "?exercicio=2025", "?ano=2025&limit=5&offset=0"]:
    r = gbr(B + q, headers={**H, "accept": "application/json", "x-requested-with": "XMLHttpRequest"}, timeout=90)
    t = r.text if r is not None else ""
    print("Q", q, r.status_code if r is not None else None, len(t), t[:900].replace("\n", " "), flush=True)
    try:
        j = r.json(); L = j.get("rows") or j.get("data") or j if isinstance(j, (dict, list)) else []
        L = L if isinstance(L, list) else []
        print("N", q, len(L), j.get("total") if isinstance(j, dict) else "", list(L[0].keys()) if L else "", flush=True)
        if L:
            for k in L[0]:
                if re.search(r"autor|parlam|munic|ano|exerc", k, re.I): print("TOP", k, collections.Counter(str(x.get(k)) for x in L).most_common(5), flush=True)
            break
    except Exception as e: print("ERR", repr(e)[:100])
