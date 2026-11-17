"""Sonda temporária: endereço real do download no portal de dados abertos de Curitiba."""
import sys, re, html, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://dadosabertos.curitiba.pr.gov.br"
d = html.unescape(requests.get(B + "/conjuntodado/detalhe?chave=CB9CBEB2-1C2C-48BA-A632-25EDCB766744", headers=H, timeout=40).text)
print("MID", sorted(set(re.findall(r'https?://[\w.-]*curitiba[\w./%-]*\.(?:csv|zip)', d)))[:5], flush=True)
i = d.find("function downloadArquivos")
if i >= 0: print("FN", re.sub(r"\s+", " ", d[i:i + 800]), flush=True)
for js in re.findall(r'<script[^>]*src="([^"]+)"', d):
    u = js if js.startswith("http") else B + js
    try: t = requests.get(u, headers=H, timeout=30).text
    except Exception: continue
    j = t.find("downloadArquivos")
    if j >= 0: print("JSFN", u, re.sub(r"\s+", " ", t[max(0, j - 100):j + 900]), flush=True)
