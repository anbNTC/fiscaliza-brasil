"""Sonda temporária: Instagram de cada vereador de Curitiba.
1) site da Câmara (campo instagram do perfil); 2) redes sociais declaradas ao TSE em 2024 (dados abertos: rede_social_candidato_2024)."""
import re, sys, io, csv, time, zipfile, unicodedata
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
    VER.append({"nome": j.get("title"), "cmc": j.get("instagram") or ""})
    time.sleep(0.2)

C = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand"
def zcsv(url, filtro):
    z = zipfile.ZipFile(io.BytesIO(requests.get(url, timeout=600).content))
    nomes = [n for n in z.namelist() if filtro in n and n.endswith(".csv")]
    print("ZIP", url.rsplit("/", 1)[1], nomes[:3], flush=True)
    return list(csv.DictReader(io.StringIO(z.read(nomes[0]).decode("latin-1")), delimiter=";"))
cand = [c for c in zcsv(f"{C}/consulta_cand_2024.zip", "_PR") if c.get("SG_UE") == "75353" and c.get("CD_CARGO") == "13"]
print("CAND", len(cand), flush=True)
redes = {}
for x in zcsv(f"{C}/rede_social_candidato_2024.zip", "_PR"):
    redes.setdefault(x.get("SQ_CANDIDATO"), []).append(x.get("DS_URL"))
for v in VER:
    a = sa(v["nome"])
    c = [c for c in cand if sa(c["NM_URNA_CANDIDATO"]) == a] or [c for c in cand if a in sa(c["NM_URNA_CANDIDATO"]) or sa(c["NM_URNA_CANDIDATO"]) in a]
    for k in c[:2]:
        ig = [u for u in redes.get(k["SQ_CANDIDATO"], []) if "instagram" in (u or "").lower()]
        print("VER", v["nome"], "|", k["NM_URNA_CANDIDATO"], "|", k.get("DS_SIT_TOT_TURNO"), "| CMC:", v["cmc"], "| IG:", ig, flush=True)
    if not c: print("VER", v["nome"], "| sem candidatura achada | CMC:", v["cmc"], flush=True)
