"""Sonda temporária: autores dos projetos e vereadores atuais da Câmara Municipal de São Paulo (SPLegis)."""
import re, sys, json, requests
from collections import Counter
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
B = "https://splegisws.saopaulo.sp.leg.br/ws/ws2.asmx"
def j(u):
    r = requests.get(B + "/" + u, headers=H, timeout=300)
    try: return r.json()
    except Exception:
        m = re.search(r">\s*(\[.*\]|\{.*\})\s*<", r.text, re.S)
        if m: return json.loads(m.group(1))
        print("RAW", u, r.status_code, r.text[:400].replace("\n", " "), flush=True); return []
V = j("VereadoresCMSPJSON")
at = [v for v in V if any((m.get("fim") or "") >= "2026" and (m.get("inicio") or "") >= "2025" for m in v.get("mandatos") or [])]
print("VERN", len(at), [(v["chave"], v["nome"]) for v in at], flush=True)
c = at[0]["chave"]
for op in ["ProjetosEmTramitacaoPorPromoventeJSON", "LeisAprovadasPorPromoventeJSON", "ProjetosVetadosPorPromoventeJSON"]:
    for q in [f"promovente={c}", f"promovente={c}&ano=2025", f"codigo={c}", f"chave={c}"]:
        x = j(f"{op}?{q}")
        if x: print("RES", op, q, len(x), json.dumps(x[:2], ensure_ascii=False)[:700], flush=True); break
