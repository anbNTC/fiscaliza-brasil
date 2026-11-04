"""Gera data/cota_media.json (médias da cota por Casa) e data/emendas_pr.json (emendas dos parlamentares do PR por cidade)."""
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
s = open(S / 'parana.html').read()
d = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', s, re.S).group(1))
cid = defaultdict(list)
for p in d['P']:
    if p['casa'] not in ('C', 'S'): continue
    for m, uf, tot, fav in p.get('fav') or []:
        if uf != 'PR' or not tot: continue
        cid[norm(m)].append([p['casa'], str(p['id']), p['nome'], p['partido'], round(tot), [[a, round(b)] for a, b in fav[:3]]])
for k in cid: cid[k].sort(key=lambda x: -x[4])
json.dump({"gerado": d.get("gerado"), "fonte": "Portal da Transparência (CGU) · Emendas parlamentares por favorecido, 2023 a 2026", "cid": cid}, open(D / 'emendas_pr.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(cid), 'cidades', (D / 'emendas_pr.json').stat().st_size // 1024, 'KB', cid.get('CURITIBA', [])[:2])
