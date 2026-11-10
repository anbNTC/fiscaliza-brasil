"""Câmara Municipal de Curitiba (CMC): perfil dos vereadores e contagem da atividade de cada um (2025 em diante).
Fontes: API do site (https://www.cmc.pr.gov.br/++api++) e o Painel de Atividades Legislativas da CMC (publicado no Infogram).
O sistema de proposições (SPL) exige captcha: sem lista de projetos nem votos (o site diz isso e aponta a fonte).
Saída: site/data/cam/75353.json no mesmo formato das Câmaras com SAPL (chave = índice do vereador em uf/PR.json, mun 75353)."""
import json, re, sys, time, datetime
from collections import Counter
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "cam"; OUT.mkdir(exist_ok=True)
BASE = "https://www.cmc.pr.gov.br"; UE = "75353"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
PAINEL = f"{BASE}/++api++/atividade-parlamentar/painel-de-atividades-legislativas"
# painéis conhecidos (o coletor também procura novos na página do painel)
PAINEIS = {"2026": "9fdfe2f1-3fa7-4b94-93d4-35395d20ed25", "2025": "54e229cd-2665-48cf-8933-a0641a7f2cb0"}
S = requests.Session(); S.headers.update(H)
import saida_br  # a CMC só responde a acessos do Brasil
FORA = {"conheca-os-vereadores", "liderancas-e-blocos-parlamentares", "lista-de-presenca", "mesa-diretora", "corregedoria", "frentes-parlamentares", "representacao-externa"}

def get(u, js=True):
    for k in range(4):
        try:
            r = saida_br.get(u, headers={"accept": "application/json" if js else "text/html", "user-agent": H["user-agent"]}, timeout=90, tentativas=1)
            if r is not None and r.status_code == 404: return None
            if r is not None and r.ok: return r.json() if js else r.text
            print(u, r.status_code if r is not None else "sem resposta", flush=True)
        except Exception as e: print(u, repr(e)[:100], flush=True)
        time.sleep(3 * (k + 1))
    return None

def val(x, k="title"): return (x.get(k) or x.get("token") or "") if isinstance(x, dict) else (x or "")

def vereadores():
    t = get(f"{BASE}/vereadores/conheca-os-vereadores", js=False) or ""
    out = []
    for s in dict.fromkeys(re.findall(r'/vereadores/([a-z0-9-]+)"', t)):
        if s in FORA: continue
        j = get(f"{BASE}/++api++/vereadores/{s}")
        if not j or j.get("@type") != "vereador" or j.get("ex_vereador"): continue
        foto = ""
        for k in ("foto", "image", "imagem"):
            im = j.get(k)
            if isinstance(im, dict): foto = (im.get("scales", {}).get("preview", {}) or {}).get("download") or im.get("download") or ""
            if foto: break
        out.append({"slug": s, "nome": j["title"], "civil": j.get("nome_civil") or "", "partido": val(j.get("partido")).split(" - ")[0].strip(),
                    "licenciado": bool(j.get("licenciado")), "foto": foto})
        time.sleep(0.3)
    return out

def paineis():
    P = dict(PAINEIS)
    j = get(PAINEL)
    if j:
        txt = json.dumps(j)
        for uid in re.findall(r"infogram\.com/(?:[^\"/]*?)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", txt):
            if uid not in P.values():
                m = re.search(r"(20\d\d)[^\"]{0,200}" + uid, txt)
                if m and m.group(1) not in P: P[m.group(1)] = uid
    return P

def tabelas(uid):
    h = S.get(f"https://e.infogram.com/{uid}?src=embed", timeout=60).text
    m = re.search(r"window\.infographicData\s*=\s*(\{.*?\});\s*</script>", h, re.S)
    c = json.loads(m.group(1))["elements"]["content"]["content"]; ents = c["entities"]; out = []
    for b in c["blocks"].values():
        ids = b.get("entities") or []
        textos = [{"t": " ".join(x["text"] for x in ents[i]["props"]["content"]["blocks"]).strip(), "top": ents[i].get("top", 0), "left": ents[i].get("left", 0)}
                  for i in ids if ents.get(i, {}).get("props", {}).get("content", {}).get("blocks")]
        for i in ids:
            e = ents.get(i, {})
            if not e.get("props", {}).get("chartData"): continue
            for sh in e["props"]["chartData"]["data"]:
                rows = [[(x or {}).get("value", "") for x in (r or [])] for r in sh]
                cand = sorted([t for t in textos if t["top"] <= e.get("top", 0) and abs(t["left"] - e.get("left", 0)) < 120 and len(t["t"]) > 5 and not re.search("Clique|Obs|Type", t["t"])], key=lambda t: -t["top"])
                extra = " / ".join(t["t"] for t in textos if re.search(r"vereadores - (individual|coletivos)|individual", t["t"]))
                out.append({"title": cand[0]["t"] if cand else extra, "rows": rows})
    return out

