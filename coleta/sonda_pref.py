"""Sonda temporária: caminhos da API de servidores no código do portal Elotech."""
import sys, re, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://maringa.oxy.elotech.com.br"
s = requests.get(B + "/portaltransparencia/static/js/main.ad8f87f3.chunk.js", headers=H, timeout=60).text
print("LEN", len(s), flush=True)
for m in sorted(set(re.findall(r'["\'`]([/\w.${}-]*(?:servidor|folha|remunera)[/\w.${}?=&-]*)["\'`]', s, re.I)))[:60]: print("PATH", m, flush=True)
i = s.find("servidores"); print("CTX", s[max(0, i - 600):i + 600].replace("\n", " "), flush=True)
