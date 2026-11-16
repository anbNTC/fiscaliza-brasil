"""Sonda temporária: nome de cada tipo e filtro combinado autor+tipo+ano em Cuiabá."""
import re, sys, html, time
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
B = "https://legislativo.camaracuiaba.mt.gov.br/spl/"
def pg(q):
    t = html.unescape(get(B + "consulta-producao.aspx?" + q, headers={**H, "accept": "text/html"}, timeout=90).text); s = re.sub(r"<[^>]+>", " ", t)
    tot = re.search(r"Localizada\(s\)\s*(\d+)", re.sub(r"\s+", " ", s)); tit = re.findall(r"([A-ZÀ-Úa-zà-ú ]+?) n° \d+/\d{4}", s)
    return (int(tot.group(1)) if tot else 0), (tit[0].strip() if tit else ""), re.sub(r"\s+", " ", s)
for q in ["autor=8219&tipo=103&ano=2025", "autor=8219&tipo=103&ano_proposicao=2025", "autor=8219&ano=2025&tipo=116", "autor=8219&tipo=116&ano_proposicao=2025"]:
    n, nome, s = pg(q); print("COMB", q, n, nome, flush=True); time.sleep(0.5)
