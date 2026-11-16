"""Câmara Municipal de Cuiabá (MT): proposições de cada vereador desde 2025.
Fonte: Processo Legislativo Eletrônico da Câmara (https://legislativo.camaracuiaba.mt.gov.br/spl/), consulta pública sem captcha.
1) consulta-autor.aspx: autores com proposições em 2025 ou 2026 (id do autor).
2) consulta-producao.aspx?autor=ID&tipo=T&ano=A: total de cada tipo por vereador e ano (só a primeira página, que traz o total
   e os 10 mais recentes; as outras páginas exigem reenvio de formulário e não são lidas, para não sobrecarregar o site).
Sem votos nominais (a consulta não publica). Responde só a acessos do Brasil: usa a saída BR.
Roda no máximo uma vez por semana (REFAZ=1 força). Saída: site/data/cam/90670.json no formato das câmaras do SAPL."""
import json, os, re, sys, time, html, datetime
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from saida_br import get
from assembleias_sapl import limpa, norm, H

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "cam"; UE = "90670"
B = "https://legislativo.camaracuiaba.mt.gov.br/spl/"
ANOS = [a for a in (2025, 2026) if a <= datetime.date.today().year]
# tipo da Câmara → sigla do painel (as que contam como projeto: PL, PLC, PDL, PRE, PEL)
TIPOS = {103: "PL", 101: "PLC", 105: "PDL", 106: "PRE", 107: "PEL", 116: "IND", 125: "PINF", 124: "REQ", 129: "REQ", 135: "MOC", 136: "MOC"}
PROJ = {"PL", "PLC", "PDL", "PRE", "PEL"}
SIGLA = {"PL": "PL", "PLC": "PLC", "PDL": "PDL", "PRE": "PR", "PEL": "PELOM"}
FORA = re.compile(r"mesa|executivo|comiss|prefeit|tribunal|minist[ée]rio|defensoria|popular|lideran", re.I)
HOMEN = re.compile(r"denomina|utilidade p[uú]blica|t[ií]tulo de cidad|calend[aá]rio|dia (municipal|do|da)|semana (municipal|do|da)|honra|homenag|medalha|comenda", re.I)

def pg(q):
    for i in range(3):
        r = get(B + q, headers={**H, "accept": "text/html"}, timeout=120)
        if r is not None and r.ok: return html.unescape(r.text)
        time.sleep(4 + 4 * i)
    return None

def itens(t):
    """total e os itens da primeira página: [código, ementa, data, tramitando, autores]"""
    s = re.sub(r"\s+", " ", re.sub(r"<(script|style|svg)[\s\S]*?</\1>|<[^>]+>", " | ", t))
    tot = re.search(r"Localizada\(s\)[ |]*(\d+)", s); out = []
    for m in re.finditer(r"([A-ZÀ-Úa-zà-ú ]+?) n° (\d+)/(\d{4}) [ |]*(.*?)\| Processo N°:(.*?)(?=[A-ZÀ-Úa-zà-ú ]+? n° \d+/\d{4} |$)", s):
        bloco = m.group(5)
        dt = re.search(r"Data:[ |]*(\d\d)/(\d\d)/(\d{4})", bloco); sit = re.search(r"Situação:[ |]*([^|]+)", bloco)
        au = re.search(r"Autor\(es\) da Proposição:[ |]*(.*?)(?:\| \| \| \| |IA \||ACOMPANHE|DETALHES)", bloco)
        out.append([m.group(2) + "/" + m.group(3), m.group(4).strip(" |")[:220], f"{dt.group(3)}-{dt.group(2)}-{dt.group(1)}" if dt else "",
                    1 if sit and "tramit" in sit.group(1).lower() else 0, [a.strip() for a in (au.group(1) if au else "").split("|") if a.strip()]])
    return (int(tot.group(1)) if tot else 0), out

