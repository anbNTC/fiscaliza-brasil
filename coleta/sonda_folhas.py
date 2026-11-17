"""Sonda temporária: portais (CKAN) de estados e capitais com folha de pagamento com nome e lotação."""
import sys, json, requests, concurrent.futures as cf
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
P = ["dados.sc.gov.br", "dados.rs.gov.br", "dados.es.gov.br", "dados.pr.gov.br", "dadosabertos.pr.gov.br", "dados.sp.gov.br", "dados.ba.gov.br", "dados.ce.gov.br",
     "dados.al.gov.br", "dados.rj.gov.br", "dados.df.gov.br", "dados.ms.gov.br", "dados.to.gov.br", "dados.pa.gov.br", "dados.mt.gov.br", "dados.am.gov.br",
     "dados.rn.gov.br", "dados.pb.gov.br", "dados.pi.gov.br", "dados.ma.gov.br", "dados.se.gov.br", "dados.ro.gov.br", "dados.ap.gov.br", "dados.ac.gov.br",
     "dados.rr.gov.br", "dadosabertos.go.gov.br",
     "dadosabertos.curitiba.pr.gov.br", "dados.curitiba.pr.gov.br", "dados.fortaleza.ce.gov.br", "dados.rio", "dadosabertos.rio.rj.gov.br", "dados.salvador.ba.gov.br",
     "dados.natal.rn.gov.br", "dados.joaopessoa.pb.gov.br", "dadosabertos.goiania.go.gov.br", "dados.manaus.am.gov.br", "dados.florianopolis.sc.gov.br",
     "dados.campogrande.ms.gov.br", "dados.teresina.pi.gov.br", "dados.aracaju.se.gov.br", "dados.vitoria.es.gov.br", "dados.cuiaba.mt.gov.br", "dados.belem.pa.gov.br",
     "dados.saoluis.ma.gov.br", "dados.maceio.al.gov.br", "dados.palmas.to.gov.br", "dados.portovelho.ro.gov.br", "dados.boavista.rr.gov.br", "dados.macapa.ap.gov.br",
     "dados.riobranco.ac.gov.br"]
def um(p):
    out = []
    for q in ("remuneracao servidores", "folha de pagamento", "servidores ativos"):
        u = f"https://{p}/api/3/action/package_search?q={q.replace(' ', '%20')}&rows=6"
        try:
            r = requests.get(u, headers=H, timeout=20)
            if not r.ok: r = gbr(u, headers=H, timeout=40) or r
            j = r.json()["result"]
            for x in j["results"]:
                out.append((x["name"], (x.get("title") or "")[:70], "/".join(sorted({(y.get("format") or "?").upper() for y in x.get("resources", [])})[:4]), (x.get("metadata_modified") or "")[:10]))
        except BaseException as e:
            return p, "falhou " + repr(e)[:60]
    return p, list(dict.fromkeys(out))[:8]
with cf.ThreadPoolExecutor(16) as ex:
    for p, r in ex.map(um, P):
        if isinstance(r, str): print("PORTAL", p, r, flush=True); continue
        print("PORTAL", p, len(r), flush=True)
        for x in r: print("  PKG", p, " | ".join(map(str, x)), flush=True)
