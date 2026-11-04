"""Gera data/semana.json: resumo das últimas 4 semanas com votações no Plenário (Câmara e Senado)."""
import json, datetime
from pathlib import Path
from collections import defaultdict
D = Path(__file__).resolve().parents[1] / 'site' / 'data'
BR = json.load(open(D / 'br.json')); VC = json.load(open(D / 'camara_votacoes.json')); VS = json.load(open(D / 'senado_votacoes.json'))
PT = json.load(open(D / 'partidos.json'))
dep = {}; [dep.update(json.load(open(f))) for f in (D / 'c').glob('*.json')]
sen = {}; [sen.update(json.load(open(f))) for f in (D / 's').glob('*.json')]
info = {str(d[0]): ("C", d[1], d[2], d[3]) for d in BR['dep']}; info.update({str(s[0]): ("S", s[1], s[3], s[4]) for s in BR['sen']})
seg = lambda d: (datetime.date.fromisoformat(d) - datetime.timedelta(days=datetime.date.fromisoformat(d).weekday())).isoformat()
sem = defaultdict(lambda: {"c": [], "s": []})
for i, v in enumerate(VC): sem[seg(v[1])]["c"].append(i)
for i, v in enumerate(VS): sem[seg(v[1])]["s"].append(i)
out = []
for w in sorted(sem)[-4:][::-1]:
    ci, si = sem[w]["c"], sem[w]["s"]
    falt, contra = [], []
    for casa, idx, base, pos in (("C", ci, dep, PT['cam']), ("S", si, sen, PT['sen'])):
        if not idx: continue
        for k, x in base.items():
            if k not in info: continue
            v = x.get('v', ''); pres = x.get('pres') or [0, 0]
            first = len(v) - pres[1] if pres[1] else len(v)
            valid = [i for i in idx if i >= first]
            if not valid: continue
            aus = sum(1 for i in valid if v[i] == '-')
            ok = [i for i in valid if v[i] != '-' and v[i] not in 'V']
            p = pos.get(info[k][2], '')
            c = sum(1 for i in valid if v[i] in 'SN' and i < len(p) and p[i] in 'SN' and v[i] != p[i])
            if aus: falt.append([casa, k, info[k][1], info[k][2], info[k][3], aus, len(valid)])
            if c: contra.append([casa, k, info[k][1], info[k][2], info[k][3], c])
    falt.sort(key=lambda x: (-x[5] / x[6], -x[5])); contra.sort(key=lambda x: -x[5])
    out.append({"seg": w, "c": ci, "s": si, "falt": falt[:12], "contra": contra[:10],
                "aprov": sum(1 for i in ci if VC[i][2] == "1") + sum(1 for i in si if VS[i][5] == "A"),
                "rej": sum(1 for i in ci if VC[i][2] == "0") + sum(1 for i in si if VS[i][5] == "R")})
json.dump({"gerado": BR.get("gerado"), "semanas": out}, open(D / 'semana.json', 'w'), ensure_ascii=False, separators=(',', ':'))
for s in out: print(s['seg'], len(s['c']), len(s['s']), s['falt'][:2], s['contra'][:2])
