"""Servidores dos gabinetes dos vereadores, com cargo e remuneração, nos portais de transparência da Elotech (eloweb.net).
É o sistema de transparência de muitas Câmaras Municipais (Curitiba e outras). A API é pública e é a mesma que o próprio portal usa.
Lista de portais: coleta/elotech_portais.json [{"host", "uf", "ue" (código TSE da cidade)}]; a entidade "Câmara" é achada sozinha.
Saída: site/data/gabm/{ue}.json {"fonte", "url", "gerado", "dep": {índice do vereador em uf/{UF}.json: [[nome, cargo, desde, remuneração]]}, "outros": nº sem vereador}
Só servidores ativos lotados em gabinete de vereador ("GAB. VER." e parecidos)."""
import json, re, sys, time, datetime, unicodedata
from collections import defaultdict
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "gabm"; OUT.mkdir(exist_ok=True)
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json"}
HOJE = datetime.date.today()
GAB = re.compile(r"\bGAB(INETE)?\.?\s*(DO|DA|DE)?\s*(VER|VEREADOR|VEREADORA)\b|\bGAB\.?\s*VER\b|GABINETE\s+(DO|DA)\s+VEREADOR", re.I)

def get(host, path, ent=None, ex=None, tent=3):
    h = dict(H)
    if ent: h["entidade"] = str(ent)
    if ex: h["exercicio"] = str(ex)
    for k in range(tent):
        try:
            r = requests.get(f"https://{host}/portaltransparencia-api{path}", headers=h, timeout=90)
            if r.ok: return r.json()
            if r.status_code in (400, 404, 500): return None
        except Exception as e: print(host, path, repr(e)[:100], flush=True)
        time.sleep(4 * (k + 1))

def um(p, U):
    host = p["host"]; ents = get(host, "/api/entidades/") or []
    cam = [e for e in ents if e.get("id") == p.get("ent")] or [e for e in ents if e.get("tipo") == "L" or "CAMARA" in limpa(e.get("nome", ""))]
    if not cam: return None, "sem entidade Câmara"
    ent = cam[0]["id"]; ex = HOJE.year
    pessoas = []; pg = 0
    while True:
        j = get(host, f"/api/servidores?entidade={ent}&exercicio={ex}&page={pg}&size=200", ent, ex)
        if not j: break
        pessoas += j.get("content") or []
        if j.get("last", True) or pg > 60: break
        pg += 1; time.sleep(0.4)
    if not pessoas: return None, "API sem servidores"
    m = U["mun"].get(p["ue"]); vs = (m[3] or []) if m else []
    idx = {}
    for i, v in enumerate(vs):
        for nm in (v[0], v[1]): idx.setdefault(limpa(nm), i)
    toks = [(i, set(limpa(v[0]).split()) | set(limpa(v[1]).split())) for i, v in enumerate(vs)]
    def dono(lot):
        cands = re.findall(r"\(([^)]+)\)", lot) + [re.sub(r"^.*?\b(VER|VEREADOR|VEREADORA)\.?\s+", "", lot, flags=re.I)]
        for c in cands:
            c = limpa(c)
            if c in idx: return idx[c]
        t = set(limpa(cands[-1]).split())
        best = sorted(((len(t & q), i) for i, q in toks), reverse=True)
        if best and best[0][0] >= 2 and (len(best) < 2 or best[1][0] < best[0][0]): return best[0][1]
    dep = defaultdict(list); outros = 0; ativos = 0; lots = defaultdict(int)
    for s in pessoas:
        if (s.get("situacao") or "").upper() != "ATIVO": continue
        lot = s.get("descricaoLotacao") or ""
        lots[lot] += 1
        if re.match(r"^\s*VEREADOR", s.get("descricaoCargo") or "", re.I): continue  # o próprio vereador
        if GAB.search(lot): i = dono(lot)
        else:  # algumas Câmaras usam o nome do vereador como lotação (ex.: Petrópolis)
            i = idx.get(limpa(lot)); 
            if i is None: continue
        ativos += 1
        if i is None: outros += 1; continue
        dep[str(i)].append([(s.get("nome") or "").title(), (s.get("descricaoCargo") or "").strip().capitalize(), s.get("dataAdmissao") or "", round(float(s.get("remuneracao") or 0), 2)])
    for v in dep.values(): v.sort(key=lambda r: -r[3])
    out = {"fonte": f"Portal da Transparência da Câmara Municipal ({host}) · servidores", "url": f"https://{host}/portaltransparencia/{ent}/servidores",
           "gerado": HOJE.isoformat(), "dep": dep, "outros": outros,
           "obs": "Remuneração como publicada no portal da Câmara (valor do cargo, sem descontos). Só servidores ativos lotados em gabinete de vereador."}
    json.dump(out, open(OUT / f"{p['ue']}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return {"servidores": len(pessoas), "gabinetes": len(dep), "pessoas_em_gabinete": ativos, "sem_vereador": outros,
            "lotacoes": [k for k, _ in sorted(lots.items(), key=lambda z: -z[1])[:6]] if not dep else []}, None

def main():
    P = json.load(open(Path(__file__).resolve().parent / "elotech_portais.json")); res = {}; UF = {}
    for p in P:
        if p["uf"] not in UF: UF[p["uf"]] = json.load(open(D / "uf" / f"{p['uf']}.json"))
        try: r, err = um(p, UF[p["uf"]])
        except Exception as e: r, err = None, repr(e)[:120]
        res[p["host"]] = r or err; print(p["host"], r or err, flush=True)
    ok = sum(1 for v in res.values() if isinstance(v, dict))
    print(json.dumps({"portais": len(P), "com_dados": ok}))

if __name__ == "__main__":
    main()
