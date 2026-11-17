"""Sonda temporária: meses com dados na API de remuneração da Paraíba."""
import sys, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
A = "https://api.dadosabertos.codata.pb.gov.br/api/v1/remuneracao/"
for ano, mes in [(2026, m) for m in range(9, 0, -1)] + [(2025, 12)]:
    r = requests.get(A + "servidor", params={"ano": ano, "mes": mes, "page": 1, "per_page": 1}, headers=H, timeout=60)
    print("MES", ano, mes, r.status_code, r.text[:160].replace("\n", " "), flush=True)
