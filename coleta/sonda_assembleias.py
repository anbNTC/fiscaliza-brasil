"""Sonda 2: lê as páginas de dados abertos e lista os links de dados; testa endpoints do SAPL (votos, autoria) e da ALESP."""
import json, re, concurrent.futures as cf
from pathlib import Path
import requests
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json, text/xml, */*"}
PAGS = {"SP": "https://www.al.sp.leg.br/dados-abertos", "BA": "https://www.al.ba.leg.br/dados-abertos", "CE": "https://www.al.ce.leg.br/dados-abertos",
        "GO": "https://www.al.go.leg.br/dados-abertos", "PA": "https://www.al.pa.leg.br/dados-abertos", "RJ": "https://www.al.rj.leg.br/dados-abertos",
        "SC": "https://www.al.sc.leg.br/dados-abertos", "MT": "https://www.al.mt.leg.br/dados-abertos", "AC": "https://www.al.ac.leg.br/dados-abertos"}
SAPL = "AC AL AM MT PB PI RO TO".split()
T = []
for uf in SAPL:
    b = f"https://sapl.al.{uf.lower()}.leg.br/api"
    T += [f"{b}/", f"{b}/parlamentares/parlamentar/?page_size=2", f"{b}/materia/materialegislativa/?page_size=2&ano=2025", f"{b}/materia/autoria/?page_size=2",
          f"{b}/sessao/votoparlamentar/?page_size=2", f"{b}/sessao/registrovotacao/?page_size=2", f"{b}/parlamentares/mandato/?page_size=2", f"{b}/parlamentares/legislatura/?page_size=3"]
T += ["https://www.al.sp.leg.br/repositorioDados/deputados/deputados.xml", "https://www.al.sp.leg.br/repositorioDados/processo_legislativo/proposituras.zip",
      "https://www.al.sp.leg.br/api/deputado", "https://www.al.sp.leg.br/repositorioDados/processo_legislativo/documento_autor.zip"]
def get(u, n=3000):
    try:
        r = requests.get(u, headers=H, timeout=25)
        return {"u": u, "st": r.status_code, "ct": r.headers.get("content-type", ""), "n": len(r.content), "ini": r.text[:n] if "zip" not in r.headers.get("content-type", "") else ""}
    except Exception as e: return {"u": u, "erro": type(e).__name__}
def links(item):
    uf, u = item
    try:
        r = requests.get(u, headers=H, timeout=25); hs = sorted(set(re.findall(r'href="([^"#]+)"', r.text)))
        return {"uf": uf, "u": u, "links": [h for h in hs if re.search(r"(api|json|csv|xml|zip|dados|webservice|ws/|swagger|odata|download)", h, re.I)][:120]}
    except Exception as e: return {"uf": uf, "u": u, "erro": type(e).__name__}
with cf.ThreadPoolExecutor(16) as ex:
    R = {"paginas": list(ex.map(links, PAGS.items())), "testes": list(ex.map(get, T))}
json.dump(R, open(Path(__file__).resolve().parents[1] / "site" / "data" / "_sonda_assembleias.json", "w"), ensure_ascii=False, indent=1)
print("ok")
