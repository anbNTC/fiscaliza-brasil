"""ALRS (Rio Grande do Sul): proposições de cada deputado eleito em 2022, de 2023 em diante, pela pesquisa pública de proposições da Assembleia.
A página de resultados traz a lista completa em JSON (usada pelo botão "Gerar CSV"); lemos esse JSON.
O site só responde a acessos do Brasil, então a coleta passa pela saída BR (coleta/saida_br.py).
Saída: site/data/est/RS.json no mesmo formato das outras Assembleias."""
import json, re, sys, time, html, datetime, concurrent.futures as cf
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa
from saida_br import get

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "est"; OUT.mkdir(exist_ok=True)
B = "https://ww4.al.rs.gov.br"
ANOS = range(2023, datetime.date.today().year + 1)
PROJ = {"PL", "PLC", "PEC", "PDL", "PR"}
DEC = json.JSONDecoder()

def lista(t):
    i = t.find('[{"siglaTipoProposicao"')
    if i < 0: return []
    try: return DEC.raw_decode(t, i)[0]
    except ValueError: return []

def data_iso(s):
    m = re.match(r"(\d\d)/(\d\d)/(\d{4})", s or ""); return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""

def coleta_dep(nome):
    itens = {}
    for ano in ANOS:
        for pg in range(1, 30):
            r = get(f"{B}/legislativo/pesquisa", {"nomeProponente": nome, "anoProposicao": ano, "pagina": pg}, timeout=150); time.sleep(0.3)
            ls = lista(r.text) if r is not None and r.status_code == 200 else []
            novos = [x for x in ls if x.get("proposicaoId") not in itens]
            for x in novos: itens[x.get("proposicaoId")] = x
            if not novos or 'pagina=' + str(pg + 1) not in (r.text if r is not None else ""): break
    return nome, list(itens.values())

def main():
    t = get(f"{B}/legislativo").text
    sel = re.search(r'<select name="nomeProponente"[\s\S]*?</select>', t)
    ops = [html.unescape(x).strip() for x in re.findall(r'<option value="([^"]*)"', sel.group(0))] if sel else []
    U = json.load(open(D / "uf" / "RS.json")); de = U.get("de22", [])
    idx = {}
    for k, x in enumerate(de): idx.setdefault(limpa(x[0]), k); idx.setdefault(limpa(x[1]), k)
    toks = [(k, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for k, x in enumerate(de)]
    alvo = {}
    for o in ops:
        if not o or re.match(r"^\d+ Deputados", o): continue
        k = idx.get(limpa(o))
        if k is None:
            tt = set(limpa(o).split())
            best = sorted(((len(tt & q) / max(1, min(len(tt), len(q))), len(tt & q), j) for j, q in toks), reverse=True)
            if best and (len(best) < 2 or best[1][:2] < best[0][:2]) and best[0][0] >= 0.99 and best[0][1] >= min(2, len(tt)): k = best[0][2]
        if k is not None and k not in alvo.values(): alvo[o] = k
    print(len(ops), "proponentes;", len(alvo), "de", len(de), "eleitos encontrados", flush=True)
    with cf.ThreadPoolExecutor(3) as ex: R = dict(ex.map(coleta_dep, alvo))
    dep = {}
    for nome, k in alvo.items():
        its = sorted(R[nome], key=lambda x: data_iso(x.get("dthProtocolo")), reverse=True)
        cont = Counter((x.get("siglaTipoProposicao") or "?").strip() for x in its)
        props = [[f"{x['siglaTipoProposicao'].strip()} {x.get('nroProposicao')}/{x.get('anoProposicao')}", re.sub(r"\s+", " ", x.get("ementa") or "").strip()[:200],
                  data_iso(x.get("dthProtocolo")), 0 if re.search(r"arquiv|rejeit|retirad|sancion|promulg|vetad|prejudic", x.get("descricao") or "", re.I) else 1]
                 for x in its if (x.get("siglaTipoProposicao") or "").strip() in PROJ][:80]
        dep[str(k)] = {"nome": nome, "civil": "", "partido": "", "foto": "", "cont": dict(cont), "props": props, "votos": {}, "vlist": [],
                       "sapl": f"{B}/legislativo/pesquisa?nomeProponente={nome.replace(' ', '+')}"}
    out = {"fonte": "Assembleia Legislativa do Rio Grande do Sul (ALRS) · pesquisa de proposições", "url": f"{B}/legislativo", "gerado": datetime.date.today().isoformat(),
           "legislatura": "56ª legislatura (2023–2027)", "temVotos": False, "dep": dep}
    json.dump(out, open(OUT / "RS.json", "w"), ensure_ascii=False, separators=(",", ":"))
    falta = [de[k][0] for k in range(len(de)) if k not in alvo.values()]
    r = {"eleitos": len(de), "ligados": len(dep), "proposicoes": sum(len(v) for v in R.values()), "sem_par": falta[:12]}
    print(json.dumps(r, ensure_ascii=False)); return r

if __name__ == "__main__":
    main()
