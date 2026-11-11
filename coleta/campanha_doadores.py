"""Quem financiou e quem recebeu da campanha de cada eleito (TSE, prestação de contas de candidatos).
Fonte: TSE · Dados Abertos, "prestacao_de_contas_eleitorais_candidatos_{ano}.zip" (receitas e despesas contratadas).
Só os candidatos que aparecem no site (eleitos de 2022, 2024 e 2026), pelo número sequencial do TSE (SQ_CANDIDATO).
Saída: site/data/camp/{UF}.json (2022 e 2026) e site/data/camp/m{UF}.json (prefeitos e vereadores de 2024)
  {sq: {"c": [receita total, [[origem, valor]...], despesa total, [[tipo de gasto, valor]...]],
        "d": [[doador, valor] x10], "nd": nº de doadores, "f": [[fornecedor, valor] x10], "nf": nº de fornecedores}}
Nomes de doadores e fornecedores são publicados pelo TSE; CPF e CNPJ não entram no site.
Um ano já gravado não é baixado de novo, salvo com REFAZ=1 (2026 é refeito até a prestação final ficar completa: REFAZ_ANOS)."""
import csv, io, json, os, re, sys, zipfile, tempfile, datetime
from collections import defaultdict
from pathlib import Path
import requests

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "camp"; OUT.mkdir(exist_ok=True)
URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/prestacao_contas/prestacao_de_contas_eleitorais_candidatos_{ano}.zip"
ANOS = [int(a) for a in os.environ.get("ANOS", "2022 2024 2026").split()]
REFAZ_ANOS = {int(a) for a in os.environ.get("REFAZ_ANOS", "2026").split()}
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}
TOP = 10
MIN_IDX = float(os.environ.get("MIN_IDX", "1000"))   # doações a partir deste valor entram na busca "Quem financiou quem"
DOA = D / "doa"
normd = lambda s: re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", __import__("unicodedata").normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().upper())).strip()

def num(s):
    s = str(s or "").strip()
    if "," in s: s = s.replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return 0.0

def nome(s):
    s = re.sub(r"\s+", " ", str(s or "").strip())
    if not s or s.startswith("#NULO") or s == "#NE": return ""
    return s

def interesse():
    """SQ dos candidatos que o site mostra, por UF e ano."""
    q = defaultdict(lambda: defaultdict(set))
    for f in (D / "uf").glob("*.json"):
        U = json.load(open(f)); uf = f.stem
        for k, ano in (("de22", 2022), ("de26", 2026), ("df26", 2026), ("se26", 2026)):
            for p in U.get(k) or []:
                if len(p) > 10 and p[10]: q[ano][uf].add(str(p[10]))
        for m in (U.get("mun") or {}).values():
            for p in [m[1], m[2]] + list(m[3] or []):
                if p and len(p) > 10 and p[10]: q[2024][uf].add(str(p[10]))
    # deputados federais e senadores eleitos (lista do TSE gravada por votos_municipio.py) e governadores
    for f in (D / "vm").glob("*.json"):
        V = json.load(open(f)); uf = f.stem
        for ano, cs in V.get("anos", {}).items():
            for c in ("F", "S"):
                for x in cs.get(c, []):
                    if x[3]: q[int(ano)][uf].add(str(x[4]))
    try:
        BR = json.load(open(D / "br.json"))
        for uf, u in BR["ufs"].items():
            for k, ano in (("gov", 2022), ("gov26", 2026)):
                for p in u.get(k) or []:
                    if p and len(p) > 10 and p[10]: q[ano][uf].add(str(p[10]))
    except Exception as e: print("br.json:", e)
    return q

