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
au = j("ProjetosAutoresJSON?ano=2025") or j("ProjetosAutoresJSON?ano=2025&tipo=") or j("ProjetosAutoresJSON?ano=2025&tipo=PL"); print("AUT", len(au), json.dumps(au[:3], ensure_ascii=False)[:800], flush=True)
V = j("VereadoresCMSPJSON")
at = [v for v in V if any((m.get("fim") or "9999") >= "2026" and (m.get("inicio") or "") >= "2024" for m in v.get("mandatos") or [])]
print("VER atuais", len(at), flush=True)
print("VER1", json.dumps({k: v for k, v in at[0].items() if k != "cargos"}, ensure_ascii=False)[:1500], flush=True)
print("VERN", [v["nome"] for v in at], flush=True)
P = j("PromoventesCMSPJSON"); print("PROMTIPOS", Counter(p["tipo"]["nome"] for p in P), flush=True)
print("PROMVER", [p for p in P if p["tipo"]["nome"].startswith("VEREADOR")][:5], flush=True)
pj = j("ProjetosPorAnoJSON?ano=2025"); print("TIPOS", Counter(p["tipo"] for p in pj).most_common(30), flush=True)
