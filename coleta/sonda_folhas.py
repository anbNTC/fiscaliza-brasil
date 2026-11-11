"""Sonda temporária: portais de folha de estados e capitais pela saída do Brasil."""
import re, sys
sys.path.insert(0, "coleta")
from saida_br import get
A = ["https://cearatransparente.ce.gov.br/files/downloads/integration/servers/server_salaries/",
     "https://cearatransparente.ce.gov.br/portal-da-transparencia/servidores/remuneracao",
     "https://dados.prefeitura.sp.gov.br/api/3/action/package_search?q=remuneracao&rows=8",
     "https://dados.prefeitura.sp.gov.br/api/3/action/package_search?q=servidores&rows=8",
     "https://dados.df.gov.br/api/3/action/package_search?q=remuneracao&rows=8",
     "https://dados.rs.gov.br/api/3/action/package_search?q=remuneracao&rows=8",
     "https://dados.ce.gov.br/api/3/action/package_search?q=remuneracao&rows=8",
     "https://dados.pe.gov.br/api/3/action/package_search?q=remuneracao&rows=8",
     "https://dados.go.gov.br/api/3/action/package_search?q=remuneracao&rows=8",
     "https://dados.sp.gov.br/api/3/action/package_search?q=remuneracao&rows=8",
     "https://transparencia.vitoria.es.gov.br/", "https://transparencia.vitoria.es.gov.br/Pessoal.aspx"]
for u in A:
    try:
        r = get(u, headers={"accept": "*/*"}, timeout=90, tentativas=1)
        if r is None: print("==", u, "sem resposta"); continue
        t = r.text; print("==", u, r.status_code, r.headers.get("content-type"), len(t))
        if "package_search" in u:
            for m in re.finditer(r'"name": ?"([^"]+)", ?"notes"|"title": ?"([^"]{5,120})"', t): print("   ", m.group(1) or m.group(2))
        else:
            for m in list(re.finditer(r'href="([^"]*(?:csv|zip|xlsx|download|Pessoal|servidor|remunera)[^"]*)"', t, re.I))[:25]: print("   ", m.group(1)[:200])
    except Exception as e: print("==", u, "ERRO", repr(e)[:120])
    sys.stdout.flush()
