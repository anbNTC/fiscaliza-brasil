"""Quem trabalha no gabinete de cada deputado federal (Câmara · Dados Abertos, arquivo de funcionários).
Fonte: https://dadosabertos.camara.leg.br/arquivos/funcionarios/csv/funcionarios.csv (lotação ligada ao deputado).
Saída: site/data/gab/{UF}.json {"fonte", "gerado", "dep": {id: [[nome, cargo ou função, desde], ...]}}
O próprio deputado (grupo "Parlamentar") não entra. O arquivo não traz salário: só o cargo, cuja tabela é pública na Câmara."""
import csv, io, json, re, datetime
from collections import defaultdict
from pathlib import Path
import requests
D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "gab"; OUT.mkdir(exist_ok=True)
URL = "https://dadosabertos.camara.leg.br/arquivos/funcionarios/csv/funcionarios.csv"
t = requests.get(URL, headers={"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}, timeout=180).content.decode("utf-8-sig", "replace")
BR = json.load(open(D / "br.json")); uf = {str(d[0]): d[3] for d in BR["dep"]}
G = defaultdict(dict); n = 0
for r in csv.DictReader(io.StringIO(t), delimiter=";"):
    m = re.search(r"/deputados/(\d+)$", r.get("uriLotacao") or "")
    if not m or (r.get("grupo") or "").strip() == "Parlamentar" or m.group(1) not in uf: continue
    f = (r.get("funcao") or "").strip(); c = (r.get("cargo") or "").strip()
    cargo = re.sub(r"^[A-Z]{2,4}\d+\s*-\s*", "", f).title() if f else (r.get("grupo") or "").strip()
    if c and c not in cargo: cargo += f" ({c})"
    G[uf[m.group(1)]].setdefault(m.group(1), []).append([(r.get("nome") or "").strip().title(), cargo, r.get("dataNomeacao") or r.get("dataInicioHistorico") or ""]); n += 1
for u, deps in G.items():
    for k in deps: deps[k].sort(key=lambda x: x[0])
    json.dump({"fonte": "Câmara dos Deputados · Dados Abertos, funcionários (lotação nos gabinetes)", "url": URL, "gerado": datetime.date.today().isoformat(), "dep": deps},
              open(OUT / f"{u}.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(json.dumps({"funcionarios": n, "deputados": sum(len(v) for v in G.values()), "estados": len(G)}))
