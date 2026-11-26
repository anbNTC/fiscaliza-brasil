"""Câmaras municipais no sistema "Câmara sem Papel" / Processo Legislativo Eletrônico (páginas /spl/*.aspx): proposições de cada
vereador desde 2025. É o mesmo sistema em todas (Cuiabá, Teresina, Sorocaba, Várzea Grande, Vila Velha...), consulta pública sem captcha.
Por câmara:
1) consulta-tipo.aspx: tipos de proposição da casa (o código de cada tipo muda de uma câmara para outra) e anos com proposições.
2) consulta-autor.aspx: autores com proposições em 2025 ou 2026.
3) consulta-producao.aspx?autor=ID&tipo=T&ano=A: total de cada tipo por vereador e ano (só a primeira página: o total e os 10 mais
   recentes; as outras páginas exigem reenvio de formulário e não são lidas, para não sobrecarregar o site).
Sem votos nominais (o sistema não publica). Só responde a acessos do Brasil: usa a saída BR.
Cada câmara é refeita no máximo uma vez por semana (REFAZ=1 força); cada execução para em MAX_MIN minutos e continua na próxima.
Uma câmara só é gravada se a maioria dos autores casar com os vereadores eleitos (evita gravar a cidade errada quando dois
municípios têm o mesmo nome, ex.: Santa Luzia). Saída: site/data/cam/{UE}.json no formato das câmaras do SAPL."""
import json, os, re, sys, time, html, datetime, concurrent.futures as cf
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from saida_br import get
from assembleias_sapl import limpa, norm, H

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "cam"
ANOS = [a for a in (2025, 2026) if a <= datetime.date.today().year]
MAX_MIN = float(os.environ.get("MAX_MIN", "40")); T0 = time.time()
# (UF, código TSE do município, endereço do sistema)
CAMS = [("MT", "90670", "https://legislativo.camaracuiaba.mt.gov.br"), ("PI", "12190", "https://teresina.camarasempapel.com.br"),
        ("SP", "71455", "https://sorocaba.camarasempapel.com.br"), ("MT", "91677", "https://varzeagrande.camarasempapel.com.br"),
        ("ES", "57037", "https://vilavelha.camarasempapel.com.br"), ("MG", "51551", "https://santaluzia.camarasempapel.com.br"),
        ("ES", "56251", "https://cariacica.camarasempapel.com.br"), ("ES", "56634", "https://linhares.camarasempapel.com.br"),
        ("SP", "70475", "https://santanadeparnaiba.camarasempapel.com.br"), ("SP", "71838", "https://camarasempapel.camarataubate.sp.gov.br"),
        ("MG", "53732", "https://timoteo.camarasempapel.com.br"), ("ES", "56120", "https://marataizes.camarasempapel.com.br"),
        ("ES", "56154", "https://baixoguandu.camarasempapel.com.br"), ("ES", "56774", "https://novavenecia.camarasempapel.com.br"),
        ("MG", "41416", "https://boaesperanca.camarasempapel.com.br"), ("RJ", "58440", "https://itatiaia.camarasempapel.com.br"),
        ("SP", "63690", "https://cruzeiro.camarasempapel.com.br"), ("ES", "56014", "https://afonsoclaudio.camarasempapel.com.br"),
        ("ES", "56430", "https://fundao.camarasempapel.com.br"), ("ES", "57959", "https://vargemalta.camarasempapel.com.br"),
        ("ES", "56073", "https://anchieta.camarasempapel.com.br"), ("RJ", "58750", "https://paraty.camarasempapel.com.br"),
        ("RJ", "58327", "https://portoreal.camarasempapel.com.br"), ("SP", "64670", "https://guararema.camarasempapel.com.br"),
        ("SP", "71978", "https://tremembe.camarasempapel.com.br")]
