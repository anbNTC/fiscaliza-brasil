"""ALEP (Paraná): proposições e leis de cada deputado estadual desde 2023, pela API pública da Assembleia.
API: http://webservices.assembleia.pr.leg.br/api/public (só HTTP: o HTTPS tem certificado inválido).
O filtro de tipo da API é ignorado: um pedido por ano traz tudo.
Votos ficam em PDFs atrás de reCAPTCHA: não coletamos (o site diz isso).
Saída: site/data/est/PR.json no mesmo formato das outras Assembleias, mais "leis" = [[número, ano, ementa, homenagem 0/1, autor principal 0/1, data]]."""
import json, re, sys, time, html, datetime
from collections import Counter
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa, norm

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "est"; OUT.mkdir(exist_ok=True)
WS = "http://webservices.assembleia.pr.leg.br/api/public"
SITE = "https://www.assembleia.pr.leg.br"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json"}
ANOS = range(2023, datetime.date.today().year + 1)
TIPO = {"PROJETO DE LEI": "PL", "PROJETO DE LEI COMPLEMENTAR": "PLC", "PROPOSTA DE EMENDA À CONSTITUIÇÃO": "PEC", "PROPOSTA DE EMENDA A CONSTITUICAO": "PEC",
        "PROJETO DE RESOLUÇÃO": "PRE", "PROJETO DE RESOLUCAO": "PRE", "PROJETO DECRETO LEGISLATIVO": "PDL", "PROJETO DE DECRETO LEGISLATIVO": "PDL",
        "REQUERIMENTO": "REQ", "INDICAÇÃO": "IND", "INDICACAO": "IND", "MOÇÃO": "MOC", "MOCAO": "MOC", "PEDIDO DE INFORMAÇÃO": "PINF", "PEDIDO DE INFORMACAO": "PINF"}
PROJ = {"PL", "PLC", "PEC", "PRE", "PDL"}
HOMENAGEM = re.compile(r"UTILIDADE PUBLICA|DENOMINA|TITULOS? HONORIFICOS?|CIDADAO HONORARIO|^DATA$|DATAS COMEMORATIVAS|CALENDARIO")
FIM = re.compile(r"arquiv|rejeit|retirad|sancion|promulg|vetad|prejudic|transformad", re.I)
# nome no site da ALEP ≠ nome usado como autor na API
ALIAS = {"luis-raimundo-corti": "LUIS RAIMUNDO CORTI", "arilson-maroldi-chiorato": "ARILSON CHIORATO", "doutor-antenor": "DR ANTENOR",
         "pedro-paulo-bazana": "BAZANA", "marcia-huculak": "SECRETARIA MARCIA", "thiago-buehrer": "THIAGO BUHRER",
         "artagao-junior": "ARTAGAO JUNIOR", "tito-barichello": "DELEGADO TITO BARICHELLO"}
S = requests.Session(); S.headers.update(H)

def post(u, body):
    for k in range(4):
        try:
            r = S.post(u, json=body, timeout=180)
            if r.ok: return r.json()
            print(u, body, r.status_code, flush=True)
        except Exception as e: print(u, body, repr(e)[:120], flush=True)
        time.sleep(5 * (k + 1))
    return {"lista": []}

def deputados():
    t = S.get(f"{SITE}/deputados/conheca", timeout=60, headers={"accept": "text/html"}).text
    out, vistos = [], set()
    for slug, bloco in re.findall(r'href="https://www\.assembleia\.pr\.leg\.br/deputados/perfil/([a-z0-9-]+)"[^>]*>(.*?)</a>', t, re.S):
        if slug in vistos: continue
        vistos.add(slug); txt = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(bloco)).split()); partes = txt.split(" ")
        if len(partes) < 2: continue
        partido = partes.pop(); nome = re.sub(r"^(PRESIDENTE|\d+º (SECRETÁRIO|SECRETÁRIA|VICE-PRESIDENTE)|DEPUTADO|DEPUTADA)\s+", "", " ".join(partes))
        foto = re.search(r'<img[^>]+src="([^"]+)"', bloco)
        out.append({"slug": slug, "nome": nome, "partido": partido, "key": ALIAS.get(slug, norm(nome)), "foto": foto.group(1) if foto else ""})
    return out

def autores(s): return [norm(re.sub(r"DEPUTAD[OA]", "", a)) for a in (s or "").split(",") if a.strip()]

