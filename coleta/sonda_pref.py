"""Sonda temporária: portais de dados abertos (CKAN) de cidades grandes com folha de servidores."""
import sys, requests, concurrent.futures as cf
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
P = ["dados.campinas.sp.gov.br", "dadosabertos.campinas.sp.gov.br", "dados.guarulhos.sp.gov.br", "dadosabertos.sjc.sp.gov.br", "dados.sjc.sp.gov.br",
     "dados.ribeiraopreto.sp.gov.br", "dados.santoandre.sp.gov.br", "dados.osasco.sp.gov.br", "dados.sorocaba.sp.gov.br", "dados.santos.sp.gov.br",
     "dados.londrina.pr.gov.br", "dadosabertos.londrina.pr.gov.br", "dados.maringa.pr.gov.br", "dadosabertos.maringa.pr.gov.br", "dados.joinville.sc.gov.br",
     "dadosabertos.joinville.sc.gov.br", "dados.blumenau.sc.gov.br", "dados.uberlandia.mg.gov.br", "dados.contagem.mg.gov.br", "dados.juizdefora.mg.gov.br",
     "dados.niteroi.rj.gov.br", "dadosabertos.niteroi.rj.gov.br", "dados.caxiasdosul.rs.gov.br", "dados.feiradesantana.ba.gov.br", "dados.jaboatao.pe.gov.br",
     "dados.saobernardo.sp.gov.br", "dados.cascavel.pr.gov.br", "dados.pontagrossa.pr.gov.br", "dados.fozdoiguacu.pr.gov.br", "dados.saojosedospinhais.pr.gov.br",
     "dados.serra.es.gov.br", "dados.vilavelha.es.gov.br", "dados.anapolis.go.gov.br", "dados.aparecida.go.gov.br", "dados.betim.mg.gov.br", "dados.montesclaros.mg.gov.br",
     "dados.piracicaba.sp.gov.br", "dados.jundiai.sp.gov.br", "dados.bauru.sp.gov.br", "dados.mogidascruzes.sp.gov.br", "dados.pelotas.rs.gov.br", "dados.canoas.rs.gov.br"]
def um(p):
    out = []
    for q in ("remuneracao", "servidores", "folha"):
        u = f"https://{p}/api/3/action/package_search?q={q}&rows=5"
        try:
            r = requests.get(u, headers=H, timeout=15)
            if not r.ok: r = gbr(u, headers=H, timeout=30) or r
            for x in r.json()["result"]["results"]: out.append((x["name"], (x.get("title") or "")[:60], (x.get("metadata_modified") or "")[:10]))
        except BaseException: return p, None
    return p, list(dict.fromkeys(out))[:6]
with cf.ThreadPoolExecutor(16) as ex:
    for p, r in ex.map(um, P):
        if r is None: continue
        print("PORTAL", p, len(r), flush=True)
        for x in r: print("  PKG", p, " | ".join(x), flush=True)
