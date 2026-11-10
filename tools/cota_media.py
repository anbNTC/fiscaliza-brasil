"""Gera data/cota_media.json (médias da cota por Casa) ."""
import json, re, unicodedata, statistics
from pathlib import Path
from collections import defaultdict
D = Path(__file__).resolve().parents[1] / 'site' / 'data'; S = Path(__file__).resolve().parents[1] / 'site'
norm = lambda s: re.sub(r"[^A-Z ]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()).strip()
out = {}
for casa, pasta in (("C", "c"), ("S", "s")):
    tot = []
    for f in (D / pasta).glob('*.json'):
        for k, v in json.load(open(f)).items():
            c = v.get('cota')
            if c and c.get('a'):
                tot.append(sum(sum(x.values()) for x in c['a'].values()))
    out[casa] = {"n": len(tot), "media": round(statistics.mean(tot)), "mediana": round(statistics.median(tot)), "p90": round(sorted(tot)[int(len(tot) * .9)])}
json.dump(out, open(D / 'cota_media.json', 'w'))
print(out)
