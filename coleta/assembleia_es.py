"""ALES (Espírito Santo): deputados e proposições desde fev/2023 pela API pública do SPL da Assembleia (/api/publico).
O site só responde a acessos do Brasil, então a coleta passa pela saída BR (coleta/saida_br.py).
Saída: site/data/est/ES.json no mesmo formato das outras Assembleias, com a presença em plenário por ano."""
import json, re, sys, time, datetime, concurrent.futures as cf
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa, norm
from saida_br import get

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "est"; OUT.mkdir(exist_ok=True)
API = "https://www3.al.es.gov.br/api/publico"; DESDE = "2023-02-01"
TIPOS = [(r"^PROJETO DE LEI COMPLEMENTAR", "PLC"), (r"^PROJETO DE LEI$", "PL"), (r"EMENDA (A|À) CONSTITUI|EMENDA CONSTITUCIONAL", "PEC"),
         (r"^PROJETO DE DECRETO LEGISLATIVO", "PDL"), (r"^PROJETO DE RESOLU", "PR"), (r"^INDICA", "IND"), (r"^REQUERIMENTO", "REQ")]
PROJ = {"PL", "PLC", "PEC", "PDL", "PR"}

def sig(nome):
    n = norm(nome)
    for p, s in TIPOS:
        if re.search(p, n): return s
    return None

def js(path, **p):
    r = get(f"{API}/{path}", p, timeout=180)
    try: return r.json() if r is not None and r.status_code == 200 else None
    except ValueError: return None

def data_iso(s):
    m = re.match(r"(\d\d)/(\d\d)/(\d{4})", s or ""); return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""

def coleta_dep(p):
    d = js("parlamentar/", parlamentarID=p["parlamentarID"]) or {}
    d = (d.get("parlamentares") or [d])[0] if d else {}
    aid = d.get("autorID"); cont = Counter(); props = []
    if aid:
        for t in d.get("porposicoesApresentadas") or []:
            s = sig(t.get("tipo"))
            if not s: continue
            j = js("proposicao/", autorID=aid, tipoID=t["tipoID"], dataInicio=DESDE, pag=1, qtd=100 if s in PROJ else 1) or {}
            n = int(j.get("total") or 0); cont[s] += n
            if s in PROJ:
                for x in j.get("Data") or []:
                    props.append([f"{x.get('sigla') or s} {x.get('numero')}/{x.get('ano')}", re.sub(r"\s+", " ", x.get("assunto") or "").strip()[:200],
                                  data_iso(x.get("data")), 1 if norm(x.get("situacao")) == "TRAMITANDO" else 0])
            time.sleep(0.2)
    pres = {}
    for f in d.get("frequenciaPlenario") or []:
        for a in f.get("frequenciaSituacaoAnos") or []:
            if a.get("ano", 0) >= 2023: pres.setdefault(str(a["ano"]), {})[f.get("frequenciaSituacaoNome")] = int(a.get("quantidade") or 0)
    return p["parlamentarID"], {"cont": dict(cont), "props": sorted(props, key=lambda x: x[2], reverse=True)[:80], "pres": pres, "aid": aid}

def main():
    parl = []; pg = 1
    while pg < 20:
        j = js("parlamentar/", parlamentarLegislatura=20, pag=pg, qtd=20, detalhes="false") or {}
        ps = j.get("parlamentares") or []; parl += ps
        if not ps or len(parl) >= int(j.get("total") or 0): break
        pg += 1
    print(len(parl), "deputados", flush=True)
    with cf.ThreadPoolExecutor(3) as ex: R = dict(ex.map(coleta_dep, parl))
    U = json.load(open(D / "uf" / "ES.json")); de = U.get("de22", [])
    idx = {}
    for k, x in enumerate(de): idx.setdefault(limpa(x[0]), k); idx.setdefault(limpa(x[1]), k)
    toks = [(k, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for k, x in enumerate(de)]
    dep = {}; sem = []
    for p in parl:
        r = R[p["parlamentarID"]]; k = None
        for n in (p.get("parlamentarRazaoSocial"), p.get("parlamentarNome")):
            if k is None: k = idx.get(limpa(n))
        if k is None:
            SUF = {"FILHO", "JUNIOR", "NETO", "SOBRINHO"}
            tt = (set(limpa(p.get("parlamentarRazaoSocial")).split()) | set(limpa(p.get("parlamentarNome")).split())) - SUF
            best = sorted(((len(tt & q) / max(1, min(len(tt), len(q))), len(tt & q), j) for j, q in toks), reverse=True)
            unico = len(best) < 2 or best[1][:2] < best[0][:2]
            if best and unico and (best[0][1] >= 2 and best[0][0] >= 0.6 or best[0][0] >= 0.99): k = best[0][2]
        reg = {"nome": p.get("parlamentarRazaoSocial") or p.get("parlamentarNome"), "civil": "", "partido": p.get("partidoSigla") or "", "foto": p.get("parlamentarFoto") or "",
               "cont": r["cont"], "props": r["props"], "votos": {}, "vlist": [], "pres": r["pres"], "sapl": "https://www3.al.es.gov.br/spl/parlamentares.aspx"}
        if k is None: sem.append(reg["nome"]); dep["x" + str(p["parlamentarID"])] = reg
        elif str(k) not in dep or sum(reg["cont"].values()) > sum(dep[str(k)]["cont"].values()): dep[str(k)] = reg
    out = {"fonte": "Assembleia Legislativa do Espírito Santo (Ales) · API pública do SPL", "url": "https://www3.al.es.gov.br/dados-abertos.aspx", "gerado": datetime.date.today().isoformat(),
           "legislatura": "20ª legislatura (2023–2027)", "temVotos": False, "dep": dep}
    json.dump(out, open(OUT / "ES.json", "w"), ensure_ascii=False, separators=(",", ":"))
    r = {"deputados": len(parl), "ligados": len(parl) - len(sem), "proposicoes": sum(sum(x["cont"].values()) for x in R.values()), "sem_autor": sum(1 for x in R.values() if not x["aid"]), "sem_par": sem[:10]}
    print(json.dumps(r, ensure_ascii=False)); return r

if __name__ == "__main__":
    main()
