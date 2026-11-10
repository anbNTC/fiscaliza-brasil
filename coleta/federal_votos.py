"""Coleta diária das votações nominais do Plenário da Câmara e do Senado (acrescenta as novas, não mexe nas antigas).
Câmara: arquivos anuais dos Dados Abertos (votacoes, votacoesProposicoes, votacoesObjetos, votacoesOrientacoes, votacoesVotos).
Senado: Dados Abertos, /dadosabertos/votacao?dataInicio=&dataFim= (votação com o voto de cada senador).
Atualiza: site/data/camara_votacoes.json, senado_votacoes.json, c/{UF}.json e s/{UF}.json (campo "v": um caractere por votação)
e br.json (deputados que passaram a votar, como suplentes que assumiram, e partido atual).
Depois desta etapa, tools/partidos.py recalcula o voto com ou contra o partido ("fp")."""
import csv, io, json, os, sys, time, datetime, re
from collections import defaultdict
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)", "accept": "application/json"}
S = requests.Session(); S.headers.update(H)
HOJE = datetime.date.today()
CV = {"sim": "S", "não": "N", "nao": "N", "abstenção": "A", "abstencao": "A", "obstrução": "O", "obstrucao": "O", "artigo 17": "P", "art. 17": "P"}
SV = {"sim": "S", "não": "N", "nao": "N", "abstenção": "A", "abstencao": "A", "votou": "V", "p-nrv": "P", "presidente (art. 51 risf)": "R", "presidente": "R", "obstrução": "O"}
rd = lambda p: json.load(open(D / p))
wr = lambda p, x: json.dump(x, open(D / p, "w"), ensure_ascii=False, separators=(",", ":"))

def get(u, js=True, tent=4):
    for k in range(tent):
        try:
            r = S.get(u, timeout=240)
            if r.status_code == 404: return None
            if r.ok: return r.json() if js else r.content
            print(u, r.status_code, flush=True)
        except Exception as e: print(u, repr(e)[:120], flush=True)
        time.sleep(6 * (k + 1))

def csv_ano(tipo, ano):
    b = get(f"https://dadosabertos.camara.leg.br/arquivos/{tipo}/csv/{tipo}-{ano}.csv", js=False)
    return list(csv.DictReader(io.StringIO(b.decode("utf-8-sig")), delimiter=";")) if b else []

def int0(x):
    try: return int(x)
    except Exception: return 0

