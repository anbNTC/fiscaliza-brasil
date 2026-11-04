"""Coleta, na API de Dados Abertos da Câmara, para cada votação de site/data/camara_votacoes.json:
  - a orientação oficial de cada partido, federação ou bloco (Sim, Não, Liberado, Obstrução)
  - o partido de cada deputado NO DIA da votação (resolve quem trocou de partido)
Saída: site/data/camara_orient.json  {"v": {id_votacao: {"o": {rotulo: "S"|"N"|"L"|"O"}, "p": {id_dep: "SIGLA"}}}}
É incremental: só busca votações que ainda não estão no arquivo."""
import json, sys, time
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"
API = "https://dadosabertos.camara.leg.br/api/v2"
OUT = D / "camara_orient.json"
S = requests.Session(); S.headers.update({"accept": "application/json", "user-agent": "FiscalizaBrasil/1.0 (+https://fiscalizaja.com.br)"})
COD = {"Sim": "S", "Não": "N", "Nao": "N", "Liberado": "L", "Obstrução": "O", "Obstrucao": "O", "Abstenção": "A"}

def get(url, tent=4):
    for k in range(tent):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 200: return r.json().get("dados", [])
            if r.status_code in (404, 400): return []
        except Exception as e:
            pass
        time.sleep(2 * (k + 1))
    raise RuntimeError("falhou: " + url)

def main(limite=None):
    VC = json.load(open(D / "camara_votacoes.json"))
    atual = json.load(open(OUT)) if OUT.exists() else {"v": {}}
    falta = [v[0] for v in VC if v[0] not in atual["v"]]
    if limite: falta = falta[:limite]
    print(f"{len(VC)} votações, {len(falta)} para buscar", flush=True)
    erros = 0
    for n, vid in enumerate(falta, 1):
        try:
            o = {x.get("siglaPartidoBloco"): COD.get(x.get("orientacaoVoto"), "?") for x in get(f"{API}/votacoes/{vid}/orientacoes") if x.get("siglaPartidoBloco")}
            p = {}
            for x in get(f"{API}/votacoes/{vid}/votos"):
                d = x.get("deputado_") or {}
                if d.get("id"): p[str(d["id"])] = d.get("siglaPartido") or ""
            atual["v"][vid] = {"o": o, "p": p}
        except Exception as e:
            erros += 1; print("erro", vid, e, flush=True)
            if erros > 40: break
        if n % 50 == 0:
            print(n, "ok", flush=True); json.dump(atual, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
        time.sleep(0.15)
    json.dump(atual, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"pronto: {len(atual['v'])} votações no arquivo, {erros} erros")
    return {"votacoes": len(atual["v"]), "novas": len(falta), "erros": erros}

if __name__ == "__main__":
    print(json.dumps(main(int(sys.argv[1]) if len(sys.argv) > 1 else None)))
