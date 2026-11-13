"""Sonda temporária: formato dos métodos do web service aberto da Câmara Municipal de São Paulo (SPLegis)."""
import re, sys, json, html, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://splegisws.saopaulo.sp.leg.br/ws/ws2.asmx"
for op in ["ProjetosPorAnoJSON", "ProjetosAutoresJSON", "VereadoresCMSPJSON", "PromoventesCMSPJSON", "TiposDeMateriaJSON"]:
    d = html.unescape(requests.get(f"{B}?op={op}", headers=H, timeout=60).text)
    print("GET", op, re.findall(r"GET (/ws/ws2\.asmx/\S+)", d)[:1], flush=True)
def j(u):
    r = requests.get(B + "/" + u, headers=H, timeout=300); t = r.text
    try: return json.loads(t)
    except Exception:
        m = re.search(r">(\[.*\]|\{.*\})<", t, re.S); return json.loads(m.group(1)) if m else t[:300]
for u in ["VereadoresCMSPJSON", "PromoventesCMSPJSON", "TiposDeMateriaJSON", "ProjetosPorAnoJSON?ano=2025", "ProjetosAutoresJSON"]:
    try:
        x = j(u); n = len(x) if isinstance(x, list) else "?"
        print("RES", u, n, json.dumps(x[:3] if isinstance(x, list) else x, ensure_ascii=False)[:900], flush=True)
    except Exception as e: print("RES", u, "erro", repr(e)[:200], flush=True)
