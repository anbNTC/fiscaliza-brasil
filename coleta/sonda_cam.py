"""Sonda temporária: quantas câmaras com SAPL existem e quantas ainda não foram coletadas."""
import sys, json, concurrent.futures as cf, collections
sys.path.insert(0, "coleta")
import camaras_sapl as C
alvos = []
for f in sorted((C.D / "uf").glob("*.json")):
    U = json.load(open(f))
    for ue, m in U.get("mun", {}).items(): alvos.append((f.stem, ue, m[0]))
with cf.ThreadPoolExecutor(96) as ex: achou = [x for x in ex.map(C.sonda, alvos) if x]
ativas = [x for x in achou if x["mat"] or x["voto"]]
idx = json.load(open(C.OUT / "index.json"))
falta = [x for x in ativas if x["ue"] not in idx]
print("RES municípios", len(alvos), "| SAPL", len(achou), "| ativas", len(ativas), "| no índice", len(idx), "| faltam", len(falta), flush=True)
print("RES faltam por UF", collections.Counter(x["uf"] for x in falta).most_common(), flush=True)
print("RES maiores que faltam", sorted([(x["mat"], x["uf"], x["nome"]) for x in falta], reverse=True)[:25], flush=True)
velhas = sorted(idx.values(), key=lambda v: v[5])[:5]; print("RES mais antigas no índice", [(v[1], v[5]) for v in velhas], flush=True)
