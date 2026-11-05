"""Sonda 4: arquivos da ALESP; procura APIs escondidas nos sites de GO, SC, CE, BA, RJ (lê o HTML e os scripts)."""
import json, re, concurrent.futures as cf
from pathlib import Path
from urllib.parse import urljoin
import requests
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36", "accept": "*/*"}
def head(u):
    try:
        r = requests.get(u, headers=H, timeout=40, stream=True); n = r.headers.get("content-length"); b = next(r.iter_content(600), b"")
        return {"u": u, "st": r.status_code, "ct": r.headers.get("content-type"), "len": n, "final": r.url, "ini": b[:600].decode("latin-1")}
    except Exception as e: return {"u": u, "erro": type(e).__name__ + str(e)[:80]}
SP = ["https://www.al.sp.gov.br/repositorioDados/processo_legislativo/documento_autor.zip", "https://www.al.sp.gov.br/repositorioDados/processo_legislativo/proposituras.zip",
      "https://www.al.sp.gov.br/repositorioDados/deputados/deputados.xml", "https://www.al.sp.gov.br/repositorioDados/deputados/deputados.zip",
      "https://www.al.sp.gov.br/repositorioDados/processo_legislativo/documento_andamento_atual.zip", "https://www.al.sp.gov.br/dados-abertos/recurso/61"]
SITES = {"GO": ["https://transparencia.al.go.leg.br/", "https://portal.al.go.leg.br/", "https://www.al.go.leg.br/"],
         "SC": ["https://portalelegis.alesc.sc.gov.br/", "https://www.alesc.sc.gov.br/"],
         "CE": ["https://www.al.ce.leg.br/", "https://www.al.ce.gov.br/"], "BA": ["https://www.al.ba.gov.br/", "https://www.al.ba.gov.br/atividade-legislativa/proposicoes"],
         "RJ": ["https://www.alerj.rj.gov.br/", "https://www3.alerj.rj.gov.br/lotus_notes/default.asp", "http://alerjln1.alerj.rj.gov.br/scpro2327.nsf"],
         "MS": ["https://www.al.ms.gov.br/"], "RN": ["https://www.al.rn.leg.br/"], "SE": ["https://al.se.leg.br/"], "DF": ["https://www.cl.df.gov.br/"]}
def scan(item):
    uf, us = item; out = []
    for u in us:
        try:
            r = requests.get(u, headers=H, timeout=30); txt = r.text
            js = [urljoin(r.url, s) for s in re.findall(r'<script[^>]+src="([^"]+)"', txt)][:12]
            apis = set(re.findall(r'https?://[a-zA-Z0-9.\-]+(?:/[a-zA-Z0-9_\-./]*)?(?:api|ws|webservice|odata|dados)[a-zA-Z0-9_\-./]*', txt, re.I))
            for j in js:
                try: apis |= set(re.findall(r'["\'](https?://[^"\']*(?:api|ws/|webservice|odata)[^"\']*)["\']', requests.get(j, headers=H, timeout=20).text, re.I))
                except Exception: pass
            links = [h for h in set(re.findall(r'href="([^"#]+)"', txt)) if re.search(r"propos|projeto|materia|dados|api|leis|deputad", h, re.I)][:60]
            out.append({"u": u, "st": r.status_code, "final": r.url, "apis": sorted(apis)[:60], "links": sorted(links)})
        except Exception as e: out.append({"u": u, "erro": type(e).__name__})
    return uf, out
with cf.ThreadPoolExecutor(12) as ex:
    R = {"sp": list(ex.map(head, SP)), "sites": dict(ex.map(scan, SITES.items()))}
json.dump(R, open(Path(__file__).resolve().parents[1] / "site" / "data" / "_sonda_assembleias.json", "w"), ensure_ascii=False, indent=1)
