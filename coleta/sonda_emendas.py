"""Sonda temporária: colunas das emendas parlamentares estaduais do Espírito Santo (dados.es.gov.br)."""
import sys, csv, io, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
r = requests.get("https://dados.es.gov.br/api/3/action/package_show?id=portal-da-transparencia-emendas-parlamentares-do-estado", headers=H, timeout=60).json()["result"]
for x in r["resources"]: print("RES", x["name"], "|", x.get("format"), "|", x["url"], flush=True)
from collections import Counter
for nome in ("Emendas-Estaduais-2025.csv", "Emendas-Estaduais-Execucao-2025.csv"):
    u = next(x["url"] for x in r["resources"] if x["name"] == nome)
    b = requests.get(u, headers=H, timeout=300).content
    try: t = b.decode("utf-8-sig")
    except UnicodeDecodeError: t = b.decode("latin-1")
    sep = ";" if t[:2000].count(";") >= t[:2000].count(",") else ","
    rd = list(csv.DictReader(io.StringIO(t), delimiter=sep))
    print("COLS", nome, len(rd), list(rd[0].keys()), flush=True)
    for row in rd[:2]: print("ROW", nome, dict(row), flush=True)
    for c in rd[0]:
        if any(k in c.lower() for k in ("autor", "parlament", "deput", "munic", "benef")): print("TOP", nome, c, Counter(x[c] for x in rd).most_common(5), flush=True)