def rotas():
    """SQ do candidato -> [nome, cargo, UF, endereço da ficha], para a busca de doadores levar à ficha certa."""
    R = {}; tit = lambda x: " ".join(w.capitalize() for w in str(x).split())
    BR = json.load(open(D / "br.json"))
    dep = {normd(d[5]): d for d in BR["dep"]}; sen = {normd(x[2]): x for x in BR["sen"]}
    for uf, u in BR["ufs"].items():
        for k, a in (("gov", "22"), ("gov26", "26")):
            for i, p in enumerate((u.get(k) or [])[:2]):
                if p and len(p) > 10: R[str(p[10])] = [tit(p[0]), fem(("Governador" if i == 0 else "Vice-governador") + (" (eleito em 2026)" if a == "26" else ""), p[4]), uf, f"#/p/g/{uf}/{i}/{a}"]
    for f in (D / "uf").glob("*.json"):
        U = json.load(open(f)); uf = f.stem
        for k, a, t, c in (("de22", "22", "e", "Deputado estadual"), ("de26", "26", "e", "Deputado estadual (eleito em 2026)"), ("df26", "26", "f", "Deputado federal (eleito em 2026)"), ("se26", "26", "n", "Senador (eleito em 2026)")):
            for i, p in enumerate(U.get(k) or []):
                if len(p) > 10: R[str(p[10])] = [tit(p[0]), fem(c, p[4]), uf, f"#/p/{t}/{uf}/{a}/{i}"]
        for ue, m in (U.get("mun") or {}).items():
            for k, p in (("p", m[1]), ("v", m[2])) + tuple((str(i), q) for i, q in enumerate(m[3] or [])):
                if p and len(p) > 10: R[str(p[10])] = [tit(p[0]), fem({"p": "Prefeito", "v": "Vice-prefeito"}.get(k, "Vereador"), p[4]) + " · " + tit(m[0]), uf, f"#/p/m/{uf}/{ue}/{k}"]
    for f in (D / "vm").glob("*.json"):
        V = json.load(open(f)); uf = f.stem
        for x in (V.get("anos", {}).get("2022", {}).get("F") or []):
            d = dep.get(normd(x[1]))
            if x[3] and d: R[str(x[4])] = [d[1], fem("Deputado federal", d[10] if len(d) > 10 else ""), uf, f"#/p/c/{d[0]}"]
        for x in (V.get("anos", {}).get("2022", {}).get("S") or []):
            d = sen.get(normd(x[1]))
            if x[3] and d: R[str(x[4])] = [d[1], "Senador", uf, f"#/p/s/{d[0]}"]
    return R

ROTAS = {}
FEM = [("Governador", "Governadora"), ("Vice-governador", "Vice-governadora"), ("Deputado", "Deputada"), ("Senador", "Senadora"), ("Prefeito", "Prefeita"), ("Vice-prefeito", "Vice-prefeita"), ("Vereador", "Vereadora"), ("eleito", "eleita")]
def fem(c, sx):
    if sx != "F": return c
    for a, b in FEM: c = re.sub(r"\b" + a + r"\b", b, c)
    return c

