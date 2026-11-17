"""Sonda temporária: conjunto de servidores no portal de dados abertos de Curitiba."""
import sys, re, io, csv, html, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H, texto
B = "https://dadosabertos.curitiba.pr.gov.br"
t = html.unescape(requests.get(B + "/conjuntodado/", headers=H, timeout=40).text)
ls = sorted(set(re.findall(r'href="([^"]*detalhe[^"]*)"[^>]*>\s*([^<]{3,90})<', t)))
print("LIST", len(ls), [x for x in ls if re.search(r"servid|cargo|pessoal|folha|remunera", x[1], re.I)][:10], ls[:5], flush=True)
alvo = next((x[0] for x in ls if re.search(r"servid", x[1], re.I)), None)
if alvo:
    d = html.unescape(requests.get(alvo if alvo.startswith("http") else B + alvo, headers=H, timeout=40).text)
    arqs = sorted(set(re.findall(r'href="([^"]+\.(?:csv|zip|xlsx?|json)[^"]*)"', d, re.I)))
    print("ARQ", len(arqs), arqs[-8:], flush=True)
    print("TXT", re.sub(r"\s+", " ", re.sub(r"<(script|style)[\s\S]*?</\1>|<[^>]+>", " ", d))[:1200], flush=True)
    if arqs:
        u = arqs[-1] if arqs[-1].startswith("http") else B + arqs[-1]
        b = requests.get(u, headers={**H, "Range": "bytes=0-300000"}, timeout=120).content
        if b[:2] == b"PK":
            import zipfile; b = zipfile.ZipFile(io.BytesIO(requests.get(u, headers=H, timeout=300).content)); n = b.namelist()[0]; b = b.read(n)[:300000]
        tt = texto(b); sep = ";" if tt[:3000].count(";") > tt[:3000].count(",") else ","
        rows = list(csv.DictReader(io.StringIO(tt.rsplit("\n", 1)[0]), delimiter=sep))
        print("COLS", u[-60:], list(rows[0].keys()), flush=True); print("ROW", rows[0], flush=True)
        for c in rows[0]:
            if re.search(r"lota|orgao|órgão|unidade|secret", c, re.I): print("TOP", c, collections.Counter(x[c] for x in rows).most_common(5), flush=True)
