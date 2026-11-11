"""Sonda temporária: Porto Alegre (lotação do gabinete) e Vitória (links da página de pessoal)."""
import csv, io, re, sys, requests
from collections import Counter
sys.path.insert(0, "coleta")
from saida_br import get
from prefeituras_abertas import texto, H
b = requests.get("https://dadosabertos.poa.br/dataset/7fd4117c-a972-4b1a-a2c1-a2b7e56f8f26/resource/140bd4c0-5e3f-4ec8-8656-856ed28a21db/download/servidores_ativos.csv", headers=H, timeout=300).content
t = texto(b); sep = ";" if t[:3000].count(";") > t[:3000].count(",") else ","
rd = csv.DictReader(io.StringIO(t), delimiter=sep); orig = Counter(); car = Counter(); comp = Counter()
for r in rd:
    comp[r.get("competencia")] += 1
    if re.search(r"PREFEIT|GABINETE", r.get("nome_cargo") or "", re.I): car[(r.get("origem"), r.get("empresa"), r.get("nome_cargo"))] += 1
    orig[r.get("origem")] += 1
print("competências:", comp.most_common(3)); print("origens:", orig.most_common(60))
for k, v in car.most_common(30): print("  ", v, k)
print("\n#### Vitória")
for u in ["https://transparencia.vitoria.es.gov.br/Pessoal.aspx", "https://transparencia.vitoria.es.gov.br/", "https://transparencia.vitoria.es.gov.br/DadosAbertos.aspx"]:
    r = get(u, headers={"accept": "text/html"}, timeout=90, tentativas=1)
    if r is None: print(u, "sem resposta"); continue
    print("==", u, r.status_code)
    for m in sorted(set(re.findall(r'href="([^"#]+)"', r.text)))[:80]: print("   ", m[:160])
