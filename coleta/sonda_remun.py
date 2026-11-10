"""Sonda (temporária): tabela de níveis SP x salários pagos x códigos do cadastro de funcionários; Senado."""
import requests, re, io, csv, subprocess, collections, json
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}
g = lambda u, **k: requests.get(u, timeout=180, headers=H, **k)
B = "https://www2.camara.leg.br/a-camara/estruturaadm/diretorias/diretoria-de-gestao-pessoas/estrutura-1/depes/secretariado-parlamentar/posse-de-sp-sem-vinculo/"
for nm in ("TABSP202601MAR202620260303.pdf",):
    r = g(B + nm); print("PDF", r.status_code, r.headers.get("content-type"), len(r.content))
    if r.ok and r.content[:4] == b"%PDF":
        open("/tmp/t.pdf", "wb").write(r.content); print(subprocess.run(["pdftotext", "-layout", "/tmp/t.pdf", "-"], capture_output=True, text=True).stdout[:6000])
r = g("https://www2.camara.leg.br/transparencia/recursos-humanos/remuneracao/relatorios-consolidados-por-ano-e-mes/2026/outubro-de-2026-csv")
t = r.content.decode("latin-1") if b"\xc3" not in r.content[:20000] else r.content.decode("utf-8")
rows = list(csv.reader(io.StringIO(t), delimiter=";")); h = rows[0]
c = collections.Counter(x[6] for x in rows[1:] if x[1] == "Secretário Parlamentar" and x[2] == "Normal")
print("FUNCAO SP (valor: n):", sorted(c.items(), key=lambda z: float(z[0].replace(",", ".")))[:80])
print("GRUPOS:", collections.Counter(x[1] for x in rows[1:]).most_common(20))
r = g("https://dadosabertos.camara.leg.br/arquivos/funcionarios/csv/funcionarios.csv")
F = list(csv.DictReader(io.StringIO(r.content.decode("utf-8-sig")), delimiter=";")); print("CAMPOS", list(F[0].keys()))
cc = collections.Counter((x.get("cargo") or "") for x in F if (x.get("grupo") or "").startswith("Secret")); print("CODIGOS SP:", sorted(cc.items()))
cn = collections.Counter((x.get("cargo") or "") for x in F if "CNE" in (x.get("cargo") or "")); print("CNE:", cn.most_common(20))
print("GRUPOS F:", collections.Counter(x.get("grupo") for x in F).most_common(10))
for u in ("https://www.senado.leg.br/transparencia/lai/secrh/servidores_comissionados.csv", "https://adm.senado.gov.br/adm-dadosabertos/v3/api-docs", "https://adm.senado.gov.br/adm-dadosabertos/swagger-config.json"):
    try: r = g(u); print("==", u, r.status_code, r.headers.get("content-type"), len(r.content)); tx = r.content.decode("utf-8", "ignore"); print(tx[:1500] if "csv" in u else "\n".join(sorted(set(re.findall(r'"(/api/v1/[^"]*remunera[^"]*)"', tx)))) or tx[:800])
    except Exception as e: print(u, e)
