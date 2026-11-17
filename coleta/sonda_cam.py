"""Sonda temporária: acha o SAPL de câmaras maiores sem dados pelo link no próprio site da câmara (Portal Modelo e afins)."""
import sys, re, json, requests, concurrent.futures as cf, collections
sys.path.insert(0, "coleta")
import camaras_sapl as C
from assembleias_sapl import H
idx = json.load(open(C.OUT / "index.json"))
alvos = []
for f in sorted((C.D / "uf").glob("*.json")):
    U = json.load(open(f))
    for ue, m in U.get("mun", {}).items():
        if ue not in idx and len(m[3] or []) >= 13: alvos.append((f.stem, ue, m[0], len(m[3])))
print("RES alvos (13+ vereadores, sem dados):", len(alvos), flush=True)
def acha(a):
    uf, ue, nome, nv = a; s = C.slug(nome); u = uf.lower()
    for site in [f"https://www.{s}.{u}.leg.br", f"https://{s}.{u}.leg.br", f"https://www.camara{s}.{u}.gov.br", f"https://www.cm{s}.{u}.gov.br", f"https://www.camara{s}.{u}.leg.br"]:
        try: t = requests.get(site, headers=H, timeout=10).text
        except Exception: continue
        hs = sorted(set(re.findall(r'https?://(sapl[\w.-]*\.(?:leg|gov)\.br|[\w.-]+/sapl)', t, re.I)))
        sist = [k for k in ("sapl", "siscam", "legislativo", "splegis", "sino.", "ipm", "betha", "e-legis", "atende.net", "portaltransparencia", "camaradigital", "legisla") if k in t.lower()]
        return a, site, hs, sist
    return a, None, [], []
with cf.ThreadPoolExecutor(64) as ex: R = list(ex.map(acha, alvos))
ok = [r for r in R if r[1]]; com = [r for r in ok if r[2]]
print("RES site achado", len(ok), "| com link de SAPL", len(com), flush=True)
def valida(c):
    a, site, hs, _ = c
    for h in hs:
        b = "https://" + h.rstrip("/")
        try:
            r = requests.get(f"{b}/api/materia/materialegislativa/", params={"ano": 2025, "page_size": 1}, headers=H, timeout=20)
            if r.ok and "json" in r.headers.get("content-type", ""): return (a[0], a[1], a[2], b, r.json().get("pagination", {}).get("total_entries"))
        except Exception: pass
    return (a[0], a[1], a[2], "SEMAPI " + " ".join(hs[:2]), None)
with cf.ThreadPoolExecutor(40) as ex: V = list(ex.map(valida, com))
novos = [v for v in V if not v[3].startswith("SEMAPI")]
print("RES SAPL novos com API", len(novos), flush=True)
for v in novos: print("RESN", v[1], v[3], v[4], flush=True)
print("RES sem API", [v[3][7:] for v in V if v[3].startswith("SEMAPI")][:30], flush=True)
print("RES sistemas citados nos sites sem SAPL", collections.Counter(k for r in ok if not r[2] for k in r[3]).most_common(), flush=True)
