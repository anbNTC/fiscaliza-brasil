"""Sonda temporária: links por autor e ano na consulta de Cuiabá."""
import re, sys, html
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
r = get("https://legislativo.camaracuiaba.mt.gov.br/spl/consulta-autor.aspx", headers={**H, "accept": "text/html"}, timeout=90)
t = r.text; i = t.find("Adevair Cabral")
print("RAW", re.sub(r"\s+", " ", t[i - 600:i + 1600]), flush=True)
print("VS", len(re.search(r'id="__VIEWSTATE" value="([^"]*)"', t).group(1)) if "__VIEWSTATE" in t else 0, flush=True)
hs = re.findall(r'href="([^"]+)"[^>]*>\s*2025\s*<', t); print("H2025", len(hs), hs[:5], flush=True)