# nome do tipo na câmara → sigla do painel (as que contam como projeto: PL, PLC, PDL, PRE, PEL)
TIPO_RE = [(r"^projeto de lei complementar", "PLC"), (r"^projeto de lei", "PL"), (r"^projeto de decreto legislativo", "PDL"), (r"^projeto de resolu", "PRE"),
           (r"^(proposta de )?emenda (a|à) lei org[aâ]nica|^projeto de emenda", "PEL"), (r"^indica", "IND"), (r"^pedido de informa|^requerimento de informa", "PINF"),
           (r"^requerimento", "REQ"), (r"^mo[cç][aã]o", "MOC")]
FORA_TIPO = re.compile(r"substitutiv|^emenda(?! (a|à) lei org)|subemenda|veto|parecer|mensagem|executivo|do prefeito|of[ií]cio|ata\b", re.I)
PROJ = {"PL", "PLC", "PDL", "PRE", "PEL"}
SIGLA = {"PL": "PL", "PLC": "PLC", "PDL": "PDL", "PRE": "PR", "PEL": "PELOM"}
FORA = re.compile(r"mesa|executivo|comiss|prefeit|tribunal|minist[ée]rio|defensoria|popular|lideran|bancada|frente", re.I)

def pg(base, q):
    for i in range(3):
        r = get(f"{base}/spl/{q}", headers={**H, "accept": "text/html"}, timeout=120, tentativas=1)
        if r is not None and r.ok: return html.unescape(r.text)
        time.sleep(4 + 4 * i)
    return None

def cards(t):
    """[(nome do cartão, html dos links do cartão)] das páginas por tipo e por autor"""
    partes = re.split(r"<div class='card-title[^>]*>", t)[1:]
    out = []
    for p in partes:
        m = re.match(r"\s*([^<]+?)\s*\((\d+)\)\s*<", p)
        if m: out.append((m.group(1).strip(), p))
    return out

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

def casa_tse(nome, tse, idx):
    k = idx.get(norm(nome)); k = idx.get(limpa(nome)) if k is None else k
    if k is None:
        tt = set(limpa(nome).split())
        cs = [i for i, x in enumerate(tse) if limpa(x[0]) and set(limpa(x[0]).split()) <= tt] or [i for i, x in enumerate(tse) if len(tt & set(limpa(x[1]).split())) >= 2]
        if not cs and len(tt) == 1: cs = [i for i, x in enumerate(tse) if tt <= set(limpa(x[0]).split()) | set(limpa(x[1]).split())]
        if len(cs) == 1: k = cs[0]
    return k

