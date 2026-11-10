"""Prefeitura de Curitiba: quem trabalha no gabinete do prefeito e do vice, com remuneração bruta e líquida.
Fonte: Portal da Transparência da Prefeitura (www.transparencia.curitiba.pr.gov.br/meta4/servidores.aspx), consulta pública sem captcha.
A consulta lista nome, cargo, lotação e remuneração de cada servidor, 10 por página. Para não pesar no site da Prefeitura,
lemos só os cargos em comissão e as funções gratificadas (onde ficam as equipes de gabinete) e guardamos quem está lotado
no gabinete do prefeito ou do vice. Saída: junta em site/data/gabm/75353.json (chaves "p" e "v")."""
import re, html, json, time, datetime, sys
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gabinetes_elotech import grava

U = "https://www.transparencia.curitiba.pr.gov.br/meta4/servidores.aspx?quadro="
S = requests.Session(); S.headers.update({"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"})
HOJE = datetime.date.today()
P = "ctl00$cphMasterPrincipal$"
GABP = re.compile(r"GABINETE\s+DO\s+PREFEITO|GAB\.?\s*PREFEITO|VICE[\s-]*PREFEIT", re.I)
num = lambda s: float(re.sub(r"[^\d,]", "", s).replace(",", ".") or 0)

def ocultos(t): return dict(re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', t))

def linhas(t):
    tab = re.search(r'id="cphMasterPrincipal_gdvPesquisaServidores"[\s\S]*?</table>', t)
    if not tab: return []
    out = []
    for tr in re.findall(r"<tr[\s\S]*?</tr>", tab.group(0)):
        c = [" ".join(re.sub(r"<[^>]+>", " ", html.unescape(x)).split()) for x in re.findall(r"<td[^>]*>([\s\S]*?)</td>", tr)]
        if len(c) >= 5 and c[0] and "R$" in c[3]: out.append(c[:5])
    return out

def post(t, extra, ano, mes, cargo):
    d = ocultos(t); d.update({P + "ddlAno": str(ano), P + "ddlMes": str(mes), P + "rblAtivoInativo": "0", P + "txtNome": "", P + "ddlCargo": cargo}); d.update(extra)
    for k in range(4):
        try:
            r = S.post(U, data=d, timeout=120)
            if r.ok: return r.text
        except Exception as e: print("post", repr(e)[:100], flush=True)
        time.sleep(5 * (k + 1))
    raise RuntimeError("Prefeitura de Curitiba não respondeu")

def main():
    t = S.get(U, timeout=90).text
    if re.search(r"captcha", t, re.I): raise RuntimeError("a consulta passou a pedir captcha: não coletamos")
    ano = re.search(r'ddlAno"[^>]*>\s*<option selected="selected" value="(\d+)"', t); mes = re.search(r'ddlMes"[^>]*>\s*<option selected="selected" value="(\d+)"', t)
    ano, mes = (ano.group(1) if ano else HOJE.year), (mes.group(1) if mes else HOJE.month)
    cargos = re.findall(r'<option value="([^"]+)">', t.split('id="cphMasterPrincipal_ddlCargo"', 1)[-1].split("</select>", 1)[0])
    alvo = [c for c in cargos if re.search(r"COMISS|GRATIFICAD|ASSESSOR|CHEFE DE GABINETE|SECRETARIO", c, re.I)] or ["CARGO EM COMISSÃO"]
    print("competência", mes, "/", ano, "· cargos lidos:", alvo, flush=True)
    gab = {"p": [], "v": []}; lidos = 0
    for cg in alvo:
        t2 = post(t, {"__EVENTTARGET": P + "ddlCargo", "__EVENTARGUMENT": ""}, ano, mes, cg)
        pg = 1
        while True:
            L = linhas(t2); lidos += len(L)
            for nome, cargo, lot, bruto, liq in L:
                if GABP.search(lot):
                    gab["v" if re.search("VICE", lot, re.I) else "p"].append([nome.title(), (cargo + " · " + lot.title()).capitalize(), "", round(num(bruto), 2), round(num(liq), 2)])
            if f"Page${pg + 1}" not in t2 or pg > 600: break
            pg += 1; time.sleep(0.6)
            t2 = post(t2, {"__EVENTTARGET": P + "gdvPesquisaServidores", "__EVENTARGUMENT": f"Page${pg}"}, ano, mes, cg)
        print(cg, "páginas:", pg, flush=True)
    for v in gab.values(): v.sort(key=lambda r: -r[3])
    gab = {k: v for k, v in gab.items() if v}
    print("servidores lidos:", lidos, "· no gabinete:", {k: len(v) for k, v in gab.items()})
    if gab:
        grava("75353", {"_tipo": "pref", "dep": gab, "fonte": "Portal da Transparência da Prefeitura de Curitiba · remuneração dos servidores",
                        "url": "https://www.transparencia.curitiba.pr.gov.br/meta4/servidores.aspx?quadro=", "competencia": f"{int(mes):02d}/{ano}",
                        "obs": f"Remuneração bruta e líquida de {int(mes):02d}/{ano}, como publicada pela Prefeitura. Só cargos em comissão e funções gratificadas lotados no gabinete do prefeito ou do vice."})

if __name__ == "__main__":
    main()
