"""Sonda temporária: onde estão o governador, o vice e as suas equipes nas folhas abertas de MG e SC; e o download completo do arquivo do Recife."""
import csv, io, re, sys, requests
from collections import Counter
sys.path.insert(0, "coleta")
from prefeituras_abertas import recente, baixa
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}

def linhas(url):
    b = baixa(url); print("bytes:", len(b) if b else None, flush=True)
    if not b: return [], []
    t = b.decode("utf-8-sig", "ignore") if b"\xc3" in b[:300000] else b.decode("latin-1")
    sep = ";" if t[:3000].count(";") > t[:3000].count(",") else ","
    rd = csv.reader(io.StringIO(t), delimiter=sep); cab = next(rd); return cab, rd

for nome, ckan, pac in [("MG", "https://dados.mg.gov.br", "remuneracao-servidores-ativos"), ("SC", "https://dados.sc.gov.br", "remuneracao-servidores")]:
    print("\n########", nome, flush=True)
    j = requests.get(f"{ckan}/api/3/action/package_show", params={"id": pac}, headers=H, timeout=60).json()["result"]
    r = recente([x for x in j["resources"] if not re.search(r"inativ|pension", (x.get("name") or "") + (x.get("url") or ""), re.I)])
    print("arquivo:", r.get("name"), r.get("url"))
    cab, rd = linhas(r["url"]); print(cab)
    org = Counter(); chefes = []; n = 0
    for row in rd:
        n += 1; d = dict(zip(cab, row)); txt = " | ".join(row)
        o = d.get("orgao_exercicio") or d.get("OrgaoExercicio") or ""; u = d.get("unidade_exercicio") or d.get("UnidadeExercicio") or ""
        if re.search(r"GOVERNADORI|GABINETE DO GOVERNADOR|VICE-GOVERNADOR|SECRETARIA-GERAL|SECRETARIA GERAL|CASA CIVIL|GABINETE DO VICE", o + " " + u, re.I): org[(o, u)] += 1
        if re.search(r"\b(VICE-)?GOVERNADOR DO ESTADO\b", (d.get("cargo_comissao") or "") + (d.get("Cargo") or ""), re.I): chefes.append({k: v for k, v in d.items() if k in ("nome", "Nome", "orgao_exercicio", "unidade_exercicio", "OrgaoExercicio", "UnidadeExercicio", "cargo_comissao", "Cargo", "remuneracao", "ValorBruto")})
    print("linhas", n); print("chefes:", chefes)
    for (o, u), c in org.most_common(40): print("  ", c, "|", o, "|", u)
    sys.stdout.flush()

print("\n######## Recife (download completo)")
j = requests.get("https://dados.recife.pe.gov.br/api/3/action/package_show", params={"id": "servidores"}, headers=H, timeout=60).json()["result"]
r = recente(j["resources"]); print(r.get("name"))
cab, rd = linhas(r["url"]); print(cab)
lot = Counter(); meses = Counter(); n = 0
for row in rd:
    n += 1; d = dict(zip(cab, row)); meses[(d.get("asalseanoo"), d.get("asalsemess"))] += 1
    l = (d.get("esalseunidade") or "") + " · " + (d.get("eslserlotacao") or "")
    if re.search(r"GAB|PREFEIT", l, re.I): lot[l] += 1
print("linhas", n, "meses", sorted(meses.items())[-3:])
for l, c in lot.most_common(25): print("  ", c, l)
