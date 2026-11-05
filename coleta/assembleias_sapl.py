"""Assembleias Legislativas que usam o SAPL (sistema do Interlegis): deputados estaduais, projetos que apresentaram desde 2023
e, onde a Assembleia registra, o voto de cada deputado.
Saída: site/data/est/{UF}.json  {"fonte", "gerado", "dep": {chave: {...}}}  onde chave = índice do deputado em uf/{UF}.json (de22).
Sem captcha nem bloqueio: só a API pública do SAPL."""
import json, os, re, sys, time, unicodedata, datetime, concurrent.futures as cf
from collections import Counter, defaultdict
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "est"; OUT.mkdir(exist_ok=True)
UFS = os.environ.get("UFS", "AC AL AM MT PB PI RO TO").split()
DESDE = "2023-02-01"; ANOS = range(2023, datetime.date.today().year + 1)
LIM_MIN = float(os.environ.get("MAX_MIN", "35"))
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json"}
norm = lambda s: re.sub(r"[^A-Z ]", "", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()).strip()
VOTO = {"Sim": "S", "Não": "N", "Nao": "N", "Abstenção": "A", "Abstencao": "A", "Obstrução": "O"}
PROJ = {"PLO", "PL", "PLC", "PEC", "PDL", "PRE", "PR", "PLE", "PLOA"}

class SAPL:
    def __init__(s, uf):
        s.b = f"https://sapl.al.{uf.lower()}.leg.br/api"; s.S = requests.Session(); s.S.headers.update(H); s.fim = time.time() + LIM_MIN * 60
    def get(s, path, **p):
        for k in range(4):
            try:
                r = s.S.get(f"{s.b}/{path}", params=p, timeout=40)
                if r.status_code == 200: return r.json()
                if r.status_code in (400, 403, 404): return None
            except Exception: pass
            time.sleep(2 * (k + 1))
        return None
    def todos(s, path, parar=None, **p):
        p.setdefault("page_size", 100); pg = 1; out = []
        while time.time() < s.fim:
            j = s.get(path, page=pg, **p)
            if not j: break
            rs = j.get("results", []); out += rs
            if parar and rs and parar(rs[-1]): break
            if not j.get("pagination", {}).get("next_page"): break
            pg += 1
        return out

