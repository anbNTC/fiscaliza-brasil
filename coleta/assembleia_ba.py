"""ALBA (Bahia): proposições de cada deputado de fev/2023 a jul/2025, pela consulta pública do site da Assembleia.
A partir de ago/2025 a ALBA passou a usar outro sistema, protegido contra acesso automático; por regra do projeto, não contornamos.
Saída: site/data/est/BA.json no mesmo formato das outras Assembleias."""
import json, os, re, sys, time, html, datetime, concurrent.futures as cf
from collections import Counter
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "est"; OUT.mkdir(exist_ok=True)
B = "https://www.al.ba.gov.br/atividade-legislativa-nova/proposicoes"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
FIM = time.time() + 60 * float(os.environ.get("MAX_MIN", "25"))
PROJ = {"PL", "PLC", "PEC", "PDL", "PRS"}

def get(S, **p):
    for k in range(3):
        try:
            r = S.get(B, params=p, timeout=60)
            if r.ok: return r.text
        except Exception: pass
        time.sleep(3 * (k + 1))
    return ""

def linhas(t):
    out = []
    for m in re.finditer(r'proposicao/([A-Z.]+)-(\d+)-(\d{4})"[\s\S]*?</td>\s*<td><span[^>]*>([\s\S]*?)</span>', t):
        out.append((m.group(1).rstrip("."), int(m.group(2)), m.group(3), re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(4)))).strip()))
    return out

def coleta_dep(did):
    S = requests.Session(); S.headers.update(H); itens = []
    for pg in range(0, 30):
        if time.time() > FIM: break
        ls = linhas(get(S, deputado=did, dataInicio="2023-02-01", dataFim=datetime.date.today().isoformat(), page=pg, size=200)); time.sleep(0.5)
        if not ls: break
        itens += ls
        if len(ls) < 200: break
    return did, itens

def main():
    S = requests.Session(); S.headers.update(H)
    t = get(S)
    sel = re.search(r'<select[^>]+name="deputado"[\s\S]*?</select>', t)
    ops = [(v, re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", n))).strip()) for v, n in re.findall(r'<option value="(\d+)">([\s\S]*?)</option>', sel.group(0))] if sel else []
    print(len(ops), "deputados", flush=True)
    with cf.ThreadPoolExecutor(3) as ex: R = dict(ex.map(lambda o: coleta_dep(o[0]), ops))
    U = json.load(open(D / "uf" / "BA.json")); de = U.get("de22", [])
    idx = {}
    for k, x in enumerate(de): idx.setdefault(limpa(x[0]), k); idx.setdefault(limpa(x[1]), k)
    toks = [(k, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for k, x in enumerate(de)]
    dep = {}; sem = []
    for did, nome in ops:
        its = sorted(set(R.get(did, [])), key=lambda x: (x[2], x[1]), reverse=True)
        k = idx.get(limpa(nome))
        if k is None:
            tt = set(limpa(nome).split())
            best = sorted(((len(tt & q) / max(1, min(len(tt), len(q))), len(tt & q), j) for j, q in toks), reverse=True)
            if best and best[0][0] >= 0.99 and (len(best) < 2 or best[1][:2] < best[0][:2]): k = best[0][2]
        reg = {"nome": nome, "civil": "", "partido": "", "foto": "", "cont": dict(Counter(x[0] for x in its)),
               "props": [[f"{x[0]} {x[1]}/{x[2]}", x[3][:200], "", 0] for x in its if x[0] in PROJ][:80], "votos": {}, "vlist": [],
               "sapl": f"{B}?deputado={did}&dataInicio=2023-02-01"}
        if k is None: sem.append(nome); dep["x" + did] = reg
        else: dep[str(k)] = reg
    out = {"fonte": "Assembleia Legislativa da Bahia (ALBA) · consulta pública de proposições", "url": "https://www.al.ba.gov.br", "gerado": datetime.date.today().isoformat(),
           "legislatura": "20ª legislatura (2023–2027)", "temVotos": False,
           "obs": "Proposições de fevereiro de 2023 a julho de 2025. Desde agosto de 2025, a ALBA usa outro sistema que bloqueia o acesso automático; as proposições mais novas estão no site oficial.", "dep": dep}
    json.dump(out, open(OUT / "BA.json", "w"), ensure_ascii=False, separators=(",", ":"))
    r = {"deputados": len(ops), "ligados": len(ops) - len(sem), "proposicoes": sum(len(v) for v in R.values()), "sem_par": sem[:10]}
    print(json.dumps(r, ensure_ascii=False)); return r

if __name__ == "__main__":
    main()