def uma(uf, ue, base):
    stamp = OUT / f"_csp_{ue}.txt"
    if not os.environ.get("REFAZ") and stamp.exists() and (datetime.date.today() - datetime.date.fromisoformat(stamp.read_text().strip())).days < 7:
        return ue, "em dia"
    U = json.load(open(D / "uf" / f"{uf}.json")); m = U["mun"].get(ue)
    if not m: return ue, "município não encontrado"
    tse = m[3]; idx = {}
    for i, x in enumerate(tse): idx.setdefault(norm(x[0]), i); idx.setdefault(limpa(x[0]), i); idx.setdefault(norm(x[1]), i)
    t = pg(base, "consulta-tipo.aspx")
    if not t: return ue, "consulta indisponível"
    tipos = {}   # código → (sigla, anos com proposições)
    for nome, p in cards(t):
        if FORA_TIPO.search(nome): continue
        sg = next((s for r, s in TIPO_RE if re.search(r, nome, re.I)), None)
        if not sg: continue
        for cod in set(re.findall(r"tipo=(\d+)", p)):
            anos = {int(a) for a in re.findall(rf"tipo={cod}&ano_proposicao=(\d{{4}})", p)}
            tipos[cod] = (sg, anos)
    a = pg(base, "consulta-autor.aspx")
    if not a or not tipos: return ue, "sem tipos ou autores"
    autores = []
    for nome, p in cards(a):
        anos = re.findall(r"consulta-producao\.aspx\?autor=(\d+)&ano=(\d{4})", p); nome = re.sub(r"^vereador[a]?\s+|\s*\(Câmara Digital\)\s*", "", nome, flags=re.I).strip(" .")
        if anos and any(int(x) in ANOS for _, x in anos) and not FORA.search(nome): autores.append((nome, anos[0][0], {int(x) for _, x in anos}))
    casados = [n for n, _, _ in autores if casa_tse(n, tse, idx) is not None]
    if not autores or len(casados) < max(3, 0.5 * len(autores)):
        return ue, f"autores não batem com os eleitos ({len(casados)}/{len(autores)}): não gravado"
    dep = {}; sem = []
    for nome, aid, anos_aut in autores:
        if (time.time() - T0) / 60 > MAX_MIN: return ue, "sem tempo (continua na próxima execução)"
        cont = Counter(); props = []; parcial = False
        for ano in ANOS:
            if ano not in anos_aut: continue
            for cod, (sg, anos_tipo) in tipos.items():
                if anos_tipo and ano not in anos_tipo: continue
                r = pg(base, f"consulta-producao.aspx?autor={aid}&tipo={cod}&ano={ano}"); time.sleep(0.5)
                if not r: continue
                n, its = itens(r)
                if not n: continue
                cont[sg] += n
                if sg in PROJ:
                    parcial |= n > len(its)
                    for c, em, dt, tram, au in its:
                        props.append([f"{SIGLA[sg]} {c}", em, dt, tram, 1 if not au or limpa(au[0]) == limpa(nome) else 0])
        if not cont: continue
        k = casa_tse(nome, tse, idx)
        reg = {"nome": nome, "civil": "", "partido": "", "foto": "", "cont": dict(cont),
               "props": sorted(props, key=lambda p: p[2], reverse=True)[:80], "parcial": parcial, "leis": [], "votos": {}, "vlist": [],
               "sapl": f"{base}/spl/consulta-producao.aspx?autor={aid}"}
        if k is None: sem.append(nome); dep["x" + aid] = reg
        else: dep[str(k)] = reg
    if not dep: return ue, "nada coletado"
    cid = m[0].title()
    out = {"fonte": f"Câmara Municipal de {cid} ({uf}) · Processo Legislativo Eletrônico", "url": f"{base}/spl/consulta-autor.aspx", "gerado": datetime.date.today().isoformat(),
           "legislatura": "2025–2028", "temVotos": False, "casa": "Câmara Municipal", "desde": "2025",
           "obs": f"Totais por tipo de proposição como publicados pela Câmara de {cid}. A lista mostra os projetos mais recentes de cada tipo; a consulta da Câmara não publica os votos de cada vereador.",
           "dep": dep}
    json.dump(out, open(OUT / f"{ue}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    stamp.write_text(datetime.date.today().isoformat())
    ex1 = next(iter(dep.values()))
    return ue, {"cidade": m[0], "vereadores": len(dep), "sem_casar": sem, "base": base, "exemplo": [ex1["nome"], ex1["cont"], ex1["props"][:1]]}

def main():
    feitos = []
    so = os.environ.get("PADROES", "").split()   # teste: só os códigos indicados
    ordem = sorted([c for c in CAMS if not so or c[1] in so], key=lambda c: (OUT / f"_csp_{c[1]}.txt").read_text().strip() if (OUT / f"_csp_{c[1]}.txt").exists() else "")
    with cf.ThreadPoolExecutor(4) as ex:
        for ue, r in ex.map(lambda c: uma(*c), ordem):
            print(ue, json.dumps(r, ensure_ascii=False), flush=True)
            if isinstance(r, dict): feitos.append((ue, r))
    if feitos:
        try: I = json.load(open(OUT / "index.json"))
        except Exception: I = {}
        uf_de = {c[1]: c[0] for c in CAMS}
        for ue, r in feitos: I[ue] = [uf_de[ue], r["cidade"], r["base"] + "/spl/", False, r["vereadores"], datetime.date.today().isoformat()]
        json.dump(I, open(OUT / "index.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("câmaras gravadas nesta execução:", len(feitos), flush=True)

if __name__ == "__main__":
    main()
