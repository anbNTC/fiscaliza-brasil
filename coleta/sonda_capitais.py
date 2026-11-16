"""Sonda temporária: consulta por tipo de Cuiabá e mapa por tipo de um vereador."""
import re, sys, html
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
B = "https://legislativo.camaracuiaba.mt.gov.br/spl/"
t = html.unescape(get(B + "consulta-tipo.aspx", headers={**H, "accept": "text/html"}, timeout=90).text)
ls = re.findall(r"<div class='card-title[^>]*>([^<]+?)\((\d+)\)<[\s\S]*?</div></div></div>", t)
print("TIPOS", [(a.strip(), b) for a, b in ls][:40], flush=True)
print("TLINKS", sorted(set(re.findall(r"href='(consulta-[a-z]+\.aspx\?[^']*(?:2025|2026)[^']*)'", t)))[:40], flush=True)
