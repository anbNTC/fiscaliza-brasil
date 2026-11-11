"""Sonda temporária: procura, nos portais CKAN de prefeituras e governos estaduais, conjuntos com a folha dos servidores."""
import json, sys, requests
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
HOSTS = ["https://dados.recife.pe.gov.br", "http://dados.prefeitura.sp.gov.br", "https://dadosabertos.poa.br", "https://dados.fortaleza.ce.gov.br",
         "https://dados.campinas.sp.gov.br", "https://dados.natal.br", "https://dados.niteroi.rj.gov.br", "https://dados.joaopessoa.pb.gov.br",
         "https://dados.ce.gov.br", "https://dados.rs.gov.br", "https://dados.mg.gov.br", "https://dados.sp.gov.br", "https://dados.es.gov.br",
         "https://dados.pr.gov.br", "https://dados.al.gov.br", "https://dados.df.gov.br", "https://dados.ba.gov.br", "https://dados.pe.gov.br",
         "https://dados.go.gov.br", "https://dados.sc.gov.br", "https://dados.rn.gov.br", "https://dados.pa.gov.br", "https://dados.ms.gov.br",
         "https://dados.mt.gov.br", "https://dados.to.gov.br", "https://dados.am.gov.br", "https://dados.ro.gov.br", "https://dados.ap.gov.br",
         "https://dados.ac.gov.br", "https://dados.rr.gov.br", "https://dados.ma.gov.br", "https://dados.pi.gov.br", "https://dados.se.gov.br",
         "https://dados.pb.gov.br", "https://dados.rj.gov.br", "https://dadosabertos.go.gov.br", "https://dadosabertos.ba.gov.br", "https://dadosabertos.es.gov.br",
         "https://dados.vitoria.es.gov.br", "https://dados.florianopolis.sc.gov.br", "https://dados.manaus.am.gov.br", "https://dados.salvador.ba.gov.br",
         "https://dados.goiania.go.gov.br", "https://dados.jaboatao.pe.gov.br", "https://dados.santos.sp.gov.br", "https://dados.saojosedoscampos.sp.gov.br"]
for h in HOSTS:
    for q in ["servidores remuneracao", "folha pagamento", "remuneracao"]:
        try:
            r = requests.get(f"{h}/api/3/action/package_search", params={"q": q, "rows": 6}, headers=H, timeout=40)
            j = r.json()
        except Exception as e:
            print(h, "ERRO", repr(e)[:80]); break
        res = j.get("result", {}).get("results", [])
        if not res: continue
        print("##", h, "q=", q, "total", j["result"].get("count"))
        for p in res:
            rs = p.get("resources") or []
            print("  ", p["name"], "|", (p.get("title") or "")[:70], "| recursos", len(rs), "|", "; ".join(((x.get("name") or "")[:40] + " [" + (x.get("format") or "") + "]") for x in rs[-3:]))
        break
    sys.stdout.flush()
