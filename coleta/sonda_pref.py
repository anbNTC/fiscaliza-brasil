"""Sonda temporária: lista de servidores pela API Elotech (Maringá)."""
import sys, re, requests, json
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
B = "https://maringa.oxy.elotech.com.br/portaltransparencia-api"
def g(u):
    for f in (lambda: requests.get(u, headers={**H, "accept": "application/json"}, timeout=40), lambda: gbr(u, headers={**H, "accept": "application/json"}, timeout=60)):
        try:
            r = f()
            if r is not None and r.ok: return r
            print("  st", r.status_code if r is not None else None, (r.text[:120] if r is not None else ""), flush=True)
        except Exception as e: print("  err", repr(e)[:100], flush=True)
for p in ["/api/exercicios", "/api/exercicios?entidade=1", "/api/entidades/1/exercicios", "/api/configuracoes/exercicios"]:
    r = g(B + p); print("EX", p, (r.text[:400] if r is not None else None), flush=True)
    if r is not None: break
for q in ["entidade=1&exercicio=2026&page=0&size=3", "entidade=1&exercicio=2026&page=0&size=3&lotacao=GABINETE", "entidade=1&exercicio=2026&page=0&size=3&search=GABINETE DO PREFEITO"]:
    r = g(B + "/api/servidores?" + q); print("SV", q, (r.text[:1500] if r is not None else None), flush=True)
