"""Emendas de deputados estaduais ao orçamento do estado, onde o governo publica em dados abertos com o nome do autor.
Hoje: Pernambuco (dados.pe.gov.br), Minas Gerais (dados.mg.gov.br) e Goiás (dadosabertos.go.gov.br), de 2023 em diante.
Os três portais são CKAN: lemos a lista de arquivos do conjunto e baixamos os que trazem autor, município e valores.
Saída: site/data/emendas_est/{UF}.json
  {"fonte", "url", "gerado", "metrica", "dep": {"chave": [nome, k_de22 (int) | chave "x..." da Assembleia | None, total, pago, [[cidade, valor] x10]]},
   "cid": {CIDADE_NORMALIZADA: [[chave, valor] ...]}}"""
import csv, difflib, io, json, re, sys, datetime, zipfile
import sys as _s; from pathlib import Path as _P; _s.path.insert(0, str(_P(__file__).resolve().parent)); from legislatura import lista_est
from collections import defaultdict
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from assembleias_sapl import limpa, norm

D = Path(__file__).resolve().parents[1] / "site" / "data"; OUT = D / "emendas_est"; OUT.mkdir(exist_ok=True)
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}
ANO0 = 2023
csv.field_size_limit(1 << 30)

def num(s):
    s = str(s or "").strip().replace("R$", "").strip()
    if not s: return 0.0
    if "," in s: s = s.replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return 0.0

def recursos(base, pid):
    r = requests.get(f"{base}/api/3/action/package_show", params={"id": pid}, headers=H, timeout=90).json()["result"]
    return r["resources"]

def baixa(u):
    r = requests.get(u, headers=H, timeout=(30, 600)); r.raise_for_status(); b = r.content
    if b[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(b)); b = b"".join(z.read(n) for n in z.namelist() if n.lower().endswith(".csv"))
    for enc in ("utf-8-sig", "latin-1"):
        try: return b.decode(enc)
        except UnicodeDecodeError: pass

def linhas(texto):
    sep = ";" if texto[:2000].count(";") >= texto[:2000].count(",") else ","
    return csv.DictReader(io.StringIO(texto), delimiter=sep)

def ano_ok(v):
    m = re.search(r"(20\d\d)", str(v or "")); return bool(m) and int(m.group(1)) >= ANO0

# cada estado devolve itens (autor, município, empenhado, pago, beneficiário)
def pe():
    rs = recursos("https://dados.pe.gov.br", "emendasparlamentaresestaduais")
    for x in rs:
        nm = x["name"].lower(); u = x["url"]
        if "tabela completa" in nm and u.lower().endswith(".csv"):
            for r in linhas(baixa(u)):
                if ano_ok(r.get("ano")): yield r.get("autor"), r.get("municipio"), num(r.get("valor_empenhado")), num(r.get("valor_pago")) + num(r.get("valor_rp_pago")), r.get("nome_credor")
        elif re.search(r"emendas parlamentares estaduais (202[3-5])", nm) and (x.get("format") or "").upper() == "JSON":
            try: js = requests.get(u, headers=H, timeout=300).json()
            except Exception as e: print("PE json", nm, e); continue
            its = js if isinstance(js, list) else next((v for v in js.values() if isinstance(v, list)), []) if isinstance(js, dict) else []
            if not its or "autor" not in its[0]: print("PE", nm, "sem autor; campos:", list(its[0])[:12] if its else []); continue
            for r in its:
                yield r.get("autor"), r.get("municipio"), num(r.get("valor_empenhado") or r.get("vlrempenhado")), num(r.get("valor_pago") or r.get("vlrtotalpago")), r.get("nome_credor") or r.get("credor")

def mg():
    rs = recursos("https://dados.mg.gov.br", "portal_emendas_estaduais")
    u = next(x["url"] for x in rs if "indica" in x["name"].lower())
    for r in linhas(baixa(u)):
        if ano_ok(r.get("ano_exercicio")): yield r.get("responsavel"), r.get("municipio"), num(r.get("valor_empenhado")) or num(r.get("valor_indicacao")), num(r.get("valor_pago")), r.get("beneficiario_nome")

def go():
    rs = recursos("https://dadosabertos.go.gov.br", "emendas-parlamentares")
    # o arquivo mais recente traz de 2020 até hoje
    u = next(x["url"] for x in rs if "2026" in x["name"] and (x.get("format") or "").upper() == "CSV")
    for r in linhas(baixa(u)):
        k = {norm(a): a for a in r}
        g = lambda *ps: next((r[v] for c, v in k.items() if all(p in c for p in ps)), "")
        if ano_ok(g("EXERCICIO")): yield g("AUTOR"), g("MUNICIPIO"), num(g("VALOR EMPENHO")), num(g("OP")), g("BENEFICIARIO NOME")

