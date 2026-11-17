"""Sonda temporária: órgãos do governador em Goiás, arquivos de Fortaleza e recurso da Paraíba."""
import sys, io, csv, re, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H, texto
pk = lambda ck, n: requests.get(f"{ck}/api/3/action/package_show?id={n}", headers=H, timeout=60).json()["result"]
r = pk("https://dados.pb.gov.br", "remuneracao-servidores"); print("PB", [{k: v for k, v in x.items() if k in ("name", "url", "format", "description", "access_url", "download_url")} for x in r["resources"]][:2], r.get("url"), flush=True)
r = pk("https://dados.fortaleza.ce.gov.br", "servidores-pmf"); print("FOR", [(x["name"], x["url"][-30:]) for x in r["resources"]], flush=True)
u = "https://dadosabertos.go.gov.br/dataset/9cec56e2-8e10-472f-b060-d925ba3b29b5/resource/5a09150b-5708-4c09-a094-da432b179c91/download/folhapagamento_202608.csv"
t = texto(requests.get(u, headers=H, timeout=600).content)
rows = list(csv.DictReader(io.StringIO(t), delimiter=";"))
og = collections.Counter(r["ORGAO"] for r in rows)
print("GOORG", [(o, n) for o, n in og.items() if re.search(r"GOVERN|VICE|CASA CIVIL|GABINETE|MILITAR DO GOV|CERIMON", o, re.I)], flush=True)
ch = [(r["NOMESERVIDOR"], r["NOMECARGO"], r["NOMECARGOSECUNDARIO"], r["ORGAO"]) for r in rows if re.search(r"^(VICE-?)?GOVERNADOR", r["NOMECARGO"] + " " + r["NOMECARGOSECUNDARIO"], re.I) or re.search(r"\bGOVERNADOR\b", r["NOMECARGO"], re.I)]
print("GOCHEFE", ch[:6], flush=True)
