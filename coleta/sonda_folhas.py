"""Sonda temporária: colunas da "Relação de servidores, cargos e encargos" de Curitiba."""
import sys, re, io, csv, html, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H, texto
B = "https://dadosabertos.curitiba.pr.gov.br"
d = html.unescape(requests.get(B + "/conjuntodado/detalhe?chave=CB9CBEB2-1C2C-48BA-A632-25EDCB766744", headers=H, timeout=40).text)
print("TIT", re.findall(r"<h\d[^>]*>([^<]{5,90})</h", d)[:4], flush=True)
arqs = sorted(set(re.findall(r'href="([^"]+)"[^>]*>[^<]*(?:csv|CSV|Download|Baixar)', d))) + sorted(set(re.findall(r'href="([^"]+\.(?:csv|zip)[^"]*)"', d, re.I)))
print("ARQ", len(arqs), arqs[-10:], flush=True)
print("TXT", re.sub(r"\s+", " ", re.sub(r"<(script|style)[\s\S]*?</\1>|<[^>]+>", " ", d))[300:2200], flush=True)
for u in arqs[-3:]:
    u = u if u.startswith("http") else B + u
    try:
        b = requests.get(u, headers={**H, "Range": "bytes=0-400000"}, timeout=120).content
        tt = texto(b); sep = ";" if tt[:3000].count(";") > tt[:3000].count(",") else ","
        rows = list(csv.DictReader(io.StringIO(tt.rsplit("\n", 1)[0]), delimiter=sep))
        print("COLS", u[-70:], list(rows[0].keys()), flush=True); print("ROW", rows[0], flush=True)
        for c in rows[0]:
            if re.search(r"lota|orgao|órgão|unidade|secret|cargo", c, re.I): print("TOP", c, collections.Counter(x[c] for x in rows).most_common(6), flush=True)
        g = [x for x in rows if re.search(r"GABINETE DO PREFEITO|PREFEITO MUNICIPAL|CHEFE DE GABINETE", " ".join(x.values()), re.I)]
        print("GAB", len(g), g[:2], flush=True)
        break
    except Exception as e: print("ERRO", u[-60:], repr(e)[:150], flush=True)
