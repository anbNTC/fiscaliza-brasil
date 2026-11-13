"""Câmara Municipal de São Paulo: projetos de cada vereador da legislatura 2025–2028 e leis aprovadas.
Fonte: SPLegis, web service aberto da Câmara (https://splegisws.saopaulo.sp.leg.br/ws/ws2.asmx), sem captcha.
1) ProjetosPorAnoJSON (2025 em diante): todas as matérias com tipo, número, data e ementa.
2) ProjetosAutoresJSON: autores de cada projeto (PL, PDL, PR, PLO). Um pedido por projeto, guardado em cache
   (site/data/cam/_cmsp_autores.json) para não repetir; no máximo LIMITE pedidos novos por execução, com pausa entre eles.
3) LeisAprovadasPorPromoventeJSON: leis de cada vereador publicadas desde 2025.
A Câmara não publica votos nominais nesse serviço.
Saída: site/data/cam/71072.json no mesmo formato das câmaras do SAPL (chave = índice do vereador na lista do TSE)."""
import json, os, re, sys, time, datetime
from collections import Counter, defaultdict
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa, norm, H

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "cam"; UE = "71072"
B = "https://splegisws.saopaulo.sp.leg.br/ws/ws2.asmx"
CACHE = OUT / "_cmsp_autores.json"; LIMITE = int(os.environ.get("LIMITE", "1500"))
PROJ = {"PL", "PDL", "PR", "PLO", "PELOM"}
OUTROS = {"IND": "IND", "MOC": "MOC", "REQ": "REQ"}
HOMEN = re.compile(r"denomina|utilidade p[uú]blica|t[ií]tulo de cidad|calend[aá]rio|dia (municipal|do|da)|semana (municipal|do|da)|honra|homenag|medalha|salva de prata", re.I)

def j(u, tent=3):
    for i in range(tent):
        try:
            r = requests.get(f"{B}/{u}", headers={**H, "accept": "application/json"}, timeout=120)
            if r.status_code == 500 and "Missing parameter" in r.text: raise SystemExit("parâmetro faltando em " + u)
            if r.ok:
                try: return r.json()
                except Exception:
                    m = re.search(r">\s*(\[.*\]|\{.*\})\s*<", r.text, re.S)
                    return json.loads(m.group(1)) if m else []
        except SystemExit: raise
        except Exception: pass
        time.sleep(2 + 3 * i)
    return None

