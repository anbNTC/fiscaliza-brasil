"""Coleta diária do que cada deputado federal e senador apresentou e gastou, refeita do zero a cada dia (desde 2023).
Câmara · projetos: arquivos anuais proposicoes, proposicoesAutores e proposicoesTemas (Dados Abertos).
Câmara · cota parlamentar (CEAP): www.camara.leg.br/cotas/Ano-AAAA.csv.zip.
Senado · cota (CEAPS): www.senado.gov.br/transparencia/LAI/verba/despesa_ceaps_AAAA.csv.
Grava em c/{UF}.json e s/{UF}.json os campos "au" (projetos) e "cota" ({"a": ano -> tipo -> R$, "m": mês -> R$, "f": maiores fornecedores})
sem mexer nos outros campos. Se uma fonte falhar, o campo antigo fica como estava."""
import csv, io, json, re, sys, time, datetime, zipfile, unicodedata
from collections import defaultdict, Counter
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"
H = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
S = requests.Session(); S.headers.update(H)
HOJE = datetime.date.today(); ANOS = range(2023, HOJE.year + 1)
LISTA = {"PL", "PLP", "PEC", "PDL"}
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^A-Z ]", " ", unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper())).strip()
num = lambda s: float(str(s or "0").replace(".", "").replace(",", ".")) if "," in str(s or "") else float(s or 0)

def baixa(u, tent=4):
    for k in range(tent):
        try:
            r = S.get(u, timeout=300)
            if r.status_code == 404: return None
            if r.ok: return r.content
            print(u, r.status_code, flush=True)
        except Exception as e: print(u, repr(e)[:120], flush=True)
        time.sleep(8 * (k + 1))

def csv_camara(tipo, ano):
    b = baixa(f"https://dadosabertos.camara.leg.br/arquivos/{tipo}/csv/{tipo}-{ano}.csv")
    return csv.DictReader(io.StringIO(b.decode("utf-8-sig")), delimiter=";") if b else None

def projetos_camara(ids):
    prop = {}; aut = defaultdict(list); temas = defaultdict(list)
    for ano in ANOS:
        rd = csv_camara("proposicoes", ano)
        if rd is None: raise RuntimeError(f"proposicoes-{ano} indisponível")
        for r in rd: prop[r["id"]] = r
        rd = csv_camara("proposicoesAutores", ano)
        if rd is None: raise RuntimeError(f"proposicoesAutores-{ano} indisponível")
        for r in rd:
            if r.get("idDeputadoAutor") in ids: aut[r["idDeputadoAutor"]].append((r["idProposicao"], r.get("ordemAssinatura") or "", r.get("proponente") or ""))
        rd = csv_camara("proposicoesTemas", ano)
        for r in rd or []: temas[r.get("uriProposicao", "").rsplit("/", 1)[-1] or r.get("idProposicao", "")].append(r.get("tema"))
    out = {}
    for k, L in aut.items():
        c = Counter(); l = []; vis = set()
        for pid, ordem, prop1 in L:
            p = prop.get(pid)
            if not p or pid in vis: continue
            vis.add(pid); sg = p.get("siglaTipo") or ""; c[sg] += 1
            if sg in LISTA:
                l.append([pid, sg, p.get("numero"), int(p.get("ano") or 0), (p.get("dataApresentacao") or "")[:10], (p.get("ementa") or "").strip()[:200],
                          p.get("ultimoStatus_descricaoSituacao") or "", 1 if str(ordem).strip() == "1" else 0, [t for t in temas.get(pid, []) if t][:3]])
        l.sort(key=lambda x: x[4], reverse=True)
        out[k] = {"c": dict(c), "l": l}
    return out