def acrescenta(pasta, chaves_uf, novos_votos, n_antes, n_novos):
    """novos_votos: {id_parlamentar: {pos: código}}; estende "v" de todos (presentes no arquivo ou novos)."""
    mud = 0
    for uf, ids in chaves_uf.items():
        p = D / pasta / f"{uf}.json"
        try: X = json.load(open(p))
        except Exception: X = {}
        for k in ids:
            x = X.setdefault(k, {})
            v = (x.get("v") or "").ljust(n_antes, "-")[:n_antes]
            nv = novos_votos.get(k, {})
            add = "".join(nv.get(i, "-") for i in range(n_novos))
            x["v"] = v + add
            if "pres" in x and isinstance(x["pres"], list) and len(x["pres"]) == 2:
                x["pres"] = [x["pres"][0] + sum(1 for c in add if c not in "-?"), x["pres"][1] + (n_novos if nv else 0)]
            mud += 1
        # quem não está mais em exercício: completa com "-" para manter o tamanho
        for k, x in X.items():
            if k not in ids and isinstance(x, dict) and "v" in x: x["v"] = (x["v"] or "").ljust(n_antes + n_novos, "-")[: n_antes + n_novos]
        json.dump(X, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    return mud

def camara(BR):
    VC = rd("camara_votacoes.json"); ids = {x[0] for x in VC}; ult = max(x[1] for x in VC)
    anos = sorted({int(ult[:4]), HOJE.year})
    V = []; P = {}; O = {}; G = {}; VT = defaultdict(dict); dep_info = {}
    for ano in anos:
        for r in csv_ano("votacoes", ano):
            if r["siglaOrgao"] == "PLEN" and r["data"] >= ult and r["id"] not in ids: V.append(r)  # nominal = tem voto registrado (filtrado abaixo)
        # checagem: o critério reproduz o que já existe?
        if ano == int(ult[:4]):
            ja = sum(1 for x in VC if x[1][:4] == str(ano))
            print("Câmara: votações nominais já gravadas em", ano, ja, flush=True)
    if not V: print("Câmara: nenhuma votação nova desde", ult); return 0
    alvo = {r["id"] for r in V}; print("Câmara: votações do Plenário depois de", ult, "a conferir:", len(alvo), flush=True)
    for ano in anos:
        for r in csv_ano("votacoesProposicoes", ano):
            if r["idVotacao"] in alvo and r["idVotacao"] not in P: P[r["idVotacao"]] = r
        for r in csv_ano("votacoesObjetos", ano):
            if r["idVotacao"] in alvo and r["idVotacao"] not in O: O[r["idVotacao"]] = r
        for r in csv_ano("votacoesOrientacoes", ano):
            if r["idVotacao"] in alvo and (r["siglaBancada"] or "").strip().lower() == "governo": G[r["idVotacao"]] = r["orientacao"]
        for r in csv_ano("votacoesVotos", ano):
            if r["idVotacao"] in alvo:
                VT[r["idVotacao"]][r["deputado_id"]] = CV.get((r["voto"] or "").strip().lower(), "?")
                dep_info[r["deputado_id"]] = (r["deputado_nome"], r["deputado_siglaPartido"], r["deputado_siglaUf"], r["deputado_urlFoto"], r["dataHoraVoto"])
    V = [r for r in V if VT.get(r["id"])]  # só as que têm voto registrado
    V.sort(key=lambda r: (r["data"], r["dataHoraRegistro"]))
    novos = []; temas = {}
    for r in V:
        pr = P.get(r["id"]) or O.get(r["id"]) or {}
        tit = pr.get("proposicao_titulo") or (f'{pr.get("proposicao_siglaTipo", "")} {pr.get("proposicao_numero", "")}/{pr.get("proposicao_ano", "")}' if pr else "")
        pid = pr.get("proposicao_id")
        if pid and pid not in temas:
            j = get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes/{pid}/temas", tent=2) or {}
            temas[pid] = [t.get("tema") for t in j.get("dados", []) if t.get("tema")][:4]; time.sleep(0.3)
        vs = VT[r["id"]]; sim = sum(1 for c in vs.values() if c == "S"); nao = sum(1 for c in vs.values() if c == "N")
        novos.append([r["id"], r["data"], "1" if r["aprovacao"] == "1" else "0", sim, nao, tit.strip(), (pr.get("proposicao_ementa") or "").strip()[:180], (r["descricao"] or "").strip(), G.get(r["id"], ""), temas.get(pid, [])])
    n0 = len(VC); VC += novos
    # deputados em exercício: os de br.json mais quem votou agora (suplente que assumiu)
    dep = {str(d[0]): d for d in BR["dep"]}
    for k, (nome, part, uf, foto, _) in dep_info.items():
        if k in dep: dep[k][2] = part or dep[k][2]
        else: BR["dep"].append([int(k), nome, part, uf, (foto or "").replace("http://", "https://"), "", None, 0, 0, None, ""]); dep[k] = BR["dep"][-1]; print("Câmara: novo deputado em exercício", nome, part, uf)
    por_uf = defaultdict(list)
    for k, d in dep.items(): por_uf[d[3]].append(k)
    nv = defaultdict(dict)
    for i, r in enumerate(V):
        for k, c in VT[r["id"]].items(): nv[k][i] = c
    acrescenta("c", por_uf, nv, n0, len(novos))
    wr("camara_votacoes.json", VC)
    print("Câmara:", len(novos), "votações novas, de", novos[0][1], "a", novos[-1][1]); return len(novos)

def senado(BR):
    VS = rd("senado_votacoes.json"); ids = {str(x[0]) for x in VS}; ult = max(x[1] for x in VS)
    ini = datetime.date.fromisoformat(ult); novos = []; votos = []
    d = ini
    while d <= HOJE:
        f = min(d + datetime.timedelta(days=30), HOJE)
        L = get(f"https://legis.senado.leg.br/dadosabertos/votacao?dataInicio={d}&dataFim={f}") or []
        for x in L:
            if str(x.get("codigoSessaoVotacao")) in ids or (x.get("casaSessao") or "SF") != "SF": continue
            vt = x.get("votos") or []
            if not vt: continue
            ids.add(str(x.get("codigoSessaoVotacao"))); votos.append((x, vt))
        d = f + datetime.timedelta(days=1)
    if votos and "_mostrou" not in os.environ:
        x0, v0 = votos[0]; print("Senado: campos", sorted(k for k in x0 if k not in ("votos", "informeLegislativo")), "| voto:", json.dumps(v0[0], ensure_ascii=False)[:300])
    votos.sort(key=lambda t: (t[0].get("dataSessao") or "", t[0].get("codigoSessaoVotacao") or 0))
    nv = defaultdict(dict); quem = {}
    for i, (x, vt) in enumerate(votos):
        sec = "S" if str(x.get("votacaoSecreta") or x.get("indicadorVotacaoSecreta") or "N")[:1].upper() == "S" else "N"
        res = str(x.get("resultadoVotacao") or x.get("resultado") or "")
        res = "A" if res[:1].upper() == "A" else "R" if res[:1].upper() == "R" else ("A" if int0(x.get("totalVotosSim")) > int0(x.get("totalVotosNao")) else "R")
        for v in vt:
            k = str(v.get("codigoParlamentar") or v.get("CodigoParlamentar") or "")
            sg = (v.get("siglaVotoParlamentar") or v.get("descricaoVotoParlamentar") or v.get("voto") or "").strip().lower()
            if k: nv[k][i] = SV.get(sg, "-" if sg else "-"); quem[k] = v
        novos.append([x.get("codigoSessaoVotacao"), x.get("dataSessao"), x.get("identificacao") or "", (x.get("ementa") or "").strip()[:180], (x.get("descricaoVotacao") or "").strip(), res, sec, int0(x.get("totalVotosSim")), int0(x.get("totalVotosNao"))])
    if not novos: print("Senado: nenhuma votação nova desde", ult); return 0
    n0 = len(VS); VS += novos
    por_uf = defaultdict(list)
    for s in BR["sen"]: por_uf[s[4]].append(str(s[0]))
    acrescenta("s", por_uf, nv, n0, len(novos))
    wr("senado_votacoes.json", VS)
    print("Senado:", len(novos), "votações novas, de", novos[0][1], "a", novos[-1][1]); return len(novos)

def main():
    BR = rd("br.json"); r = {}
    try: r["camara"] = camara(BR)
    except Exception as e: print("Câmara falhou:", repr(e)); r["camara"] = "erro"
    try: r["senado"] = senado(BR)
    except Exception as e: print("Senado falhou:", repr(e)); r["senado"] = "erro"
    BR["gerado"] = HOJE.isoformat(); wr("br.json", BR)
    print(json.dumps(r))
    if "erro" in r.values(): sys.exit(1)

if __name__ == "__main__":
    main()
