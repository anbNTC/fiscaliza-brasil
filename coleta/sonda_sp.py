"""Sonda temporária: métodos do web service aberto da Câmara Municipal de São Paulo (SPLegis)."""
import re, sys, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://splegisws.saopaulo.sp.leg.br/ws/ws2.asmx"
t = requests.get(B, headers=H, timeout=60).text
ops = sorted(set(re.findall(r'\?op=([A-Za-z0-9_]+)', t))); print("OPS", ops, flush=True)
for op in [o for o in ops if re.search(r"Projet|Vot|Vereador|Autor|Parlament|Presen", o)][:40]:
    d = requests.get(f"{B}?op={op}", headers=H, timeout=60).text
    ps = re.findall(r'<td>(\w+):</td>', d)
    print("OP", op, ps[:12], flush=True)
