"""ALEPE (Pernambuco): deputados e proposições da 20ª legislatura pela API de dados abertos da Alepe.
O site só responde a acessos do Brasil, então a coleta passa pela saída BR (coleta/saida_br.py).
Saída: site/data/est/PE.json no mesmo formato das outras Assembleias."""
import io, json, re, sys, datetime
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa, norm
from saida_br import get

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "est"; OUT.mkdir(exist_ok=True)
API = "https://dadosabertos.alepe.pe.gov.br/api/v1"
SIG = [("EMENDA A CONSTITUI", "PEC"), ("LEI COMPLEMENTAR", "PLC"), ("LEI ORDIN", "PLO"), ("DECRETO LEGISLATIVO", "PDL"), ("RESOLU", "PR"),
       ("INDICA", "IND"), ("REQUERIMENTO", "REQ"), ("VETO", "VETO")]
PROJ = {"PLO", "PLC", "PEC", "PDL", "PR"}

def sigla(tipo, padrao):
    t = norm(tipo)
    for k, s in SIG:
        if norm(k) in t: return s
    return padrao

def data_iso(s):
    m = re.match(r"(\d\d)/(\d\d)/(\d{4})", s or ""); return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""

def itens(caminho, padrao):
    r = get(f"{API}/proposicoes/{caminho}/", {"legislatura": "20"}, timeout=180)
    if r is None or r.status_code != 200: print(caminho, "falhou", r.status_code if r is not None else None, flush=True); return []
    out = []
    for el in ET.parse(io.BytesIO(r.content)).getroot():
        a = el.attrib; aut = [x.get("nome", "") for x in el.iter("autor") if (x.get("tipo") or "").upper().startswith("DEPUTAD")]
        ementa = a.get("ementa") or (el.findtext("ementa") or "")
        out.append({"sig": sigla(a.get("tipo", ""), padrao), "cod": f"{a.get('numero', '')}/{a.get('ano', '')}", "ementa": re.sub(r"\s+", " ", ementa).strip(),
                    "data": data_iso(a.get("dataPublicacao") or a.get("dataCriacao") or ""), "aut": aut})
    print(caminho, len(out), flush=True); return out

def main():
    r = get(f"{API}/parlamentares"); parl = r.json() if r is not None and r.status_code == 200 else []
    print(len(parl), "deputados", flush=True)
    todos = itens("projetos", "PL") + itens("indicacoes", "IND") + itens("requerimentos", "REQ")
    por = defaultdict(list)
    for x in todos:
        for n in x["aut"]: por[limpa(n)].append(x)
    U = json.load(open(D / "uf" / "PE.json")); de = U.get("de22", [])
    idx = {}
    for k, x in enumerate(de): idx.setdefault(limpa(x[0]), k); idx.setdefault(limpa(x[1]), k)
    toks = [(k, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for k, x in enumerate(de)]
    nomes = {limpa(p["nomeParlamentar"]): p for p in parl}
    for n in por:  # autores que não estão mais em exercício também entram
        nomes.setdefault(n, {"nomeParlamentar": next(a for x in por[n] for a in x["aut"] if limpa(a) == n), "partido": ""})
    dep = {}; sem = []
    for ln, p in nomes.items():
        its = sorted(por.get(ln, []), key=lambda x: x["data"], reverse=True)
        if not its and ln not in {limpa(q["nomeParlamentar"]) for q in parl}: continue
        k = idx.get(ln)
        if k is None:
            tt = set(ln.split())
            best = sorted(((len(tt & q) / max(1, min(len(tt), len(q))), len(tt & q), j) for j, q in toks), reverse=True)
            if best and best[0][0] >= 0.99 and (len(best) < 2 or best[1][:2] < best[0][:2]): k = best[0][2]
            elif best and best[0][1] >= 2 and best[0][0] >= 0.6 and (len(best) < 2 or best[1][:2] < best[0][:2]): k = best[0][2]
        reg = {"nome": p["nomeParlamentar"], "civil": "", "partido": p.get("partido", ""), "foto": "", "cont": dict(Counter(x["sig"] for x in its)),
               "props": [[f"{x['sig']} {x['cod']}", x["ementa"][:200], x["data"], 0] for x in its if x["sig"] in PROJ][:80], "votos": {}, "vlist": [],
               "sapl": "https://proposicoes.alepe.pe.gov.br/"}
        if k is None:
            if not its: continue
            sem.append(p["nomeParlamentar"]); dep["x" + re.sub(r"\W+", "-", ln.lower())] = reg
        elif str(k) not in dep or sum(reg["cont"].values()) > sum(dep[str(k)]["cont"].values()): dep[str(k)] = reg
    out = {"fonte": "Assembleia Legislativa de Pernambuco (Alepe) · Dados Abertos", "url": "https://dadosabertos.alepe.pe.gov.br", "gerado": datetime.date.today().isoformat(),
           "legislatura": "20ª legislatura (2023–2027)", "temVotos": False, "dep": dep}
    json.dump(out, open(OUT / "PE.json", "w"), ensure_ascii=False, separators=(",", ":"))
    r = {"deputados": len(parl), "registros": len(dep), "ligados": sum(1 for k in dep if not k.startswith("x")), "proposicoes": len(todos), "sem_par": sem[:12]}
    print(json.dumps(r, ensure_ascii=False)); return r

if __name__ == "__main__":
    main()