def main():
    ald = deputados(); print(len(ald), "deputados na página da ALEP", flush=True)
    if len(ald) < 40: raise RuntimeError("lista de deputados da ALEP incompleta")
    by = {d["key"]: d for d in ald}; R = {d["slug"]: {"cont": Counter(), "props": [], "leis": []} for d in ald}
    vistos = set(); nprop = nlei = 0
    for ano in ANOS:
        L = post(f"{WS}/proposicao/filtrar", {"ano": ano, "tipo": 1}).get("lista") or []
        for x in L:
            if x.get("codigo") in vistos: continue
            vistos.add(x.get("codigo")); nprop += 1
            tp = TIPO.get((x.get("tipoProposicao") or "").upper().strip())
            if not tp: continue
            au = autores(x.get("autor"))
            for i, a in enumerate(au):
                d = by.get(a)
                if not d: continue
                r = R[d["slug"]]; r["cont"][tp] += 1
                if tp in PROJ:
                    r["props"].append([f"{tp} {x.get('numero')}/{x.get('ano')}", (x.get("ementa") or "").strip()[:220], (x.get("dataRecebimento") or "")[:10],
                                       0 if FIM.search(x.get("status") or "") else 1, 1 if i == 0 else 0, len(au)])
        LL = post(f"{WS}/norma-legal/filtrar", {"ano": ano}).get("lista") or []
        for x in LL:
            if not (x.get("descricaoTipoNormaLegal") or "").startswith("Lei"): continue
            nlei += 1; au = autores(x.get("autores"))
            for i, a in enumerate(au):
                d = by.get(a)
                if d: R[d["slug"]]["leis"].append([x.get("numero"), ano, (x.get("ementa") or "").strip()[:220], 1 if HOMENAGEM.search(norm(x.get("assunto") or "")) else 0, 1 if i == 0 else 0, (x.get("data") or "")[:10]])
        print(ano, len(L), "proposições,", len(LL), "normas", flush=True); time.sleep(1)
    if nprop < 1000: raise RuntimeError(f"poucas proposições da ALEP ({nprop}); não grava")
    U = json.load(open(D / "uf" / "PR.json")); de = U.get("de22", [])
    idx = {}
    for k, x in enumerate(de): idx.setdefault(limpa(x[0]), k); idx.setdefault(limpa(x[1]), k)
    toks = [(k, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for k, x in enumerate(de)]
    dep = {}; sem = []
    for d in ald:
        r = R[d["slug"]]; k = idx.get(limpa(d["nome"])) if limpa(d["nome"]) else None
        if k is None:
            tt = set(limpa(d["nome"]).split())
            best = sorted(((len(tt & q) / max(1, min(len(tt), len(q))), len(tt & q), j) for j, q in toks), reverse=True)
            if tt and best and best[0][0] >= 0.99 and (len(best) < 2 or best[1][:2] < best[0][:2]): k = best[0][2]
        reg = {"nome": d["nome"].title(), "civil": "", "partido": d["partido"], "foto": d["foto"], "cont": dict(r["cont"]),
               "props": sorted(r["props"], key=lambda p: p[2], reverse=True)[:120], "votos": {}, "vlist": [],
               "leis": sorted(r["leis"], key=lambda l: (l[5] or str(l[1])), reverse=True), "sapl": f"{SITE}/deputados/perfil/{d['slug']}"}
        if k is None: sem.append(d["nome"]); dep["x" + d["slug"]] = reg
        else: dep[str(k)] = reg
    out = {"fonte": "Assembleia Legislativa do Paraná (ALEP) · API pública", "url": SITE, "gerado": datetime.date.today().isoformat(),
           "legislatura": "20ª legislatura (2023–2027)", "temVotos": False,
           "obs": "A ALEP publica os votos de cada deputado só em PDFs protegidos por reCAPTCHA, fora do formato de dados abertos. Por isso não aparecem aqui.", "dep": dep}
    json.dump(out, open(OUT / "PR.json", "w"), ensure_ascii=False, separators=(",", ":"))
    r = {"deputados": len(ald), "ligados": len(ald) - len(sem), "proposicoes": nprop, "leis": nlei, "sem_par": sem[:10]}
    print(json.dumps(r, ensure_ascii=False)); return r

if __name__ == "__main__":
    main()
