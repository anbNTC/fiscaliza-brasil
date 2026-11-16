"""Sonda temporária: produção por autor e ano na consulta de Cuiabá."""
import re, sys, html
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
B = "https://legislativo.camaracuiaba.mt.gov.br/spl/"
t = html.unescape(get(B + "consulta-autor.aspx", headers={**H, "accept": "text/html"}, timeout=90).text)
au = []
for m in re.finditer(r"<div class='card-title[^>]*>([^<]+?)\((\d+)\)<[\s\S]*?</div></div></div>", t):
    anos = re.findall(r"consulta-producao\.aspx\?autor=(\d+)&ano=(\d{4})", m.group(0))
    if any(a >= "2025" for _, a in anos): au.append((m.group(1).strip(), anos[0][0], sorted({a for _, a in anos if a >= "2025"})))
print("AUT", len(au), au[:60], flush=True)
nome, aid, _ = next(x for x in au if x[0].upper().startswith(("A", "B", "C", "D")) and "MESA" not in x[0].upper() and "COMISS" not in x[0].upper() and "PREFEIT" not in x[0].upper())
p = html.unescape(get(B + f"consulta-producao.aspx?autor={aid}&ano=2025", headers={**H, "accept": "text/html"}, timeout=90).text)
print("PROD", nome, len(p), re.sub(r"\s+", " ", re.sub(r"<(script|style|svg)[\s\S]*?</\1>|<[^>]+>", " | ", p))[1500:5000], flush=True)
print("PLINKS", sorted(set(re.findall(r"href='([^']*(?:processo|proposi|Detalhe|\.aspx\?)[^']*)'", p)))[:10], flush=True)
