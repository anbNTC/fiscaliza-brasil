"""Sonda (temporária): consulta de remuneração dos servidores da Prefeitura de Curitiba (página ASP.NET pública, sem captcha)."""
import requests, re, html
U = "https://www.transparencia.curitiba.pr.gov.br/meta4/servidores.aspx?quadro="
S = requests.Session(); S.headers.update({"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"})
t = S.get(U, timeout=60).text
print("captcha?", bool(re.search(r"captcha|recaptcha|hcaptcha|turnstile", t, re.I)))
campos = dict(re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', t))
botoes = re.findall(r'<input[^>]+type="submit"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', t) + re.findall(r'<input[^>]+name="([^"]+)"[^>]+type="submit"[^>]*value="([^"]*)"', t)
links = re.findall(r"__doPostBack\(&#39;([^&]+)&#39;", t)
print("botões", botoes[:10]); print("postbacks", sorted(set(links))[:20])
cargos = re.findall(r'<option value="([^"]+)">', t.split("ddlCargo")[1].split("</select>")[0]) if "ddlCargo" in t else []
print("cargos", len(cargos), [c for c in cargos if re.search("COMISS|GABINETE|ASSESSOR|CHEFE|SECRET", c)][:30])
dados = {**campos, "ctl00$cphMasterPrincipal$ddlAno": "2026", "ctl00$cphMasterPrincipal$ddlMes": "10", "ctl00$cphMasterPrincipal$rblAtivoInativo": "0", "ctl00$cphMasterPrincipal$txtNome": "", "ctl00$cphMasterPrincipal$ddlCargo": ""}
for b in botoes[:1]: dados[b[0]] = b[1]
r = S.post(U, data=dados, timeout=120); t2 = r.text
print("POST", r.status_code, len(t2))
tab = re.search(r"<table[\s\S]*?</table>", t2.split("frmMasterPrincipal", 1)[-1])
if tab:
    linhas = re.findall(r"<tr[\s\S]*?</tr>", tab.group(0))
    for l in linhas[:6]: print(" | ".join(" ".join(re.sub(r"<[^>]+>", " ", html.unescape(c)).split()) for c in re.findall(r"<t[dh][^>]*>([\s\S]*?)</t[dh]>", l)))
    print("linhas", len(linhas))
for k in ("Lotação", "Lotacao", "Órgão", "Secretaria", "Remunera", "Página", "pagina"):
    i = t2.find(k); print(k, t2[max(0, i - 150): i + 250].replace("\n", " ") if i > 0 else "-")
