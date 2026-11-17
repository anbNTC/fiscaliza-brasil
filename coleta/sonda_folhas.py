"""Sonda temporária: link do CSV de servidores de Curitiba e lotações do gabinete do prefeito e do vice."""
import sys, re, io, csv, html, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H, texto
B = "https://dadosabertos.curitiba.pr.gov.br"
d = html.unescape(requests.get(B + "/conjuntodado/detalhe?chave=CB9CBEB2-1C2C-48BA-A632-25EDCB766744", headers=H, timeout=40).text)
i = d.find("Servidores_Cargos_Encargos"); print("CTX", re.sub(r"\s+", " ", d[max(0, i - 900):i + 300]), flush=True)
us = sorted(set(re.findall(r'(?:href|data-\w+|onclick)="([^"]*(?:Servidores_Cargos|\.csv|download|arquivo)[^"]*)"', d, re.I)))
print("URLS", us[:10], flush=True)
u = next((x for x in us if "Servidores_Cargos" in x or ".csv" in x.lower()), None)
if u:
    u = u if u.startswith("http") else B + ("" if u.startswith("/") else "/") + u
    b = requests.get(u, headers=H, timeout=600).content; t = texto(b); del b
    rows = list(csv.DictReader(io.StringIO(t), delimiter=";" if t[:3000].count(";") > t[:3000].count(",") else ","))
    print("N", len(rows), list(rows[0].keys()), flush=True)
    lot = collections.Counter(r["LOTACAO"] for r in rows)
    print("LOT", len(lot), [x for x in lot.items() if re.search(r"GABINETE|PREFEIT|GOVERNO|VICE", x[0])][:20], flush=True)
    print("CHEFE", sorted({(r["NOME"], r["CARGO"], r["CARGO_COMISSAO"], r["LOTACAO"]) for r in rows if re.search(r"^(VICE-?)?PREFEITO", r["CARGO"] + " " + r["CARGO_COMISSAO"])})[:6], flush=True)
    print("EVENTOS", collections.Counter(r["TIPO_EVENTO"] for r in rows).most_common(4), len({r["NOME"] for r in rows}), flush=True)
