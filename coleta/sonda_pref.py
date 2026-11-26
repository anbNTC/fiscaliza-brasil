"""Sonda temporária: gabinete do prefeito em Maringá (Elotech) e outras cidades no mesmo portal."""
import sys, re, json, requests, collections, concurrent.futures as cf
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
import camaras_sapl as C
B = "https://maringa.oxy.elotech.com.br/portaltransparencia-api"
hd = {**H, "accept": "application/json", "entidade": "1", "exercicio": "2026"}
L = []; p = 0
while True:
    j = requests.get(B + f"/api/servidores?page={p}&size=2000", headers=hd, timeout=120).json()
    L += j["content"]; p += 1
    if j.get("last", True) or p > 20: break
print("MGA", len(L), j.get("totalElements"), flush=True)
lot = collections.Counter(x["descricaoLotacao"] for x in L)
print("LOT", [x for x in lot.items() if re.search(r"GABINETE|PREFEIT|VICE", x[0] or "")][:25], flush=True)
print("CHEFE", [(x["nome"], x["descricaoCargo"], x["descricaoLotacao"], x["remuneracao"]) for x in L if re.search(r"^(VICE[- ])?PREFEIT", x["descricaoCargo"] or "")][:5], flush=True)
alvos = []
for f in sorted((C.D / "uf").glob("*.json")):
    for ue, m in json.load(open(f)).get("mun", {}).items():
        if len(m[3] or []) >= 13: alvos.append((f.stem, ue, m[0], len(m[3])))
def t(a):
    s = C.slug(a[2])
    for h in [f"https://{s}.oxy.elotech.com.br", f"https://{s}.eloweb.net"]:
        try:
            r = requests.get(h + "/portaltransparencia-api/api/entidades", headers={**H, "accept": "application/json"}, timeout=10)
            if r.ok and r.text.startswith("["):
                e = r.json()
                if e and (e[0].get("uf") or "").upper() == a[0]: return a + (h, [(x["id"], x["nome"][:40]) for x in e if re.search(r"PREFEITURA|MUNICIPIO", x["nome"])][:2])
        except Exception: pass
with cf.ThreadPoolExecutor(48) as ex: R = [x for x in ex.map(t, alvos) if x]
print("ELO", len(R), "de", len(alvos), flush=True)
for x in sorted(R, key=lambda x: -x[3]): print("CID", *x, flush=True)
