"""ALESC (Santa Catarina): proposições de cada deputado desde 2023, pelas páginas públicas do e-Legis (sem captcha).
Lê a lista filtrada por autor, página por página, devagar para não sobrecarregar o site da Assembleia.
Saída: site/data/est/SC.json no mesmo formato das outras Assembleias."""
import json, os, re, sys, time, html, datetime, concurrent.futures as cf
from collections import Counter
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa, norm

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "est"; OUT.mkdir(exist_ok=True)
B = "https://portalelegis.alesc.sc.gov.br"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
DESDE = "2023-02-01"; FIM = time.time() + 60 * float(os.environ.get("MAX_MIN", "35"))
PAG_MAX = {"processo-legislativo": 40, "atividade-parlamentar": 60}
PROJ = ("PL", "PLC", "PEC", "PDL", "PRS", "PR")

def get(S, u, **p):
    for k in range(3):
        try:
            r = S.get(u, params=p, timeout=40)
            if r.ok: return r.text
        except Exception: pass
        time.sleep(3 * (k + 1))
    return ""

def cartoes(t):
    out = []
    for bloco in re.split(r'<div class="card card-alesc', t)[1:]:
        m = re.search(r'href="/proposicoes/([A-Za-z0-9]+)">([^<]+)</a>', bloco)
        if not m: continue
        ementa = re.search(r'<p class="mb-1[^"]*"[^>]*>([\s\S]*?)</p>', bloco)
        ent = re.search(r'Entrada</div>\s*<div[^>]*>(\d\d)/(\d\d)/(\d{4})', bloco)
        sit = re.search(r'Situação atual</div>\s*<div[^>]*>([\s\S]*?)</div>', bloco)
        out.append({"id": m.group(1), "cod": html.unescape(m.group(2)).strip(), "ementa": re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", ementa.group(1) if ementa else ""))).strip(),
                    "data": f"{ent.group(3)}-{ent.group(2)}-{ent.group(1)}" if ent else "", "sit": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", sit.group(1))).strip() if sit else ""})
    return out

def tipo(cod): return re.split(r"[./ ]", cod.strip())[0].upper()

def coleta_dep(slug):
    S = requests.Session(); S.headers.update(H); res = {"cont": Counter(), "props": [], "corte": False}
    for caminho, maxp in PAG_MAX.items():
        for pg in range(1, maxp + 1):
            if time.time() > FIM: res["corte"] = True; break
            cs = cartoes(get(S, f"{B}/proposicoes/{caminho}", iniciativa=slug, page=pg)); time.sleep(0.4)
            if not cs: break
            novos = [c for c in cs if c["data"] >= DESDE]
            for c in novos:
                res["cont"][tipo(c["cod"])] += 1
                if caminho == "processo-legislativo": res["props"].append([c["cod"], c["ementa"][:200], c["data"], 0 if re.search(r"arquiv|rejeit|retirad|sancion|promulg|vetad", c["sit"], re.I) else 1])
            if len(novos) < len(cs): break
            if pg == maxp: res["corte"] = True
    return slug, res

def main():
    S = requests.Session(); S.headers.update(H)
    t = get(S, f"{B}/proposicoes/processo-legislativo")
    ops = re.findall(r'<option value="([a-z0-9\-]+)"[^>]*>\s*(Deputad[oa] [^<]+?)\s*</option>', t)
    print(len(ops), "deputados em exercício na lista", flush=True)
    with cf.ThreadPoolExecutor(3) as ex: R = dict(ex.map(lambda o: coleta_dep(o[0]), ops))
    U = json.load(open(D / "uf" / "SC.json")); de = U.get("de22", [])
    idx = {}
    for k, x in enumerate(de): idx.setdefault(limpa(x[0]), k); idx.setdefault(limpa(x[1]), k)
    toks = [(k, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for k, x in enumerate(de)]
    dep = {}; sem = []
    for slug, nome in ops:
        r = R[slug]; nome = html.unescape(nome).strip(); k = idx.get(limpa(nome))
        if k is None:
            tt = set(limpa(nome).split())
            best = sorted(((len(tt & q) / max(1, min(len(tt), len(q))), len(tt & q), j) for j, q in toks), reverse=True)
            if best and best[0][0] >= 0.99 and (len(best) < 2 or best[1][:2] < best[0][:2]): k = best[0][2]
        reg = {"nome": re.sub(r"^Deputad[oa]\s+", "", nome), "civil": "", "partido": "", "foto": "", "cont": dict(r["cont"]), "props": sorted(r["props"], key=lambda p: p[2], reverse=True)[:80],
               "votos": {}, "vlist": [], "sapl": f"{B}/proposicoes/processo-legislativo?iniciativa={slug}", "parcial": r["corte"]}
        if k is None: sem.append(nome); dep["x" + slug] = reg
        else: dep[str(k)] = reg
    out = {"fonte": "Assembleia Legislativa de Santa Catarina (ALESC) · e-Legis", "url": B, "gerado": datetime.date.today().isoformat(),
           "legislatura": "20ª legislatura (2023–2027)", "temVotos": False, "dep": dep}
    json.dump(out, open(OUT / "SC.json", "w"), ensure_ascii=False, separators=(",", ":"))
    r = {"deputados": len(ops), "ligados": len(ops) - len(sem), "proposicoes": sum(sum(x["cont"].values()) for x in R.values()), "parciais": sum(1 for x in R.values() if x["corte"]), "sem_par": sem[:10]}
    print(json.dumps(r, ensure_ascii=False)); return r

if __name__ == "__main__":
    main()
