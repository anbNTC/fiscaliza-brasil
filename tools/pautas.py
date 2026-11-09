"""Pautas para vídeos: os fatos mais fortes da semana, a partir dos dados do próprio site (sem opinião, só números com fonte).
Foco no Paraná (UF_FOCO), mais as votações nacionais. Saída: site/data/pautas.json
  {"gerado", "itens": [{"tipo", "titulo", "texto", "link", "fonte", "peso"}]}  (link = rota do site; o card fica na página aberta)"""
import json, os, datetime
from pathlib import Path
D = Path(__file__).resolve().parents[1] / "site" / "data"
UF = os.environ.get("UF_FOCO", "PR")
rd = lambda p, padrao=None: json.load(open(D / p)) if (D / p).exists() else padrao
brl = lambda v: ("R$ " + f"{v / 1e6:.1f}".replace(".", ",") + " milhões") if v >= 1e6 else ("R$ " + f"{v:,.0f}".replace(",", "."))
dt = lambda d: "/".join(reversed(d.split("-")))
itens = []
def add(tipo, titulo, texto, link, fonte, peso): itens.append({"tipo": tipo, "titulo": titulo, "texto": texto, "link": link, "fonte": fonte, "peso": round(peso, 1)})

BR = rd("br.json"); S = rd("semana.json", {"semanas": []}); VC = rd("camara_votacoes.json", []); VS = rd("senado_votacoes.json", [])
nomeDep = {str(d[0]): d for d in BR["dep"]}
semanas = S["semanas"][:2]  # esta semana e a anterior

# 1) votações: apertadas e PECs, com link para "como votou o PR"
for w in semanas:
    for casa, L, VL in (("C", w["c"], VC), ("S", w["s"], VS)):
        for i in L:
            x = VL[i]; C = casa == "C"
            sim, nao = (x[3], x[4]) if C else (x[7], x[8]); tit = (x[5] if C else x[2]) or "Votação"; em = (x[6] or x[7]) if C else (x[3] or x[4])
            if not C and x[6] == "S": continue
            oq = str((x[7] if C else x[4]) or "")
            if "requerimento" in oq.lower(): continue
            tot = (sim or 0) + (nao or 0)
            if not tot: continue
            marg = abs(sim - nao) / tot; pec = tit.startswith("PEC"); apr = (x[2] == "1") if C else (x[5] == "A")
            peso = 50 * (1 - marg) + (25 if pec else 0) + (10 if tot > 400 else 0)
            oc = oq.split(". ")[0][:150]
            add("votacao", f"{tit} {'na Câmara' if C else 'no Senado'}, {sim} a {nao}: {oc.rstrip('.')}. Veja como votou cada {'deputado' if C else 'senador'} do {UF}",
                f"{dt(x[1])}. O que foi votado: {oq[:200]} Tema: {str(em)[:160]}", f"#/votacao/{casa}/{i}/{UF}", "Câmara/Senado · Dados Abertos", peso)

# 2) quem votou contra o próprio partido e quem faltou (foco no estado)
for w in semanas[:1]:
    for c in w.get("contra", []):
        if c[4] != UF: continue
        add("contra", f"{c[2]} ({c[3]}-{c[4]}) votou contra o próprio partido {c[5]} vez{'es' if c[5] > 1 else ''} nesta semana",
            "Voto diferente da maioria da bancada do partido nas votações nominais do Plenário.", f"#/p/{'c' if c[0] == 'C' else 's'}/{c[1]}", "Câmara/Senado · Dados Abertos", 30 + 5 * c[5])
    for c in w.get("falt", []):
        if c[4] != UF: continue
        add("falta", f"{c[2]} ({c[3]}-{c[4]}) não registrou voto em {c[5]} de {c[6]} votações da semana",
            "Os dados abertos não dizem o motivo (pode ser licença, missão oficial ou ausência). Vale perguntar ao gabinete antes de publicar.", f"#/p/{'c' if c[0] == 'C' else 's'}/{c[1]}", "Câmara/Senado · Dados Abertos", 25 + 3 * c[5])

