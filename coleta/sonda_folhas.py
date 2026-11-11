"""Sonda temporária: folhas de SP (capital) e PE (estado) pela saída do Brasil."""
import csv, io, json, re, sys
from collections import Counter
sys.path.insert(0, "coleta")
from saida_br import get
from prefeituras_abertas import recente
def J(u):
    r = get(u, headers={"accept": "application/json"}, timeout=120, tentativas=2); return r.json() if r is not None and r.ok else None
for base, q in [("https://dados.prefeitura.sp.gov.br", "Relação de Servidores Ativos"), ("https://dados.prefeitura.sp.gov.br", "Histórico de Remuneração dos Servidores Ativos"), ("https://dados.pe.gov.br", "remuneracao-de-servidores")]:
    print("\n########", base, q, flush=True)
    if base.endswith("pe.gov.br"): pk = J(f"{base}/api/3/action/package_show?id={q}")["result"]
    else:
        s = J(f"{base}/api/3/action/package_search?q=" + q.replace(" ", "+") + "&rows=5")["result"]["results"]
        pk = next((p for p in s if p["title"].lower().startswith(q.lower()[:25])), s[0])
    res = pk.get("resources") or []
    print("pacote:", pk["name"], "| recursos:", len(res)); print("  últimos:", [(r.get("name"), r.get("format"), (r.get("url") or "")[-60:]) for r in res[-5:]])
    cand = [r for r in res if not re.search(r"inativ|aposent|pension|json", (r.get("name") or "") + (r.get("format") or ""), re.I)]
    r = recente(cand) or (cand[-1] if cand else None)
    if not r: continue
    print("arquivo:", r.get("name"), r.get("url"), flush=True)
    rr = get(r["url"], headers={"accept": "*/*"}, timeout=300, tentativas=2)
    if rr is None: print("sem resposta"); continue
    b = rr.content; print("bytes", len(b), rr.headers.get("content-type"))
    if b[:2] == b"PK": print("zip/xlsx"); continue
    t = b.decode("utf-8-sig", "ignore") if b"\xc3" in b[:300000] else b.decode("latin-1")
    sep = ";" if t[:3000].count(";") > t[:3000].count(",") else ","
    rd = csv.reader(io.StringIO(t), delimiter=sep); cab = next(rd); print("colunas:", cab)
    C = Counter(); ex = []; n = 0
    for row in rd:
        n += 1
        for i, v in enumerate(row):
            if i < len(cab) and re.search(r"GAB.*PREFEIT|PREFEITO|GOVERNADOR|VICE-GOV", v, re.I) and len(v) < 120: C[(cab[i], v.strip())] += 1
        if len(ex) < 2 and any(re.search(r"GABINETE DO (PREFEITO|GOVERNADOR)", v, re.I) for v in row): ex.append(row)
    print("linhas", n)
    for (c, v), k in C.most_common(25): print("  ", k, "|", c, "|", v)
    print("  exemplo:", ex)
    sys.stdout.flush()
