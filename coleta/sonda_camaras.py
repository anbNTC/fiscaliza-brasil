"""Procura Câmaras Municipais com SAPL público (sapl.<cidade>.<uf>.leg.br) e mede o que cada uma tem desde 2025.
Saída: site/data/_sonda/camaras_sapl.json"""
import json, re, sys, unicodedata, concurrent.futures as cf
from pathlib import Path
import requests
D = Path(__file__).resolve().parents[1] / "site" / "data"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json"}
slug = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())
import os
PADROES = os.environ.get("PADROES", "https://sapl.{s}.{u}.leg.br").split()
def testa(a):
    for pd in PADROES:
        x = testa1(a, pd.format(s=slug(a[2]), u=a[0].lower()) + "/api")
        if x: return x
def testa1(a, b):
    uf, ue, nome, nver = a
    try:
        r = requests.get(f"{b}/materia/materialegislativa/", params={"ano": 2025, "page_size": 1}, headers=H, timeout=12)
        if r.status_code != 200 or "json" not in r.headers.get("content-type", ""): return None
        mat = r.json().get("pagination", {}).get("total_entries")
        v = requests.get(f"{b}/sessao/votoparlamentar/", params={"page_size": 1, "o": "-id"}, headers=H, timeout=12).json()
        vt = v.get("pagination", {}).get("total_entries"); ult = (v.get("results") or [{}])[0].get("data_hora")
        return {"uf": uf, "ue": ue, "nome": nome, "base": b[:-4], "materias2025": mat, "votos": vt, "ultimo_voto": ult, "vereadores_tse": nver}
    except Exception: return None
alvos = []
for f in sorted((D / "uf").glob("*.json")):
    U = json.load(open(f))
    for ue, m in U.get("mun", {}).items(): alvos.append((f.stem, ue, m[0], len(m[3])))
print(len(alvos), "cidades", flush=True)
with cf.ThreadPoolExecutor(96) as ex: R = [x for x in ex.map(testa, alvos) if x]
R.sort(key=lambda x: -(x["vereadores_tse"] or 0))
(D / "_sonda").mkdir(exist_ok=True); json.dump(R, open(D / "_sonda" / "camaras_sapl.json", "w"), ensure_ascii=False, indent=0)
print(len(R), "com SAPL;", sum(1 for x in R if x["materias2025"]), "com matérias de 2025;", sum(1 for x in R if x["votos"]), "com votos nominais")
for x in R[:120]: print(x["uf"], x["nome"], x["vereadores_tse"], x["materias2025"], x["votos"], (x["ultimo_voto"] or "")[:10])
