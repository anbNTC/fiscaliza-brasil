"""Sonda temporária: Instagram de cada vereador de Curitiba, pela página oficial de cada um no site da Câmara."""
import re, sys, json, time
sys.path.insert(0, "coleta")
from saida_br import get
B = "https://www.cmc.pr.gov.br"
t = get(f"{B}/vereadores/conheca-os-vereadores", headers={"accept": "text/html"}, timeout=90).text
for s in dict.fromkeys(re.findall(r'/vereadores/([a-z0-9-]+)"', t)):
    r = get(f"{B}/++api++/vereadores/{s}", headers={"accept": "application/json"}, timeout=90)
    if r is None or not r.ok: continue
    j = r.json()
    if j.get("@type") != "vereador" or j.get("ex_vereador"): continue
    txt = json.dumps(j, ensure_ascii=False)
    ig = sorted(set(x.strip("/").split("?")[0] for x in re.findall(r"instagram\.com/([A-Za-z0-9_.]+)", txt)))
    chaves = [k for k in j if re.search(r"insta|social|rede", k, re.I)]
    print("VER", j.get("title"), "|", (j.get("partido") or {}).get("title") if isinstance(j.get("partido"), dict) else j.get("partido"), "|", ig, "|", {k: j[k] for k in chaves}, "| licenciado" if j.get("licenciado") else "", flush=True)
    time.sleep(0.3)