def main():
    U = json.load(open(D / "uf" / "SP.json")); tse = U["mun"][UE][3]
    V = j("VereadoresCMSPJSON") or []
    atuais = {}
    for v in V:
        m = [x for x in v.get("mandatos") or [] if (x.get("inicio") or "") >= "2025" and (x.get("fim") or "") >= "2026"]
        if m: atuais[v["chave"]] = {"nome": v["nome"], "partido": ((m[0].get("partido") or {}).get("sigla") or "")}
    print("vereadores na legislatura:", len(atuais), flush=True)
    # matérias de 2025 em diante
    mats = {}
    for ano in range(2025, datetime.date.today().year + 1):
        for p in j(f"ProjetosPorAnoJSON?ano={ano}") or []:
            mats[(p["tipo"], int(p["numero"]), int(p["ano"]))] = [re.sub(r"\s+", " ", p.get("ementa") or "").strip()[:220], (p.get("data") or "")[:10]]
    print("matérias desde 2025:", len(mats), flush=True)
    # autores, com cache
    try: cache = json.load(open(CACHE))
    except Exception: cache = {}
    cache = {k: v for k, v in cache.items() if v and all(c is not None for c, _ in v)}   # consulta sem autor reconhecido: tenta de novo
    novos = 0
    for (tp, n, a) in sorted(mats, key=lambda k: (k[2], k[1]), reverse=True):
        if tp not in PROJ and tp not in OUTROS: continue
        k = f"{tp} {n}/{a}"
        if k in cache: continue
        if novos >= LIMITE: break
        r = j(f"ProjetosAutoresJSON?tipo={tp}&numero={n}&ano={a}")
        if r is None: continue
        aut = [a for x in (r if isinstance(r, list) else []) for a in (x.get("autores") or [])]
        cache[k] = [[a.get("chave"), 1 if i == 0 else 0] for i, a in enumerate(aut) if a.get("chave") is not None]
        novos += 1; time.sleep(0.25)
    json.dump(cache, open(CACHE, "w"), separators=(",", ":"))
    falta = sum(1 for (tp, n, a) in mats if (tp in PROJ or tp in OUTROS) and f"{tp} {n}/{a}" not in cache)
    print("autores: consultados agora", novos, "| sem consulta ainda", falta, flush=True)
    autoria = defaultdict(list)
    for k, aut in cache.items():
        for ch, princ in aut: autoria[ch].append((k, princ))
    # casa com a lista do TSE (nome de urna)
    idx = {}
    for i, x in enumerate(tse): idx.setdefault(norm(x[0]), i); idx.setdefault(limpa(x[0]), i); idx.setdefault(norm(x[1]), i)
    dep = {}; sem = []
    for ch, v in atuais.items():
        k = idx.get(norm(v["nome"])); k = idx.get(limpa(v["nome"])) if k is None else k
        cont = Counter(); props = []
        for kk, princ in sorted(autoria.get(ch, []), key=lambda t: (mats.get(_chave(t[0])) or ["", ""])[1], reverse=True):
            tp = kk.split()[0]; cont[tp] += 1
            if tp in PROJ:
                em, dt = mats.get(_chave(kk)) or ["", ""]
                props.append([kk, em, dt, 0, princ])
        leis = []
        for l in j(f"LeisAprovadasPorPromoventeJSON?codigo={ch}") or []:
            pub = (l.get("publicacao") or "")[:10]
            if pub < "2025": continue
            pr = l.get("projeto") or {}; em = re.sub(r"\s+", " ", pr.get("ementa") or "").strip()
            leis.append([str(l.get("numero")), pub[:4], em[:220], 1 if HOMEN.search(em) else 0, 1, pub])
        time.sleep(0.25)
        reg = {"nome": v["nome"].title(), "civil": "", "partido": v["partido"], "foto": "", "cont": dict(cont), "props": props[:80], "parcial": len(props) > 80,
               "leis": sorted(leis, key=lambda x: x[5], reverse=True), "votos": {}, "vlist": [], "sapl": "https://www.saopaulo.sp.leg.br/vereadores/membros"}
        if k is None: sem.append(v["nome"]); dep["x" + str(ch)] = reg
        else: dep[str(k)] = reg
    out = {"fonte": "Câmara Municipal de São Paulo (SP) · SPLegis, dados abertos", "url": "https://splegisconsulta.saopaulo.sp.leg.br/", "gerado": datetime.date.today().isoformat(),
           "legislatura": "2025–2028", "temVotos": False, "casa": "Câmara Municipal", "desde": "2025",
           "obs": "A Câmara de São Paulo publica em dados abertos as matérias, os autores e as leis, mas não os votos nominais de cada vereador. A situação de cada projeto (em tramitação, arquivado) não vem nesse serviço; consulte o SPLegis pelo número.",
           "dep": dep}
    if falta: out["obs"] += f" Lista ainda em montagem: faltam os autores de {falta} matérias, que entram nos próximos dias."
    json.dump(out, open(OUT / f"{UE}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    try: I = json.load(open(OUT / "index.json"))
    except Exception: I = {}
    I[UE] = ["SP", "SÃO PAULO", "https://splegisconsulta.saopaulo.sp.leg.br/", False, len(dep), datetime.date.today().isoformat()]
    json.dump(I, open(OUT / "index.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("gravado:", len(dep), "vereadores;", len(sem), "sem casar com o TSE:", sem, flush=True)

def _chave(k):
    tp, rest = k.split(" ", 1); n, a = rest.split("/"); return (tp, int(n), int(a))

if __name__ == "__main__":
    main()