ESTADOS = {"PE": (pe, "Governo de Pernambuco · Portal de Dados Abertos (dados.pe.gov.br), Emendas Parlamentares Estaduais", "https://dados.pe.gov.br/dataset/emendasparlamentaresestaduais"),
           "MG": (mg, "Governo de Minas Gerais · Portal de Dados Abertos (dados.mg.gov.br), Emendas Parlamentares Estaduais", "https://dados.mg.gov.br/dataset/portal_emendas_estaduais"),
           "GO": (go, "Governo de Goiás · Dados Abertos (dadosabertos.go.gov.br), Emendas Parlamentares", "https://dadosabertos.go.gov.br/dataset/emendas-parlamentares")}

def liga(nomes, de):
    """nome do autor -> índice em de22 (eleitos de 2022 no TSE)."""
    idx = {}
    for k, x in enumerate(de): idx.setdefault(limpa(x[0]), k); idx.setdefault(limpa(x[1]), k)
    toks = [(k, set(limpa(x[0]).split()) | set(limpa(x[1]).split())) for k, x in enumerate(de)]
    out = {}
    for n in nomes:
        k = idx.get(limpa(n))
        if k is None:
            tt = set(limpa(n).split())
            best = sorted(((len(tt & q) / max(1, min(len(tt), len(q))), len(tt & q), j) for j, q in toks), reverse=True)
            if tt and best and (len(best) < 2 or best[1][:2] < best[0][:2]) and best[0][0] >= 0.99 and best[0][1] >= min(2, len(tt)): k = best[0][2]
        if k is None:
            # nome de urna inteiro dentro do nome do autor ("ZELI" em "Zeli Fritshe"), sem ambiguidade
            tt = set(limpa(n).split()); cs = [j for j, x in enumerate(de) if limpa(x[0]) and set(limpa(x[0]).split()) <= tt]
            if len(cs) == 1: k = cs[0]
        if k is None:
            r = sorted(((difflib.SequenceMatcher(None, limpa(n), limpa(x[0])).ratio(), j) for j, x in enumerate(de)), reverse=True)
            if r and r[0][0] >= 0.86 and (len(r) < 2 or r[1][0] < r[0][0] - 0.05): k = r[0][1]
        out[n] = k
    return out

def liga_est(nomes, uf):
    """quem não está entre os eleitos de 2022: procura na lista da Assembleia (suplentes que assumiram, chaves "x...")."""
    try: E = json.load(open(D / "est" / f"{uf}.json"))["dep"]
    except Exception: return {}
    idx = {limpa(v["nome"]): k for k, v in E.items() if k[0] == "x"}
    return {n: idx[limpa(n)] for n in nomes if limpa(n) in idx}

def um(uf):
    fn, fonte, url = ESTADOS[uf]
    tot = defaultdict(lambda: [0.0, 0.0]); cid = defaultdict(lambda: defaultdict(float)); nome = {}
    n = 0
    for a, m, emp, pago, ben in fn():
        a = re.sub(r"\s+", " ", (a or "").strip()); m = norm(m)
        if not a or (not emp and not pago): continue
        ch = limpa(a) or norm(a); nome.setdefault(ch, a)
        tot[ch][0] += emp; tot[ch][1] += pago; cid[ch][m or "SEM MUNICIPIO"] += emp or pago; n += 1
    de, ANO_LEG = lista_est(json.load(open(D / "uf" / f"{uf}.json")))
    L = liga([nome[c] for c in tot], de)
    L.update({n: k for n, k in liga_est([n for n, k in L.items() if k is None], uf).items()})
    dep = {}
    for ch, (e, p) in tot.items():
        nm = nome[ch]; nm = " ".join(w.capitalize() if len(w) > 2 else w.lower() for w in nm.split()) if nm.isupper() else nm
        dep[ch] = [nm, L[nome[ch]], round(e), round(p), [[c, round(v)] for c, v in sorted(cid[ch].items(), key=lambda x: -x[1])[:10]]]
    porCid = defaultdict(list)
    for ch, cs in cid.items():
        for c, v in cs.items(): porCid[c].append([ch, round(v)])
    for c in porCid: porCid[c].sort(key=lambda x: -x[1])
    out = {"fonte": fonte, "url": url, "gerado": datetime.date.today().isoformat(), "desde": ANO0,
           "metrica": "valor empenhado (reservado no orçamento para pagar), de " + str(ANO0) + " até hoje", "dep": dep, "cid": porCid}
    out["ano"] = ANO_LEG
    json.dump(out, open(OUT / f"{uf}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    lig = sum(1 for v in dep.values() if v[1] is not None)
    r = {"uf": uf, "linhas": n, "autores": len(dep), "ligados": lig, "empenhado": round(sum(v[2] for v in dep.values())), "pago": round(sum(v[3] for v in dep.values())),
         "sem_par": sorted(((v[0], v[2]) for v in dep.values() if v[1] is None), key=lambda x: -x[1])[:8]}
    print(json.dumps(r, ensure_ascii=False), flush=True); return r

def main(ufs=None):
    res = []
    for uf in ufs or ESTADOS:
        try: res.append(um(uf))
        except Exception as e: print(uf, "falhou:", repr(e), flush=True)
    return res

if __name__ == "__main__":
    main(sys.argv[1:] or None)