def contagens(T):
    r = {}
    def add(nome, k, v):
        nome = nome.strip()
        if not nome or re.search(r"Comiss|Mesa|Vereador/|Iniciativa|Total", nome, re.I): return
        r.setdefault(nome, Counter())[k] += v
    acha = lambda rx: next((t for t in T if re.search(rx, t["title"])), None)
    n = lambda v: int(re.sub(r"\D", "", str(v)) or 0)
    for rx, k in [(r"^Requerimentos à Prefeitura", "REQP"), (r"^Requerimentos a outros", "REQ"), (r"^Indicação", "IND"), (r"^Pedidos de informação", "PINF")]:
        t = acha(rx)
        if t:
            for row in t["rows"][1:]: add(row[0], k, n(row[1]))
    for rx, k, col in [("individual", "PLI", False), ("coletivos", "PCOL", True)]:
        t = acha(rx)
        if not t: continue
        h = t["rows"][0]
        for row in t["rows"][1:]:
            s = sum(n(v) for i, v in enumerate(row[1:]) if re.match(r"^[A-Z]{3,4}$", h[i + 1] or ""))
            for nome in (row[0].split(",") if col else [row[0]]): add(nome, k, s)
    return r

def main():
    V = vereadores(); print(len(V), "vereadores no site da CMC", flush=True)
    if len(V) < 30: raise RuntimeError("lista de vereadores da CMC incompleta")
    anos = {}
    for ano, uid in sorted(paineis().items()):
        try: anos[ano] = contagens(tabelas(uid)); print(ano, len(anos[ano]), "nomes no painel", flush=True)
        except Exception as e: print(ano, "painel falhou:", repr(e)[:150], flush=True)
    U = json.load(open(D / "uf" / "PR.json")); vs = (U["mun"][UE][3] or [])
    idx = {}
    for k, x in enumerate(vs):
        for nm in (x[0], x[1]): idx.setdefault(limpa(nm), k)
    toks = [(k, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for k, x in enumerate(vs)]
    def acha(*nomes):
        for nm in nomes:
            if nm and limpa(nm) in idx: return idx[limpa(nm)]
        tt = set(limpa(nomes[0]).split())
        best = sorted(((len(tt & q) / max(1, min(len(tt), len(q))), len(tt & q), j) for j, q in toks), reverse=True)
        if tt and best and best[0][0] >= 0.99 and (len(best) < 2 or best[1][:2] < best[0][:2]): return best[0][2]
    def cont_de(v):
        tt = set(limpa(v["nome"]).split()); tot = Counter(); por = {}
        for ano, C in anos.items():
            for nm, c in C.items():
                q = set(limpa(nm).split())
                if q and (limpa(nm) == limpa(v["nome"]) or (q <= tt and len(q) >= 2) or (tt <= q and len(tt) >= 2)):
                    tot.update(c); por[ano] = dict(Counter(por.get(ano, {})) + c)
        return tot, por
    dep = {}; sem = []
    for v in V:
        k = acha(v["nome"], v["civil"]); tot, por = cont_de(v)
        reg = {"nome": v["nome"], "civil": v["civil"], "partido": v["partido"], "foto": v["foto"], "cont": dict(tot), "anos": por, "props": [], "votos": {}, "vlist": [],
               "sapl": f"{BASE}/vereadores/{v['slug']}", "licenciado": v["licenciado"]}
        if k is None: sem.append(v["nome"]); dep["x" + v["slug"]] = reg
        else: dep[str(k)] = reg
    ult = max(anos) if anos else ""
    out = {"fonte": "Câmara Municipal de Curitiba (PR) · site oficial e Painel de Atividades Legislativas", "url": f"{BASE}/atividade-parlamentar/painel-de-atividades-legislativas",
           "gerado": datetime.date.today().isoformat(), "legislatura": "19ª legislatura (2025–2028)", "temVotos": False, "casa": "Câmara Municipal", "desde": "2025",
           "obs": "A Câmara de Curitiba publica a lista de projetos e os votos de cada vereador só no sistema de proposições, que exige captcha. Por isso aqui aparecem as contagens do Painel de Atividades da própria Câmara, sem a lista de projetos nem os votos.",
           "dep": dep}
    json.dump(out, open(OUT / f"{UE}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    r = {"vereadores": len(V), "ligados": len(V) - len(sem), "anos": sorted(anos), "com_contagem": sum(1 for x in dep.values() if x["cont"]), "sem_par": sem[:8]}
    print(json.dumps(r, ensure_ascii=False)); return r

if __name__ == "__main__":
    main()
