"""Sonda temporária: que sistema usam as câmaras maiores ainda sem dados (pelo site da câmara)."""
import sys, re, json, requests, concurrent.futures as cf, collections
sys.path.insert(0, "coleta")
import camaras_sapl as C
from assembleias_sapl import H
idx = json.load(open(C.OUT / "index.json"))
alvos = []
for f in sorted((C.D / "uf").glob("*.json")):
    U = json.load(open(f))
    for ue, m in U.get("mun", {}).items():
        if ue not in idx and len(m[3] or []) >= 17: alvos.append((f.stem, ue, m[0], len(m[3])))
print("RES alvos (17+ vereadores, sem dados):", len(alvos), flush=True)
SIST = {"spl_aspx": r"/spl/[\w-]+\.aspx|consulta-autor\.aspx", "sapl": r"sapl", "siscam": r"siscam", "camaradigital": r"camara ?digital", "sinoweb": r"sino\.?web|sinoweb",
        "e-legis": r"e-?legis", "legisoft": r"legisoft", "betha": r"betha", "ipm": r"atende\.net|\bipm\b", "govbr_cms": r"/proposicoes|/materias", "smartlegis": r"smart ?legis",
        "plenus": r"plenus", "sgl": r"\bsgl\b", "legislaqui": r"legislaqui|leisMunicipais"}
def acha(a):
    uf, ue, nome, nv = a; s = C.slug(nome); u = uf.lower()
    for site in [f"https://www.{s}.{u}.leg.br", f"https://{s}.{u}.leg.br", f"https://www.camara{s}.{u}.gov.br", f"https://www.cm{s}.{u}.gov.br", f"https://www.camara{s}.{u}.leg.br", f"https://camara{s}.{u}.gov.br"]:
        try: r = requests.get(site, headers=H, timeout=10); t = r.text
        except Exception: continue
        if len(t) < 2000: continue
        hit = [k for k, p in SIST.items() if re.search(p, t, re.I)]
        hosts = sorted(set(re.findall(r'https?://([\w.-]+)/(?:spl|sapl|legislativo|sino|siscam)', t, re.I)))[:3]
        return a, site, hit, hosts
    return a, None, [], []
with cf.ThreadPoolExecutor(64) as ex: R = list(ex.map(acha, alvos))
print("RES site achado", sum(1 for r in R if r[1]), flush=True)
print("RES sistemas", collections.Counter(k for r in R for k in r[2]).most_common(), flush=True)
for r in sorted(R, key=lambda r: -r[0][3]):
    if r[1]: print("CAM", r[0][0], r[0][2], r[0][3], r[1], r[2], r[3], flush=True)
