"""Câmaras Municipais com SAPL público (sistema do Interlegis): vereadores da legislatura 2025–2028, matérias que apresentaram
e, onde a Câmara registra, o voto nominal de cada vereador.
1) Procura o SAPL de cada uma das 5.568 cidades nos endereços usuais do Interlegis (sapl.<cidade>.<uf>.leg.br e variações).
2) Coleta as que têm matérias ou votos desde 2025.
Sem captcha nem bloqueio: só a API pública do SAPL.
Saída: site/data/cam/{código TSE da cidade}.json (mesmo formato de est/{UF}.json; chave = índice do vereador na lista do TSE
       ou "x"+id para quem não está entre os eleitos de 2024) e site/data/cam/index.json {ue: [uf, nome, url, temVotos, n_vereadores]}"""
import json, os, re, sys, time, datetime, unicodedata, concurrent.futures as cf
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import SAPL, coleta_sapl, H

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "cam"; OUT.mkdir(exist_ok=True)
DESDE = "2025-01-01"; ANOS = range(2025, datetime.date.today().year + 1)
PADROES = ["https://sapl.{s}.{u}.leg.br", "https://sapl.camara{s}.{u}.gov.br", "https://sapl.cm{s}.{u}.gov.br", "https://sapl.{s}.{u}.gov.br", "https://sapl.camara{s}.{u}.leg.br"]
MIN_CIDADE = float(os.environ.get("MIN_CIDADE", "14")); MAX_TOTAL = float(os.environ.get("MAX_TOTAL", "45")) * 60
slug = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())

def sonda(a):
    uf, ue, nome = a[:3]
    for pd in PADROES:
        b = pd.format(s=slug(nome), u=uf.lower())
        try:
            r = requests.get(f"{b}/api/materia/materialegislativa/", params={"ano": 2025, "page_size": 1}, headers=H, timeout=12)
            if r.status_code != 200 or "json" not in r.headers.get("content-type", ""): continue
            mat = r.json().get("pagination", {}).get("total_entries") or 0
            v = requests.get(f"{b}/api/sessao/votoparlamentar/", params={"page_size": 1, "o": "-id"}, headers=H, timeout=12).json()
            ult = (v.get("results") or [{}])[0].get("data_hora") or ""
            return {"uf": uf, "ue": ue, "nome": nome, "base": b, "mat": mat, "voto": ult >= DESDE}
        except Exception: continue
    return None

def main():
    t0 = time.time(); alvos = []; TSE = {}
    for f in sorted((D / "uf").glob("*.json")):
        U = json.load(open(f))
        for ue, m in U.get("mun", {}).items(): alvos.append((f.stem, ue, m[0])); TSE[ue] = m[3]
    with cf.ThreadPoolExecutor(96) as ex: achou = [x for x in ex.map(sonda, alvos) if x]
    ativas = sorted([x for x in achou if x["mat"] or x["voto"]], key=lambda x: -x["mat"])
    print(len(achou), "câmaras com SAPL;", len(ativas), "com matérias ou votos desde 2025", flush=True)
    idx = {}
    try: idx = json.load(open(OUT / "index.json"))
    except Exception: pass
    def um(x):
        if time.time() - t0 > MAX_TOTAL: return x, {"erro": "sem tempo"}
        A = SAPL(base=x["base"], lim_min=MIN_CIDADE)
        r = coleta_sapl(A, TSE.get(x["ue"], []), DESDE, ANOS)
        if "erro" in r: return x, r
        out = {"fonte": f"Câmara Municipal de {x['nome'].title()} ({x['uf']}) · SAPL, dados abertos", "url": x["base"], "gerado": datetime.date.today().isoformat(),
               "legislatura": r["leg"].get("__str__"), "temVotos": bool(r["vp"]), "casa": "Câmara Municipal", "dep": r["dep"]}
        if not r["dep"]: return x, {"erro": "sem vereadores na legislatura atual"}
        json.dump(out, open(OUT / f"{x['ue']}.json", "w"), ensure_ascii=False, separators=(",", ":"))
        idx[x["ue"]] = [x["uf"], x["nome"], x["base"], bool(r["vp"]), len(r["dep"])]
        return x, {"vereadores": len(r["parl"]), "ligados": len(r["parl"]) - len(r["sem"]), "materias": len(r["mats"]), "votos": len(r["vp"])}
    with cf.ThreadPoolExecutor(8) as ex: R = list(ex.map(um, ativas))
    json.dump(idx, open(OUT / "index.json", "w"), ensure_ascii=False, separators=(",", ":"))
    for x, r in R: print(x["uf"], x["nome"], json.dumps(r, ensure_ascii=False), flush=True)
    print(json.dumps({"camaras": len(idx), "com_votos": sum(1 for v in idx.values() if v[3]), "min": round((time.time() - t0) / 60, 1)}))

if __name__ == "__main__":
    main()
