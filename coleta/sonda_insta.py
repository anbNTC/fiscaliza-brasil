"""Sonda temporária: Instagram de cada vereador de Curitiba.
1) site da Câmara (campo instagram do perfil); 2) redes sociais declaradas ao TSE no registro da candidatura de 2024 (DivulgaCandContas)."""
import re, sys, json, time, unicodedata
sys.path.insert(0, "coleta")
import requests
from saida_br import get
sa = lambda x: re.sub(r"[^A-Z ]", "", unicodedata.normalize("NFKD", str(x or "")).encode("ascii", "ignore").decode().upper()).strip()
B = "https://www.cmc.pr.gov.br"
t = get(f"{B}/vereadores/conheca-os-vereadores", headers={"accept": "text/html"}, timeout=90).text
VER = []
for s in dict.fromkeys(re.findall(r'/vereadores/([a-z0-9-]+)"', t)):
    r = get(f"{B}/++api++/vereadores/{s}", headers={"accept": "application/json"}, timeout=90)
    if r is None or not r.ok: continue
    j = r.json()
    if j.get("@type") != "vereador" or j.get("ex_vereador"): continue
    VER.append({"nome": j.get("title"), "civil": j.get("nome_civil") or j.get("nome_completo") or "", "cmc": j.get("instagram") or ""})
    time.sleep(0.2)
print("CMC", len(VER), "vereadores; chaves de nome:", flush=True)

T = "https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura"
HD = {"accept": "application/json", "user-agent": "Mozilla/5.0"}
def tse(u):
    for _ in range(3):
        try:
            r = requests.get(u, headers=HD, timeout=60)
            if r.ok: return r.json()
            print("TSE", r.status_code, u[-60:], flush=True)
        except Exception as e: print("TSE erro", repr(e)[:120], flush=True)
        time.sleep(3)
lst = tse(f"{T}/listar/2024/75353/2045202024/13/candidatos")
cands = (lst or {}).get("candidatos") or []
print("TSE", len(cands), "candidatos a vereador em Curitiba", flush=True)
for v in VER:
    alvo = sa(v["nome"])
    c = next((c for c in cands if sa(c.get("nomeUrna")) == alvo), None) or next((c for c in cands if alvo and (alvo in sa(c.get("nomeUrna")) or sa(c.get("nomeUrna")) in alvo) and "ELEIT" in sa(c.get("descricaoTotalizacao")) + "ELEIT"), None)
    sites = []
    if c:
        d = tse(f"{T}/buscar/2024/75353/2045202024/candidato/{c['id']}") or {}
        sites = d.get("sites") or []
        time.sleep(0.5)
    print("VER", v["nome"], "|", c and c.get("nomeUrna"), "|", c and c.get("descricaoTotalizacao"), "| CMC:", v["cmc"], "| TSE:", sites, flush=True)
