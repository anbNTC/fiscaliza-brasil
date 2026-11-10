"""Emendas de cada deputado federal e senador, juntando as cidades de todos os estados (a partir de site/data/emendas/{UF}.json).
Saída: site/data/emendas/aut_{UF}.json, com UF = estado do parlamentar:
  {"fonte", "dep": {"C:id"|"S:id": {"t": total pago, "n": nº de cidades, "c": [[UF, cidade, valor, [[favorecido, valor] x3], código TSE da cidade] x40], "f": [[favorecido, valor] x10]}}}"""
import json
from collections import defaultdict
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "site" / "data"; E = D / "emendas"
BR = json.load(open(D / "br.json"))
ufde = {"C:" + str(d[0]): d[3] for d in BR["dep"]}; ufde.update({"S:" + str(s[0]): s[4] for s in BR["sen"]})
import re, unicodedata
norm = lambda s: re.sub(r"[^A-Z ]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()).strip()
MUN = {}
for f in (D / "uf").glob("*.json"):
    for ue, m in (json.load(open(f)).get("mun") or {}).items(): MUN[(f.stem, norm(m[0]))] = (m[0], ue)
MUN.setdefault(("DF", "BRASILIA"), ("BRASÍLIA", ""))
cid = defaultdict(list); fav = defaultdict(lambda: defaultdict(float)); tot = defaultdict(float)
for f in sorted(E.glob("??.json")):
    uf = f.stem; X = json.load(open(f))
    for m, L in (X.get("cid") or {}).items():
        for a in L:
            if a[0] not in ("C", "S"): continue
            k = a[0] + ":" + str(a[1]); tot[k] += a[4]; nm_ue = MUN.get((uf, m)); cid[k].append([uf, nm_ue[0] if nm_ue else m, a[4], a[5], nm_ue[1] if nm_ue else ""])
            for nm, v in a[5]: fav[k][nm] += v
out = defaultdict(dict)
for k, t in tot.items():
    uf = ufde.get(k)
    if not uf: continue
    cs = sorted(cid[k], key=lambda x: -x[2])
    out[uf][k] = {"t": round(t), "n": len(cs), "c": cs[:40], "f": [[n, round(v)] for n, v in sorted(fav[k].items(), key=lambda x: -x[1])[:10]]}
for uf, dep in out.items():
    json.dump({"fonte": "Portal da Transparência (CGU) · Emendas parlamentares por favorecido, desde 2023", "dep": dep}, open(E / f"aut_{uf}.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("emendas por autor:", sum(len(d) for d in out.values()), "parlamentares em", len(out), "estados")