def cota_camara(ids):
    A = defaultdict(lambda: defaultdict(lambda: defaultdict(float))); M = defaultdict(lambda: defaultdict(float)); F = defaultdict(lambda: defaultdict(float))
    for ano in ANOS:
        b = baixa(f"https://www.camara.leg.br/cotas/Ano-{ano}.csv.zip")
        if not b: raise RuntimeError(f"cota {ano} indisponível")
        z = zipfile.ZipFile(io.BytesIO(b)); nm = z.namelist()[0]
        for r in csv.DictReader(io.TextIOWrapper(z.open(nm), encoding="utf-8-sig"), delimiter=";"):
            k = (r.get("ideCadastro") or "").strip()
            if k not in ids: continue
            v = num(r.get("vlrLiquido")); cat = (r.get("txtDescricao") or "Outros").strip().title()
            A[k][str(ano)][cat] += v; M[k][f'{ano}-{int(r.get("numMes") or 0):02d}'] += v
            F[k][(r.get("txtFornecedor") or "Não informado").strip()] += v
    return {k: {"a": {a: {c: round(v) for c, v in t.items()} for a, t in A[k].items()}, "m": {m: round(v) for m, v in sorted(M[k].items())},
                "f": [[n, round(v)] for n, v in sorted(F[k].items(), key=lambda x: -x[1])[:8]]} for k in A}

def cota_senado(sen):
    nome = {norm(s[1]): str(s[0]) for s in sen}
    A = defaultdict(lambda: defaultdict(lambda: defaultdict(float))); M = defaultdict(lambda: defaultdict(float)); F = defaultdict(lambda: defaultdict(float)); sem = Counter()
    for ano in ANOS:
        b = baixa(f"https://www.senado.gov.br/transparencia/LAI/verba/despesa_ceaps_{ano}.csv")
        if not b: raise RuntimeError(f"CEAPS {ano} indisponível")
        t = b.decode("latin-1"); linhas = t.splitlines()
        i0 = next(i for i, l in enumerate(linhas) if l.upper().startswith('"ANO"') or l.upper().startswith("ANO;"))
        for r in csv.DictReader(io.StringIO("\n".join(linhas[i0:])), delimiter=";"):
            k = nome.get(norm(r.get("SENADOR")))
            if not k: sem[r.get("SENADOR")] += 1; continue
            v = num(r.get("VALOR_REEMBOLSADO")); cat = (r.get("TIPO_DESPESA") or "Outros").split(",")[0].strip()
            A[k][str(ano)][cat] += v; M[k][f'{ano}-{int(r.get("MES") or 0):02d}'] += v; F[k][(r.get("FORNECEDOR") or "Não informado").strip()] += v
    if sem: print("Senado: nomes da CEAPS sem senador em exercício (ex-senadores ou grafia diferente):", sem.most_common(6), flush=True)
    return {k: {"a": {a: {c: round(v) for c, v in t.items()} for a, t in A[k].items()}, "m": {m: round(v) for m, v in sorted(M[k].items())},
                "f": [[n, round(v)] for n, v in sorted(F[k].items(), key=lambda x: -x[1])[:8]]} for k in A}

def grava(pasta, por_uf, campo, dados):
    n = 0
    for uf, ids in por_uf.items():
        p = D / pasta / f"{uf}.json"
        try: X = json.load(open(p))
        except Exception: X = {}
        for k in ids:
            if k in dados: X.setdefault(k, {})[campo] = dados[k]; n += 1
        json.dump(X, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    return n

def main():
    BR = json.load(open(D / "br.json")); r = {}; erro = False
    dep = defaultdict(list)
    for d in BR["dep"]: dep[d[3]].append(str(d[0]))
    ids = {k for L in dep.values() for k in L}
    sen = defaultdict(list)
    for s in BR["sen"]: sen[s[4]].append(str(s[0]))
    for nome, f, pasta, por, campo in (("camara_projetos", lambda: projetos_camara(ids), "c", dep, "au"), ("camara_cota", lambda: cota_camara(ids), "c", dep, "cota"),
                                       ("senado_cota", lambda: cota_senado(BR["sen"]), "s", sen, "cota")):
        try:
            x = f(); r[nome] = grava(pasta, por, campo, x); print(nome, r[nome], flush=True)
        except Exception as e: print(nome, "falhou:", repr(e)[:200], flush=True); r[nome] = "erro"; erro = True
    print(json.dumps(r))
    if erro: sys.exit(1)

if __name__ == "__main__":
    main()
