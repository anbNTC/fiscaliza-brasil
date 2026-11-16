"""Sonda temporária: coleta do SAPL só de Porto Velho, Boa Vista e Manaus, para ver o que falha."""
import sys, json, time, concurrent.futures as cf
sys.path.insert(0, "coleta")
from assembleias_sapl import SAPL, coleta_sapl
D = "site/data/uf/"
def um(a):
    uf, ue, base = a; t0 = time.time()
    U = json.load(open(D + uf + ".json")); A = SAPL(base=base, lim_min=45)
    try: r = coleta_sapl(A, U["mun"][ue][3], "2025-01-01", range(2025, 2027))
    except Exception as e: return a, {"exc": repr(e)[:300]}, time.time() - t0
    return a, ({"erro": r["erro"]} if "erro" in r else {"parl": len(r["parl"]), "sem": len(r["sem"]), "mats": len(r["mats"]), "vp": len(r["vp"]), "dep": len(r["dep"]), "leg": str(r["leg"].get("__str__"))}), time.time() - t0
with cf.ThreadPoolExecutor(3) as ex:
    for a, r, dt in ex.map(um, [("RO", "00035", "https://sapl.portovelho.ro.leg.br"), ("RR", "03018", "https://sapl.boavista.rr.leg.br"), ("AM", "02550", "https://sapl.cmm.am.gov.br")]):
        print("CAP", a[0], a[1], round(dt / 60, 1), "min", json.dumps(r, ensure_ascii=False), flush=True)
