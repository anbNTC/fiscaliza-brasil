"""Sonda temporária: conjunto de servidores no portal de dados abertos de Curitiba."""
import sys, re, io, csv, html, requests, collections
sys.path.insert(0, "coleta")
from prefeituras_abertas import H, texto
B = "https://dadosabertos.curitiba.pr.gov.br"
t = html.unescape(requests.get(B + "/conjuntodado/", headers=H, timeout=40).text)
print("PAGTXT", re.sub(r"\s+", " ", re.sub(r"<(script|style)[\s\S]*?</\1>|<[^>]+>", " ", t))[:2500], flush=True)
print("PAGLINKS", sorted(set(re.findall(r'href="([^"]*(?:pagina|page|termo|busca|categoria)[^"]*)"', t)))[:15], flush=True)
for q in ["/conjuntodado/?termo=servidores", "/conjuntodado/busca?termo=servidores", "/conjuntodado/?q=servidores"]:
    tt = html.unescape(requests.get(B + q, headers=H, timeout=40).text)
    print("BUSCA", q, len(tt), re.findall(r'detalhe\?chave=([\w-]+)', tt)[:8], [x.strip() for x in re.findall(r'<h\d[^>]*>([^<]{5,90})</h', tt)][:12], flush=True)
