"""Câmara dos Deputados: orientação oficial de cada partido/federação/bloco e partido de cada deputado NO DIA de cada votação.
Usa os arquivos anuais prontos da Câmara (rápido): votacoesOrientacoes-ANO.csv e votacoesVotos-ANO.csv.
Para votações que faltarem nos arquivos, consulta a API, com limite de tempo.
Saída: site/data/camara_orient.json  {"v": {id_votacao: {"o": {rotulo: "S"|"N"|"L"|"O"}, "p": {id_dep: "SIGLA"}}}}"""
import csv, io, json, os, sys, time
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"
OUT = D / "camara_orient.json"
ARQ = "https://dadosabertos.camara.leg.br/arquivos/{tipo}/csv/{tipo}-{ano}.csv"
API = "https://dadosabertos.camara.leg.br/api/v2"
LIMITE = time.time() + 60 * float(os.environ.get("MAX_MIN", "30"))
S = requests.Session(); S.headers.update({"user-agent": "FiscalizaBrasil/1.0 (+https://fiscalizaja.com.br)"})
COD = {"sim": "S", "não": "N", "nao": "N", "liberado": "L", "obstrução": "O", "obstrucao": "O", "abstenção": "A", "abstencao": "A"}
cod = lambda x: COD.get((x or "").strip().lower(), "?")

def csv_ano(tipo, ano):
    u = ARQ.format(tipo=tipo, ano=ano)
    for k in range(3):
        try:
            r = S.get(u, timeout=180)
            if r.ok:
                txt = r.content.decode("utf-8-sig", errors="replace")
                rd = csv.DictReader(io.StringIO(txt), delimiter=";")
                linhas = list(rd); print(f"{tipo}-{ano}: {len(linhas)} linhas", flush=True); return linhas
            print(f"{tipo}-{ano}: HTTP {r.status_code}", flush=True)
            if r.status_code == 404: return []
        except Exception as e: print(f"{tipo}-{ano}: {e}", flush=True)
        time.sleep(5 * (k + 1))
    return []

def api(url):
    for k in range(4):
        if time.time() > LIMITE: return None
        try:
            r = S.get(url, timeout=30, headers={"accept": "application/json"})
            if r.status_code == 200: return r.json().get("dados", [])
            if r.status_code == 429: time.sleep(float(r.headers.get("retry-after", 10))); continue
            if r.status_code in (400, 404): return []
        except Exception: pass
        time.sleep(3 * (k + 1))
    return None

def main():
    VC = json.load(open(D / "camara_votacoes.json")); ids = {v[0] for v in VC}
    anos = sorted({v[1][:4] for v in VC})
    atual = json.load(open(OUT)) if OUT.exists() else {"v": {}}
    V = atual["v"]
    for ano in anos:
        for l in csv_ano("votacoesOrientacoes", ano):
            i = l.get("idVotacao")
            if i in ids:
                rot = l.get("siglaBancada") or l.get("siglaPartidoBloco") or ""
                if rot: V.setdefault(i, {"o": {}, "p": {}})["o"][rot] = cod(l.get("orientacao") or l.get("orientacaoVoto"))
        for l in csv_ano("votacoesVotos", ano):
            i = l.get("idVotacao")
            if i in ids:
                dep = l.get("deputado_id") or ""
                if dep: V.setdefault(i, {"o": {}, "p": {}})["p"][dep] = l.get("deputado_siglaPartido") or ""
        json.dump(atual, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
    falta = [v[0] for v in VC if v[0] not in V or not V[v[0]]["p"]]
    print(f"depois dos arquivos: {len(ids) - len(falta)} de {len(ids)} votações com dados; {len(falta)} pela API", flush=True)
    feitas = 0
    for vid in falta:
        o = api(f"{API}/votacoes/{vid}/orientacoes"); p = api(f"{API}/votacoes/{vid}/votos")
        if o is None or p is None: print("tempo esgotado ou API indisponível; continua na próxima rodada", flush=True); break
        V[vid] = {"o": {x["siglaPartidoBloco"]: cod(x.get("orientacaoVoto")) for x in o if x.get("siglaPartidoBloco")},
                  "p": {str(x["deputado_"]["id"]): x["deputado_"].get("siglaPartido") or "" for x in p if x.get("deputado_")}}
        feitas += 1; time.sleep(0.8)
        if feitas % 25 == 0: json.dump(atual, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(atual, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
    com_o = sum(1 for v in V.values() if v["o"])
    r = {"votacoes": len(ids), "com_partido_no_dia": sum(1 for i in ids if i in V and V[i]["p"]), "com_orientacao": com_o, "pela_api": feitas}
    print(json.dumps(r)); return r

if __name__ == "__main__":
    main()
