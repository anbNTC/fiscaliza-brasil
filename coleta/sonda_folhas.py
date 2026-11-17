"""Sonda temporária: colunas das folhas da Paraíba, de Goiás (SEAD) e da Prefeitura de Fortaleza."""
import sys, io, csv, json, re, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H, recente, texto
def pkg(ck, nome):
    return requests.get(f"{ck}/api/3/action/package_show?id={nome}", headers=H, timeout=60).json()["result"]
for ck, nome in [("https://dados.pb.gov.br", "remuneracao-servidores"), ("https://dadosabertos.go.gov.br", "folha-de-pagamento"), ("https://dados.fortaleza.ce.gov.br", "servidores-pmf")]:
    try:
        r = pkg(ck, nome); rs = r["resources"]
        print("PKG", nome, len(rs), [(x.get("name"), x.get("format"), (x.get("last_modified") or x.get("created") or "")[:10]) for x in rs][-6:], flush=True)
        x = recente(rs) or rs[-1]; print("URL", x["url"], flush=True)
        resp = requests.get(x["url"], headers={**H, "Range": "bytes=0-400000"}, timeout=120); b = resp.content
        if b[:2] == b"PK":
            import zipfile; z = zipfile.ZipFile(io.BytesIO(requests.get(x["url"], headers=H, timeout=300).content)); n = z.namelist()[0]; b = z.read(n)[:400000]; print("ZIP", n, flush=True)
        t = texto(b)
        if t.lstrip()[:1] in "[{":
            print("JSON", t[:1500], flush=True); continue
        sep = ";" if t[:3000].count(";") > t[:3000].count(",") else ","
        rows = list(csv.DictReader(io.StringIO(t.rsplit("\n", 1)[0]), delimiter=sep))
        print("COLS", nome, list(rows[0].keys()), flush=True)
        for row in rows[:2]: print("ROW", nome, {k: v for k, v in row.items()}, flush=True)
        for c in rows[0]:
            if re.search(r"lota|orgao|órgão|unidade|secretaria|cargo", c, re.I): print("TOP", nome, c, collections.Counter(r[c] for r in rows).most_common(6), flush=True)
        gov = [r for r in rows if re.search(r"GOVERNAD|GABINETE DO PREFEITO|CHEFIA DE GABINETE|GAB\.? PREF", json.dumps(r, ensure_ascii=False), re.I)]
        print("GAB", nome, len(gov), [dict(list(g.items())[:8]) for g in gov[:2]], flush=True)
    except Exception as e: print("ERRO", nome, repr(e)[:200], flush=True)
