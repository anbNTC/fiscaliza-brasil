"""Sonda (temporária): estrutura das fontes federais para a coleta diária."""
import requests, json, io, csv
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0", "accept": "application/json"}
def g(u, **k): return requests.get(u, headers=H, timeout=180, **k)
for t in ("votacoes", "votacoesObjetos", "votacoesOrientacoes", "votacoesVotos", "votacoesProposicoes"):
    u = f"https://dadosabertos.camara.leg.br/arquivos/{t}/csv/{t}-2026.csv"
    r = g(u); print("==", t, r.status_code, len(r.content))
    if r.ok:
        rows = list(csv.DictReader(io.StringIO(r.content.decode("utf-8-sig")), delimiter=";"))
        print(list(rows[0].keys()))
        if t == "votacoes":
            pl = [x for x in rows if x.get("siglaOrgao") == "PLEN" and x["data"] >= "2026-10-14"]
            print(len(rows), "PLEN desde 14/10:", len(pl)); [print({k: x[k] for k in list(x)[:14]}) for x in pl[-4:]]
        else:
            print(json.dumps(rows[-1], ensure_ascii=False)[:700])
for u in ("https://legis.senado.leg.br/dadosabertos/votacao?dataInicio=2026-11-03&dataFim=2026-11-10",
          "https://legis.senado.leg.br/dadosabertos/senador/lista/atual.json"):
    r = g(u); print("==", u, r.status_code, len(r.content))
    try: print(json.dumps(r.json(), ensure_ascii=False)[:2500])
    except Exception: print(r.text[:800])
r = g("https://dadosabertos.camara.leg.br/api/v2/deputados?itens=3&ordem=ASC&ordenarPor=nome"); print("== deps", r.status_code, json.dumps(r.json(), ensure_ascii=False)[:800])