def main():
    g = OUT / "_cuiaba_gerado.txt"
    if not os.environ.get("REFAZ") and g.exists() and (datetime.date.today() - datetime.date.fromisoformat(g.read_text().strip())).days < 7:
        print("Cuiabá: coletada há menos de 7 dias, nada a fazer"); return
    t = pg("consulta-autor.aspx")
    if not t: print("Cuiabá: consulta indisponível"); return
    autores = []
    for m in re.finditer(r"<div class='card-title[^>]*>([^<]+?)\((\d+)\)<[\s\S]*?</div></div></div>", t):
        anos = re.findall(r"consulta-producao\.aspx\?autor=(\d+)&ano=(\d{4})", m.group(0)); nome = re.sub(r"\s*\(Câmara Digital\)\s*", "", m.group(1)).strip(" .")
        if anos and any(int(a) in ANOS for _, a in anos) and not FORA.search(nome): autores.append((nome, anos[0][0]))
    print("autores com proposições desde 2025:", len(autores), flush=True)
    U = json.load(open(D / "uf" / "MT.json")); tse = U["mun"][UE][3]
    idx = {}
    for i, x in enumerate(tse): idx.setdefault(norm(x[0]), i); idx.setdefault(limpa(x[0]), i); idx.setdefault(norm(x[1]), i)
    dep = {}; sem = []
    for nome, aid in autores:
        cont = Counter(); anos = defaultdict(Counter); props = []; parcial = False
        for ano in ANOS:
            for tp, sg in TIPOS.items():
                r = pg(f"consulta-producao.aspx?autor={aid}&tipo={tp}&ano={ano}"); time.sleep(0.6)
                if not r: continue
                n, its = itens(r)
                if not n: continue
                cont[sg] += n; anos[str(ano)][sg] += n
                if sg in PROJ:
                    parcial |= n > len(its)
                    for c, em, dt, tram, au in its:
                        props.append([f"{SIGLA[sg]} {c}", em, dt, tram, 1 if not au or limpa(au[0]) == limpa(nome) else 0])
        if not cont: continue
        k = idx.get(norm(nome)); k = idx.get(limpa(nome)) if k is None else k
        if k is None:
            tt = set(limpa(nome).split())
            cs = [i for i, x in enumerate(tse) if limpa(x[0]) and set(limpa(x[0]).split()) <= tt] or [i for i, x in enumerate(tse) if len(tt & set(limpa(x[1]).split())) >= 2]
            if len(cs) == 1: k = cs[0]
        reg = {"nome": nome, "civil": "", "partido": "", "foto": "", "cont": dict(cont),
               "props": sorted(props, key=lambda p: p[2], reverse=True)[:80], "parcial": parcial, "leis": [], "votos": {}, "vlist": [],
               "sapl": f"{B}consulta-producao.aspx?autor={aid}"}
        if k is None: sem.append(nome); dep["x" + aid] = reg
        else: dep[str(k)] = reg
        print(" ", nome, "→", "TSE " + str(k) if k is not None else "sem casar", dict(cont), flush=True)
    if not dep: print("Cuiabá: nada coletado"); return
    out = {"fonte": "Câmara Municipal de Cuiabá (MT) · Processo Legislativo Eletrônico", "url": B + "consulta-autor.aspx", "gerado": datetime.date.today().isoformat(),
           "legislatura": "2025–2028", "temVotos": False, "casa": "Câmara Municipal", "desde": "2025",
           "obs": "Totais por tipo de proposição como publicados pela Câmara de Cuiabá. A lista mostra os projetos mais recentes de cada tipo; a consulta da Câmara não publica os votos de cada vereador.",
           "dep": dep}
    json.dump(out, open(OUT / f"{UE}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    try: I = json.load(open(OUT / "index.json"))
    except Exception: I = {}
    I[UE] = ["MT", "CUIABÁ", B, False, len(dep), datetime.date.today().isoformat()]
    json.dump(I, open(OUT / "index.json", "w"), ensure_ascii=False, separators=(",", ":"))
    g.write_text(datetime.date.today().isoformat())
    print("gravado:", len(dep), "vereadores;", len(sem), "sem casar com o TSE:", sem, flush=True)

if __name__ == "__main__":
    main()
