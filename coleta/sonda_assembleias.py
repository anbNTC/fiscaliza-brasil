"""Sonda: testa endereços de dados abertos das 27 Assembleias (e do sistema SAPL do Interlegis) e grava o que respondeu."""
import json, concurrent.futures as cf
from pathlib import Path
import requests
UFS = "AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split()
C = [
 "https://al.sp.gov.br/api/deputado", "https://al.sp.gov.br/api/propositura",
 "https://dadosabertos.almg.gov.br/ws/deputados/em_exercicio?formato=json",
 "https://dadosabertos.almg.gov.br/ws/proposicoes/pesquisa/direcionada?tp=100&formato=json&ano=2026",
 "https://dadosabertos.alepe.pe.gov.br/", "https://dadosabertos.alepe.pe.gov.br/api/parlamentares", "https://dadosabertos.alepe.pe.gov.br/parlamentares",
 "https://dadosabertos.alepe.pe.gov.br/api/v1/parlamentares", "https://dadosabertos.alepe.pe.gov.br/api/projetos",
 "https://dadosabertos.cl.df.gov.br/api/3/action/package_list", "https://dadosabertos.cl.df.gov.br/",
 "http://webservices.assembleia.pr.leg.br/api/public/parlamentar",
 "https://www.alesc.sc.gov.br/dados-abertos", "https://dadosabertos.alesc.sc.gov.br/",
 "https://www.al.rs.gov.br/dados-abertos", "https://ww4.al.rs.gov.br/dados-abertos",
 "https://www.alerj.rj.gov.br/DadosAbertos", "https://dadosabertos.alerj.rj.gov.br/",
 "https://www.al.ba.gov.br/dados-abertos", "https://www.al.ce.gov.br/index.php/dados-abertos", "https://www.al.es.gov.br/Dados-Abertos",
 "https://portal.al.go.leg.br/api/proposicoes", "https://transparencia.al.go.leg.br/",
]
for uf in UFS:
    u = uf.lower()
    C += [f"https://sapl.al.{u}.leg.br/api/parlamentares/parlamentar/?page_size=1", f"https://sapl.al.{u}.leg.br/api/materia/materialegislativa/?page_size=1",
          f"https://dadosabertos.al.{u}.leg.br/", f"https://www.al.{u}.leg.br/dados-abertos"]
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json, text/xml, */*"}
def t(u):
    try:
        r = requests.get(u, headers=H, timeout=20, allow_redirects=True)
        return {"u": u, "st": r.status_code, "ct": r.headers.get("content-type", ""), "n": len(r.content), "final": r.url, "ini": r.text[:400]}
    except Exception as e: return {"u": u, "erro": type(e).__name__ + ": " + str(e)[:120]}
with cf.ThreadPoolExecutor(16) as ex: R = list(ex.map(t, C))
out = Path(__file__).resolve().parents[1] / "site" / "data" / "_sonda_assembleias.json"
json.dump(R, open(out, "w"), ensure_ascii=False, indent=1)
for r in R: print(r.get("st", "ERR"), r["u"], r.get("ct", r.get("erro", ""))[:60], r.get("n", ""))
