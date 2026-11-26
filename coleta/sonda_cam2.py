"""Sonda temporária: câmaras no sistema "Câmara sem Papel" (/spl/consulta-autor.aspx), o mesmo de Cuiabá."""
import sys, re, json, requests, concurrent.futures as cf
sys.path.insert(0, "coleta")
import camaras_sapl as C
from assembleias_sapl import H
idx = json.load(open(C.OUT / "index.json"))
alvos = []
for f in sorted((C.D / "uf").glob("*.json")):
    U = json.load(open(f))
    for ue, m in U.get("mun", {}).items():
        if ue not in idx and len(m[3] or []) >= 11: alvos.append((f.stem, ue, m[0], len(m[3])))
print("RES alvos", len(alvos), flush=True)
def testa(a):
    uf, ue, nome, nv = a; s = C.slug(nome)
    for h in [f"https://{s}.camarasempapel.com.br", f"https://{s}.nopapercloud.com.br", f"https://camarasempapel.camara{s}.{uf.lower()}.gov.br", f"https://{s}{uf.lower()}.camarasempapel.com.br"]:
        try:
            r = requests.get(h + "/spl/consulta-autor.aspx", headers=H, timeout=12)
            if r.ok and "consulta-producao.aspx" in r.text:
                anos = re.findall(r"consulta-producao\.aspx\?autor=\d+&ano=(20\d\d)", r.text)
                return (uf, ue, nome, nv, h, sum(1 for x in anos if x >= "2025"))
        except Exception: pass
    return None
with cf.ThreadPoolExecutor(64) as ex: R = [x for x in ex.map(testa, alvos) if x]
print("RES achadas", len(R), flush=True)
for x in sorted(R, key=lambda x: -x[3]): print("CSP", *x, flush=True)