def grava_indice(ano, idx, R):
    """site/data/doa/{ano}/{2 letras}.json: [[doador, total, nº de candidatos, [[nome, cargo, UF, ficha, valor] ... maiores 200]]]"""
    por = defaultdict(list)
    for (quem, uf, sq), v in idx.items():
        if v >= MIN_IDX and sq in R: por[quem].append(R[sq] + [round(v)])
    pasta = DOA / str(ano)
    if pasta.exists(): __import__("shutil").rmtree(pasta)
    pasta.mkdir(parents=True)
    G = defaultdict(list)
    for quem, L in por.items():
        L.sort(key=lambda x: -x[4]); k = (normd(quem).replace(" ", "") + "__")[:2]
        G[k].append([quem, sum(x[4] for x in L), len(L), L[:200]])
    for k, L in G.items():
        L.sort(key=lambda x: -x[1]); json.dump(L, open(pasta / f"{k}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(ano, "índice de doadores:", len(por), "doadores,", round(sum(p.stat().st_size for p in pasta.glob("*.json")) / 1e6, 1), "MB", flush=True)

def baixa(ano):
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    with requests.get(URL.format(ano=ano), headers=H, stream=True, timeout=(30, 1800)) as r:
        if r.status_code != 200: print(ano, "TSE respondeu", r.status_code, flush=True); return None
        for b in r.iter_content(1 << 20): tmp.write(b)
    tmp.close(); print(ano, "baixado:", round(os.path.getsize(tmp.name) / 1e6), "MB", flush=True); return tmp.name

def col(r, *ps):
    for k in r:
        if all(p in k for p in ps): return k

def um_ano(ano, alvo, saida, idx=None):
    f = baixa(ano)
    if not f: return False
    z = zipfile.ZipFile(f); feitos = set()
    for nm in z.namelist():
        base = nm.lower().rsplit("/", 1)[-1]
        m = re.match(r"(receitas|despesas_contratadas)_candidatos_\d{4}_([a-z]{2})\.csv$", base)
        if not m: continue
        tipo, uf = m.group(1), m.group(2).upper(); quer = alvo.get(uf)
        if not quer: continue
        A = defaultdict(lambda: defaultdict(float)); O = defaultdict(lambda: defaultdict(float)); T = defaultdict(float)
        with z.open(nm) as fh:
            rd = csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";"); ks = None
            for r in rd:
                if ks is None:
                    ks = {"sq": col(r, "SQ_CANDIDATO"), "v": col(r, "VR_RECEITA") if tipo == "receitas" else col(r, "VR_DESPESA_CONTRATADA"),
                          "n": col(r, "NM_DOADOR_RFB") if tipo == "receitas" else col(r, "NM_FORNECEDOR_RFB"),
                          "n2": col(r, "NM_DOADOR") if tipo == "receitas" else col(r, "NM_FORNECEDOR"),
                          "o": col(r, "DS_ORIGEM_RECEITA") if tipo == "receitas" else col(r, "DS_ORIGEM_DESPESA")}
                    ks["n2"] = ks["n2"] if ks["n2"] != ks["n"] else None
                sq = r.get(ks["sq"])
                if sq not in quer: continue
                v = num(r.get(ks["v"])); T[sq] += v
                quem = nome(r.get(ks["n"])) or nome(r.get(ks["n2"]) if ks["n2"] else "") or "Não informado"
                A[sq][quem] += v; ori = nome(r.get(ks["o"])) or "Outros"; O[sq][ori] += v
                if idx is not None and tipo == "receitas" and quem != "Não informado" and not re.search(r"pr[oó]prios", ori, re.I): idx[(quem, uf, sq)] += v
        S = saida.setdefault(uf, {})
        for sq in T:
            e = S.setdefault(sq, {"c": [0, [], 0, []]})
            top = sorted(A[sq].items(), key=lambda x: -x[1]); ori = [[k, round(v)] for k, v in sorted(O[sq].items(), key=lambda x: -x[1])]
            if tipo == "receitas": e["c"][0] = round(T[sq]); e["c"][1] = ori[:8]; e["d"] = [[k, round(v)] for k, v in top[:TOP]]; e["nd"] = len(top)
            else: e["c"][2] = round(T[sq]); e["c"][3] = ori[:6]; e["f"] = [[k, round(v)] for k, v in top[:TOP]]; e["nf"] = len(top)
        feitos.add(uf)
    os.unlink(f); print(ano, len(feitos), "estados", flush=True); return bool(feitos)

def arq(uf, ano): return OUT / (f"m{uf}.json" if ano == 2024 else f"{uf}.json")

def main():
    q = interesse(); res = {}
    for ano in ANOS:
        ja = all(arq(uf, ano).exists() and str(ano) in json.load(open(arq(uf, ano))).get("anos", []) for uf in q[ano]) if q[ano] else False
        ja = ja and (DOA / str(ano)).exists()   # sem o índice de doadores deste ano: baixa de novo uma vez
        if ja and os.environ.get("REFAZ") != "1" and ano not in REFAZ_ANOS: print(ano, "já gravado"); continue
        saida = {}; idx = defaultdict(float)
        try: ok = um_ano(ano, q[ano], saida, idx)
        except Exception as e: print(ano, "falhou:", repr(e), flush=True); continue
        if not ok: continue
        try: grava_indice(ano, idx, ROTAS or ROTAS.update(rotas()) or ROTAS)
        except Exception as e: print(ano, "índice de doadores falhou:", repr(e)[:200], flush=True)
        for uf, S in saida.items():
            p = arq(uf, ano)
            try: X = json.load(open(p))
            except Exception: X = {"anos": [], "dep": {}}
            # remove o que era deste ano e grava o novo
            X["dep"] = {k: v for k, v in X.get("dep", {}).items() if v.get("a") != ano}
            for sq, v in S.items(): v["a"] = ano; X["dep"][sq] = v
            X["anos"] = sorted(set(X.get("anos", [])) | {ano}); X["fonte"] = "TSE · Dados Abertos, prestação de contas eleitorais de candidatos (receitas e despesas contratadas)"
            X["gerado"] = datetime.date.today().isoformat()
            json.dump(X, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
        res[ano] = {"estados": len(saida), "candidatos": sum(len(s) for s in saida.values()), "alvo": sum(len(s) for s in q[ano].values())}
    print(json.dumps(res), json.dumps({p.name: round(p.stat().st_size / 1024) for p in sorted(OUT.glob("*.json"))}))

if __name__ == "__main__":
    main()
