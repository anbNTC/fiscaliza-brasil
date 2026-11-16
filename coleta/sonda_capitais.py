"""Sonda temporária: consulta de proposições por autor da Câmara de Cuiabá (ASP.NET)."""
import re, sys, html
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
for u in ["https://legislativo.camaracuiaba.mt.gov.br/spl/consulta-autor.aspx", "https://legislativo.camaracuiaba.mt.gov.br/spl/consulta-cronologico.aspx"]:
    r = get(u, headers={**H, "accept": "text/html"}, timeout=60)
    if r is None: print("CBA", u, "sem resposta", flush=True); continue
    t = html.unescape(r.text)
    print("CBA", u, r.status_code, len(t), "| captcha" if re.search(r"captcha", t, re.I) else "", flush=True)
    print("CAMPOS", [(a, b) for a, b in re.findall(r'<(input|select)[^>]*name="([^"]+)"', t)][:25], flush=True)
    sel = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>([^<]{2,60})</option>', t)
    print("OPCOES", len(sel), sel[:12], flush=True)
    print("TXT", re.sub(r"\s+", " ", re.sub(r"<(script|style)[\s\S]*?</\1>|<[^>]+>", " ", t))[:1200], flush=True)
    print("LINKS", sorted(set(re.findall(r'href="([^"]*(?:autor|proposi|materia|Detalhe|\.aspx\?)[^"]*)"', t)))[:15], flush=True)
