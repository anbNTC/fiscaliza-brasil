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
PREF = re.compile(r"GAB(INETE)?\.?\s*(DO|DA)?\s*(VICE[\s-]*)?PREFEIT|VICE[\s-]*PREFEIT|GABINETE\s+DO\s+PREFEITO", re.I)
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

def servidores(host, ent):
    ex = HOJE.year; pessoas = []; pg = 0
    while True:
        j = get(host, f"/api/servidores?entidade={ent}&exercicio={ex}&page={pg}&size=200", ent, ex)
        if not j: break
        pessoas += j.get("content") or []
        if j.get("last", True) or pg > 250: break
        pg += 1; time.sleep(0.3)
    return pessoas

def prefeitura(p):
    """Gabinete do prefeito e do vice: servidores ativos lotados nesses gabinetes."""
    host = p.get("host_pref") or p["host"]; ent = p.get("pref")
    if not ent: return None
    out = {"p": [], "v": []}
    for s in servidores(host, ent):
        if (s.get("situacao") or "").upper() != "ATIVO": continue
        lot = s.get("descricaoLotacao") or ""; cg = s.get("descricaoCargo") or ""
        if not PREF.search(lot) or re.match(r"^\s*(VICE[\s-]*)?PREFEIT", cg, re.I): continue
        k = "v" if re.search(r"VICE", lot, re.I) else "p"
        out[k].append([(s.get("nome") or "").title(), cg.strip().capitalize(), s.get("dataAdmissao") or "", round(float(s.get("remuneracao") or 0), 2)])
    for v in out.values(): v.sort(key=lambda r: -r[3])
    return {k: v for k, v in out.items() if v}, host, ent

def um(p, U):
    if not p.get("ent"): return {}, None
    host = p["host"]; ents = get(host, "/api/entidades/") or []
    cam = [e for e in ents if e.get("id") == p.get("ent")] or [e for e in ents if e.get("tipo") == "L" or "CAMARA" in limpa(e.get("nome", ""))]
    if not cam: return None, "sem entidade Câmara"
    ent = cam[0]["id"]
    pessoas = servidores(host, ent)
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
    out["_tipo"] = "camara"; grava(p["ue"], out)
    return {"servidores": len(pessoas), "gabinetes": len(dep), "pessoas_em_gabinete": ativos, "sem_vereador": outros,
            "lotacoes": [k for k, _ in sorted(lots.items(), key=lambda z: -z[1])[:6]] if not dep else []}, None

def grava(ue, novo):
    """Junta Câmara e Prefeitura no mesmo arquivo da cidade."""
    f = OUT / f"{ue}.json"
    try: X = json.load(open(f))
    except Exception: X = {"dep": {}}
    velho = X.get("dep") or {}
    if novo["_tipo"] == "camara": dep = {k: v for k, v in velho.items() if k in ("p", "v")}   # troca os vereadores, mantém prefeito/vice
    else: dep = {k: v for k, v in velho.items() if k not in ("p", "v")}                        # troca prefeito/vice, mantém vereadores
    if novo.get("_tipo") == "camara": X.update({k: v for k, v in novo.items() if k not in ("dep", "_tipo")})
    if novo.get("_tipo") == "pref": X["pref"] = {k: v for k, v in novo.items() if k not in ("dep", "_tipo")}
    dep.update(novo["dep"]); X["dep"] = dep; X["gerado"] = HOJE.isoformat()
    json.dump(X, open(f, "w"), ensure_ascii=False, separators=(",", ":"))

def main():
    P = json.load(open(Path(__file__).resolve().parent / "elotech_portais.json")); res = {}; UF = {}
    for p in P:
        if p["uf"] not in UF: UF[p["uf"]] = json.load(open(D / "uf" / f"{p['uf']}.json"))
        try: r, err = um(p, UF[p["uf"]])
        except Exception as e: r, err = None, repr(e)[:120]
        try:
            pr = prefeitura(p)
            if pr and pr[0]:
                grava(p["ue"], {"_tipo": "pref", "dep": pr[0], "fonte": f"Portal da Transparência da Prefeitura ({pr[1]}) · servidores", "url": f"https://{pr[1]}/portaltransparencia/{pr[2]}/servidores",
                                "obs": "Remuneração como publicada no portal da Prefeitura (valor do cargo, sem descontos). Só servidores ativos lotados no gabinete do prefeito ou do vice."})
                r = dict(r or {}); r["prefeitura"] = {k: len(v) for k, v in pr[0].items()}
        except Exception as e: print(p["host"], "prefeitura falhou", repr(e)[:100])
        res[p["host"]] = r or err; print(p["host"], r or err, flush=True)
    ok = sum(1 for v in res.values() if isinstance(v, dict))
    print(json.dumps({"portais": len(P), "com_dados": ok}))

if __name__ == "__main__":
    main()
