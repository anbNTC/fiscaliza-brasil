"""Sonda (temporária): liga o salário pago (CSV mensal) ao funcionário (ponto) e olha o Senado."""
import requests, re, io, csv, collections, json
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0", "accept": "application/json"}
g = lambda u: requests.get(u, timeout=240, headers=H)
r = g("https://www2.camara.leg.br/transparencia/recursos-humanos/remuneracao/relatorios-consolidados-por-ano-e-mes/2026/outubro-de-2026-csv")
t = r.content.decode("utf-8") if b"\xc3\xa1" in r.content[:200000] else r.content.decode("latin-1")
rows = [x for x in csv.reader(io.StringIO(t), delimiter=";") if len(x) > 14]
R = collections.defaultdict(list)
for x in rows[1:]:
    m = re.search(r"(\d+)\s*$", x[0])
    if m: R[m.group(1)].append(x)
r = g("https://dadosabertos.camara.leg.br/arquivos/funcionarios/csv/funcionarios.csv")
F = list(csv.DictReader(io.StringIO(r.content.decode("utf-8-sig")), delimiter=";"))
sp = [f for f in F if (f.get("grupo") or "").startswith("Secret")]
hit = [f for f in sp if f["ponto"].strip() in R]
print("SP no cadastro:", len(sp), "com ponto no CSV de salário:", len(hit))
for f in hit[:5]: print(f["ponto"], f["cargo"], f["nome"][:3] + "...", [x[:3] + x[6:7] + x[14:15] for x in R[f["ponto"].strip()]])
cne = [f for f in F if (f.get("grupo") or "").startswith("Cargo de Natureza")]; print("CNE:", len(cne), "ligados:", sum(1 for f in cne if f["ponto"].strip() in R))
print("pontos exemplo cadastro:", [f["ponto"] for f in sp[:5]], "ids exemplo salário:", list(R)[:5])
# nível x valor pago (função) para validar C/S/U
v = collections.defaultdict(collections.Counter)
for f in hit:
    for x in R[f["ponto"].strip()]:
        if x[2] == "Normal": v[f["cargo"]][x[6]] += 1
for k in ("SP01S", "SP01C", "SP02S", "SP12S", "SP12C", "SP12U", "SP25S", "SP25C", "SP25U", "CNE09"):
    print(k, v[k].most_common(4))
for u in ("https://adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/remuneracoes/2026/9", "https://adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/servidores/ativos", "https://adm.senado.gov.br/adm-dadosabertos/api/v1/servidores/comissionados"):
    try:
        r = g(u); print("==", u, r.status_code, r.headers.get("content-type"), len(r.content))
        j = r.json(); L = j if isinstance(j, list) else next((v for v in j.values() if isinstance(v, list)), [j])
        print(len(L), json.dumps(L[:2], ensure_ascii=False)[:1500])
        if L and isinstance(L[0], dict):
            for k in L[0]:
                if re.search("lota|setor|unidade|vinculo|cargo|categoria", k, re.I): print(" ", k, collections.Counter(str(x.get(k))[:60] for x in L).most_common(6))
    except Exception as e: print(u, repr(e)[:200])
