"""Sonda temporária: lista de arquivos e lotações do gabinete do prefeito em Curitiba."""
import sys, re, io, csv, html, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H, texto
B = "https://dadosabertos.curitiba.pr.gov.br"
j = requests.get(B + "/ConjuntoDado/DownloadArquivos/", params={"conjuntoDadoChave": "cb9cbeb2-1c2c-48ba-a632-25edcb766744", "conjuntoDadoExtensao": "377f4e23-0e4f-4f11-954f-ae06ba689558", "pagina": 1, "tamanhoPagina": 50}, headers={**H, "x-requested-with": "XMLHttpRequest"}, timeout=60).json()
tb = html.unescape(j.get("tabela") or ""); links = re.findall(r'href="([^"]+)"', tb)
print("LINKS", len(links), links[:4], j.get("paginacao"), flush=True)
print("TB", re.sub(r"\s+", " ", tb)[:1500], flush=True)
links = links or re.findall(r"(?:onclick|data-[\w-]+)=\"([^\"]+)\"", tb)
print("ATTR", links[:6], flush=True)
raise SystemExit
u = links[0] if links[0].startswith("http") else B + links[0]
t = texto(requests.get(u, headers=H, timeout=600).content)
rows = list(csv.DictReader(io.StringIO(t), delimiter=";" if t[:3000].count(";") > t[:3000].count(",") else ","))
print("N", len(rows), list(rows[0].keys()), flush=True)
lot = collections.Counter(r["LOTACAO"] for r in rows)
print("LOT", len(lot), [x for x in lot.items() if re.search(r"GABINETE|PREFEIT|VICE|GOVERNO MUNICIPAL", x[0])][:20], flush=True)
print("CHEFE", sorted({(r["NOME"], r["CARGO"], r["CARGO_COMISSAO"], r["LOTACAO"], r["TOT_VANTAGENS"]) for r in rows if re.search(r"PREFEIT", r["CARGO"] + " " + r["CARGO_COMISSAO"])})[:8], flush=True)
print("EVENTOS", collections.Counter(r["TIPO_EVENTO"] for r in rows).most_common(4), "pessoas:", len({r["NOME"] for r in rows}), flush=True)
