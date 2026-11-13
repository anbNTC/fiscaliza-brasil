"""Sonda temporária: portais estaduais de dados abertos (CKAN) com emendas parlamentares estaduais."""
import sys, json, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
P = ["dados.sc.gov.br", "dados.rs.gov.br", "dados.es.gov.br", "dados.pr.gov.br", "dadosabertos.pr.gov.br", "dados.sp.gov.br", "dados.ba.gov.br", "dados.ce.gov.br",
     "dados.al.gov.br", "dados.rj.gov.br", "dados.df.gov.br", "dados.ms.gov.br", "dados.to.gov.br", "dados.pa.gov.br", "dados.mt.gov.br", "dados.am.gov.br",
     "dados.rn.gov.br", "dados.pb.gov.br", "dados.pi.gov.br", "dados.ma.gov.br", "dados.se.gov.br", "dados.ro.gov.br", "dados.ap.gov.br", "dados.ac.gov.br", "dados.rr.gov.br"]
for p in P:
    u = f"https://{p}/api/3/action/package_search?q=emenda%20parlamentar&rows=8"
    try:
        r = requests.get(u, headers=H, timeout=25)
        if not r.ok: r = gbr(u, headers=H, timeout=40)
        j = r.json()["result"]
        print("CKAN", p, j["count"], flush=True)
        for x in j["results"]:
            print("  PKG", p, x["name"], "|", x.get("title"), "|", sorted({(y.get("format") or "?") for y in x.get("resources", [])}), "|", (x.get("metadata_modified") or "")[:10], flush=True)
    except Exception as e: print("CKAN", p, "falhou", repr(e)[:120], flush=True)
