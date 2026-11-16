"""Sonda temporária: paginação, mapa por tipo e filtros da produção por autor em Cuiabá."""
import re, sys, html
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
B = "https://legislativo.camaracuiaba.mt.gov.br/spl/"
p = html.unescape(get(B + "consulta-producao.aspx?autor=8219&ano=2025", headers={**H, "accept": "text/html"}, timeout=90).text)
print("ITENS", len(re.findall(r"Processo N°:", re.sub(r"<[^>]+>", " ", p))), "| total:", re.findall(r"Localizada\(s\)[\s\S]{0,200}?(\d+)", re.sub(r"<[^>]+>", " ", p))[:1], flush=True)
i = p.find("MAPA DE PROPOSI"); print("MAPA", re.sub(r"\s+", " ", re.sub(r"<(script|style|svg)[\s\S]*?</\1>|<[^>]+>", " | ", p[i:i + 6000]))[:1500], flush=True)
print("MAPALINKS", sorted(set(re.findall(r"href='([^']*consulta-producao[^']*)'", p)))[:20], flush=True)
print("PAG", sorted(set(re.findall(r"(?:href|onclick)='([^']*(?:pagina|page|Page\$)[^']*)'", p)))[:10], re.findall(r"__doPostBack\('([^']+)','([^']*)'\)", p)[:8], flush=True)
print("DOWN", re.findall(r"href='([^']*(?:download|Download|xls|csv|pdf)[^']*)'", p)[:5], flush=True)
