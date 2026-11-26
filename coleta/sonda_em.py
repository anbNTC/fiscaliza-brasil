"""Sonda temporária: paginação e filtro de ano do JSON de emendas de Alagoas."""
import sys, re, json, html, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
P = "https://transparencia.al.gov.br/despesa/emendas-parlamentares-estaduais/"
t = html.unescape(gbr(P, headers=H, timeout=90).text)
i = t.find("json-emendas-parlamentares"); print("JS", re.sub(r"\s+", " ", t[max(0, i - 1500):i + 1500]), flush=True)
print("FORM", re.findall(r'<(?:select|input)[^>]*name="([^"]+)"', t)[:20], flush=True)
B = "https://transparencia.al.gov.br/despesa/json-emendas-parlamentares/"
for q in ["?limit=1000&offset=0", "?ano=2025&limit=1000&offset=0", "?exercicio=2025&limit=1000"]:
    j = gbr(B + q, headers={**H, "accept": "application/json"}, timeout=120).json()
    print("Q", q, j.get("total"), len(j["rows"]), collections.Counter(x["ano"] for x in j["rows"]), flush=True)