# 3) cota parlamentar: gasto no topo e fornecedor único com fatia grande
M = rd("cota_media.json", {}); CC = rd(f"c/{UF}.json", {})
for k, X in CC.items():
    co = X.get("cota") if X else None; d = nomeDep.get(k)
    if not co or not d: continue
    tot = sum(sum(t.values()) for t in co["a"].values()); p90 = (M.get("C") or {}).get("p90")
    if p90 and tot >= p90: add("cota", f"{d[1]} ({d[2]}-{UF}) está entre os 10% de deputados que mais gastaram a cota parlamentar: {brl(tot)} desde 2023",
                               f"Gasto típico (mediana) na Câmara: {brl(M['C']['mediana'])}.", f"#/p/c/{k}", "Câmara · Dados Abertos (cota parlamentar)", 35 + 10 * (tot / p90 - 1))
    f0 = next((f for f in co.get("f", []) if f[0]), None)
    if f0 and tot and f0[1] / tot >= 0.3: add("cota", f"{round(100 * f0[1] / tot)}% da cota de {d[1]} ({d[2]}-{UF}) foi para um só fornecedor",
                                          f"{f0[0].title()} recebeu {brl(f0[1])} de um total de {brl(tot)} desde 2023.", f"#/p/c/{k}", "Câmara · Dados Abertos (cota parlamentar)", 30 + 30 * f0[1] / tot)

# 4) emendas grandes para cidades pequenas (tamanho pelo nº de votos para deputado federal na cidade em 2022, dado do TSE)
U = rd(f"uf/{UF}.json", {}); E = rd(f"emendas/{UF}.json", {}); VMm = (rd(f"vm/{UF}.json", {}) or {}).get("mun", {}); peq = {}
norm = lambda s: __import__("unicodedata").normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
for ue, m in (U.get("mun") or {}).items():
    vf = ((VMm.get(ue) or {}).get("2022") or {}).get("F")
    if vf and vf[1] < 12000: peq[norm(m[0])] = (ue, m[0], vf[1])
cand = []
for cid, L in (E.get("cid") or {}).items():
    if norm(cid) not in peq: continue
    for a in L:
        if a[0] in ("C", "S") and a[4] >= 2e6: cand.append((a[4], cid, a))
for v, cid, a in sorted(cand, reverse=True)[:6]:
    ue, nm, nv = peq[norm(cid)]
    add("emenda", f"{a[2]} ({a[3]}) mandou {brl(v)} em emendas para {nm.title()}, cidade onde {nv:,} pessoas votaram para deputado federal".replace(",", "."),
        "Valor pago desde 2023, pelo favorecido na cidade. Vale ver no Portal da Transparência para que serviu.", f"#/cidade/{UF}/{ue}", "Portal da Transparência (CGU) · TSE", 28 + v / 1e6)

# 5) doadores: maior doador pessoa física da campanha de 2022 dos eleitos do estado (quando a coleta do TSE já rodou)
CP = rd(f"camp/{UF}.json", {}).get("dep", {}) if rd(f"camp/{UF}.json") else {}
VM = (rd(f"vm/{UF}.json", {}) or {}).get("anos", {}).get("2022", {})
civ = {norm(d[5]): f"#/p/c/{d[0]}" for d in BR["dep"]}; civ.update({norm(x[2]): f"#/p/s/{x[0]}" for x in BR["sen"]})
for cg, rot in (("F", "deputado federal"), ("S", "senador")):
    for c in VM.get(cg, []):
        e = CP.get(c[4]) if c[3] else None
        if not e or not e.get("d"): continue
        pf = [x for x in e["d"] if not any(w in x[0].upper() for w in ("PARTIDO", "DIRETORIO", "DIRETÓRIO", "COMISSAO", "FUNDO", "ELEICAO", "ELEIÇÃO", norm(c[1])[:12]))]
        if pf and pf[0][1] >= 100000:
            add("doador", f"{pf[0][0].title()} doou {brl(pf[0][1])} para a campanha de {c[0].title()} ({c[2]}), {rot} eleito pelo {UF} em 2022",
                f"Campanha arrecadou {brl(e['c'][0])} no total. Doação de pessoa física é legal até 10% da renda do doador; o dado mostra quem financia, não irregularidade.", civ.get(norm(c[1]), ""), "TSE · prestação de contas", 30 + pf[0][1] / 1e5)

vis = set(); itens = [i for i in sorted(itens, key=lambda x: -x["peso"]) if not (i["titulo"] in vis or vis.add(i["titulo"]))]
json.dump({"gerado": datetime.date.today().isoformat(), "uf": UF, "itens": itens[:40]}, open(D / "pautas.json", "w"), ensure_ascii=False, indent=0)
print("pautas:", len(itens), {t: sum(1 for i in itens if i["tipo"] == t) for t in {i["tipo"] for i in itens}})
