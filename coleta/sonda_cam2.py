"""Sonda temporária: câmaras no "Câmara sem Papel" (mesmo sistema de Cuiabá), testadas pela saída do Brasil."""
import sys, re, json, concurrent.futures as cf
sys.path.insert(0, "coleta")
import camaras_sapl as C
from assembleias_sapl import H
from saida_br import get
idx = json.load(open(C.OUT / "index.json"))
alvos = []
for f in sorted((C.D / "uf").glob("*.json")):
    U = json.load(open(f))
    for ue, m in U.get("mun", {}).items():
        if ue not in idx and len(m[3] or []) >= 11: alvos.append((f.stem, ue, m[0], len(m[3])))
def testa(a):
    uf, ue, nome, nv = a; h = f"https://{C.slug(nome)}.camarasempapel.com.br"
    try:
        r = get(h + "/spl/consulta-autor.aspx", headers=H, timeout=25, tentativas=1)
        if r is not None and r.ok and "consulta-producao.aspx" in r.text:
            return (uf, ue, nome, nv, h, sum(1 for x in re.findall(r"consulta-producao\.aspx\?autor=\d+&ano=(20\d\d)", r.text) if x >= "2025"))
    except Exception: pass
with cf.ThreadPoolExecutor(12) as ex: R = [x for x in ex.map(testa, alvos) if x]
print("RES alvos", len(alvos), "achadas", len(R), flush=True)
for x in sorted(R, key=lambda x: -x[3]): print("CSP", *x, flush=True)