def coleta(uf):
    t0 = time.time(); A = SAPL(uf); log = []
    legs = A.todos("parlamentares/legislatura/")
    if not legs: return uf, {"erro": "API indisponível"}
    leg = max(legs, key=lambda x: x.get("numero") or 0)
    mand = A.todos("parlamentares/mandato/", legislatura=leg["id"]) or [m for m in A.todos("parlamentares/mandato/") if m.get("legislatura") == leg["id"]]
    pids = {m["parlamentar"] for m in mand}
    parl = {p["id"]: p for p in A.todos("parlamentares/parlamentar/") if p["id"] in pids}
    partidos = {p["id"]: p.get("sigla") for p in A.todos("parlamentares/partido/")}
    fil = defaultdict(list)
    for f in A.todos("parlamentares/filiacao/"):
        if f.get("parlamentar") in pids: fil[f["parlamentar"]].append(f)
    def partido(pid):
        fs = sorted(fil.get(pid, []), key=lambda f: f.get("data") or "")
        ativo = [f for f in fs if not f.get("data_desfiliacao")]
        f = (ativo or fs or [None])[-1]; return partidos.get(f["partido"]) if f else ""
    # autores -> parlamentar
    nomes = {norm(p.get("nome_parlamentar")): pid for pid, p in parl.items()}; nomes.update({norm(p.get("nome_completo")): pid for pid, p in parl.items()})
    aut = {}
    for a in A.todos("base/autor/"):
        pid = a.get("object_id") if a.get("object_id") in parl else nomes.get(norm(a.get("nome") or a.get("__str__")))
        if pid: aut[a["id"]] = pid
    tipos = {t["id"]: t.get("sigla") or "" for t in A.todos("materia/tipomaterialegislativa/")}
    # matérias desde 2023
    mats = {}
    for ano in ANOS:
        for m in A.todos("materia/materialegislativa/", ano=ano):
            mats[m["id"]] = m
    autoria = defaultdict(list)
    for m in mats.values():
        for a in m.get("autores") or []:
            if a in aut: autoria[aut[a]].append(m["id"])
    if not any(autoria.values()):  # alguns SAPL não preenchem "autores" na matéria: usa a tabela de autoria
        ids = set(mats)
        for a in A.todos("materia/autoria/", parar=lambda r: r.get("materia", 0) < min(ids or [0]), o="-materia"):
            if a.get("materia") in ids and a.get("autor") in aut: autoria[aut[a["autor"]]].append(a["materia"])
    # votos desde 2023
    votos = defaultdict(list); regs = {}
    vp = A.todos("sessao/votoparlamentar/", parar=lambda r: (r.get("data_hora") or "9") < DESDE, o="-id")
    vp = [v for v in vp if (v.get("data_hora") or "") >= DESDE and v.get("parlamentar") in parl]
    if vp:
        alvo = {v["votacao"] for v in vp}
        for r in A.todos("sessao/registrovotacao/", parar=lambda r: (r.get("data_hora") or "9") < DESDE, o="-id"):
            if r["id"] in alvo: regs[r["id"]] = r
        falta = [m for m in {r.get("materia") for r in regs.values()} if m and m not in mats]
        for mid in falta[:3000]:
            if time.time() > A.fim: break
            j = A.get(f"materia/materialegislativa/{mid}/")
            if j: mats[mid] = j
        for v in vp: votos[v["parlamentar"]].append(v)
    # junta com os deputados do site (TSE 2022)
    U = json.load(open(D / "uf" / f"{uf}.json")); de = U.get("de22", [])
    idx = {}
    for i, x in enumerate(de):
        idx.setdefault(norm(x[1]), i); idx.setdefault(norm(x[0]), i)
    def desc(mid):
        m = mats.get(mid) or {}; return f"{tipos.get(m.get('tipo'), '')} {m.get('numero', '')}/{m.get('ano', '')}".strip(), re.sub(r"\s+", " ", m.get("ementa") or "")[:200]
    dep = {}; sem = []
    for pid, p in parl.items():
        k = idx.get(norm(p.get("nome_completo"))); k = k if k is not None else idx.get(norm(p.get("nome_parlamentar")))
        ms = sorted(set(autoria.get(pid, [])), key=lambda i: (mats[i].get("data_apresentacao") or ""), reverse=True)
        cont = Counter(tipos.get(mats[i].get("tipo"), "?") for i in ms)
        props = [[*desc(i), mats[i].get("data_apresentacao") or "", 1 if mats[i].get("em_tramitacao") else 0] for i in ms if tipos.get(mats[i].get("tipo")) in PROJ][:80]
        vs = sorted(votos.get(pid, []), key=lambda v: v.get("data_hora") or "", reverse=True)
        vc = Counter(VOTO.get(v.get("voto"), "?") for v in vs)
        vlist = []
        for v in vs[:60]:
            r = regs.get(v["votacao"]) or {}; c, e = desc(r.get("materia"))
            vlist.append([c, e, VOTO.get(v.get("voto"), v.get("voto")), (v.get("data_hora") or "")[:10], r.get("numero_votos_sim"), r.get("numero_votos_nao")])
        reg = {"nome": p.get("nome_parlamentar"), "civil": p.get("nome_completo"), "partido": partido(pid), "foto": p.get("fotografia") or "",
               "cont": dict(cont), "props": props, "votos": dict(vc), "vlist": vlist, "sapl": f"https://sapl.al.{uf.lower()}.leg.br/parlamentar/{pid}"}
        if k is None: sem.append(p.get("nome_parlamentar")); dep["x" + str(pid)] = reg
        else: dep[str(k)] = reg
    out = {"fonte": f"Assembleia Legislativa ({uf}) · SAPL, dados abertos", "url": f"https://sapl.al.{uf.lower()}.leg.br", "gerado": datetime.date.today().isoformat(),
           "legislatura": leg.get("__str__"), "temVotos": bool(vp), "dep": dep}
    json.dump(out, open(OUT / f"{uf}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return uf, {"deputados": len(parl), "ligados": len(parl) - len(sem), "materias": len(mats), "votos": len(vp), "seg": round(time.time() - t0), "sem_par": sem[:8]}

if __name__ == "__main__":
    def seguro(u):
        try: return coleta(u)
        except Exception as e: return u, {"erro": f"{type(e).__name__}: {e}"[:300]}
    with cf.ThreadPoolExecutor(len(UFS)) as ex:
        R = dict(ex.map(seguro, UFS))
    print(json.dumps(R, ensure_ascii=False, indent=1))
