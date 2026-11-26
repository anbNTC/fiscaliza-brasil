"""Sonda temporária: caminhos da API de servidores no código do portal Elotech."""
import sys, re, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://maringa.oxy.elotech.com.br"
s = requests.get(B + "/portaltransparencia/static/js/main.ad8f87f3.chunk.js", headers=H, timeout=60).text
print("LEN", len(s), flush=True)
for k in ['"/api/servidores?"', "/api/servidores?"]:
    j = s.find(k)
    while j >= 0 and j < len(s):
        print("CALL", s[max(0, j - 500):j + 400].replace("\n", " "), flush=True); j = s.find(k, j + 1)
        if j < 0: break
    break
