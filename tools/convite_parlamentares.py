"""Convite para parlamentares divulgarem o Fiscaliza Brasil (e-mail personalizado, um por pessoa).
Grupos: vereadores de Curitiba (CMC), deputados estaduais do Paraná (ALEP) e deputados federais do Paraná (Câmara).
Os e-mails dos gabinetes vêm das páginas oficiais de cada casa. Respostas vão para o e-mail do segredo ALERTA_EMAIL (reply-to).
MODO=lista  → só monta a lista e mostra quem tem e-mail (não envia nada; não imprime os endereços)
MODO=teste  → envia 1 exemplo de cada grupo para o ALERTA_EMAIL
MODO=envia  → envia de verdade, até LIMITE por execução (plano grátis do Resend: 100/dia), sem repetir quem já recebeu
Registro de quem já recebeu: tools/convite_enviados.json (só a chave do parlamentar e a data)."""
import os, re, sys, json, time, html, datetime, unicodedata
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "coleta"))
import saida_br
from email_resend import REMETENTE

UA = {"user-agent": "Mozilla/5.0 (FiscalizaBrasil/1.0; +https://fiscalizaja.com.br)"}
REG = Path(__file__).resolve().parent / "convite_enviados.json"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
SITE = "https://fiscalizaja.com.br/fiscalize"
UF = json.load(open(Path(__file__).resolve().parents[1] / "site" / "data" / "uf" / "PR.json"))
FEM = {"xsargento-tania-guerreiro"}
MASC = {"malexandre-leprevost", "mluciano-carvalho", "edr-leonidas", "ejairo-tamura", "epedro-paulo-bazana"}   # suplentes sem gênero na base do TSE usada aqui
NOMES = {"emarcia-huculak": "Márcia Huculak"}
slug = lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

def federais():
    out = []
    j = requests.get("https://dadosabertos.camara.leg.br/api/v2/deputados?siglaUf=PR&itens=100", headers={**UA, "accept": "application/json"}, timeout=60).json()
    for d in j["dados"]:
        time.sleep(0.4)
        x = requests.get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{d['id']}", headers={**UA, "accept": "application/json"}, timeout=60).json()["dados"]
        st = x.get("ultimoStatus") or {}; em = (st.get("gabinete") or {}).get("email") or st.get("email") or ""
        out.append({"k": f"c{d['id']}", "nome": st.get("nomeEleitoral") or d["nome"], "sexo": x.get("sexo") or "", "cargo": "Deputado(a) Federal",
                    "email": em, "link": f"{SITE}#/p/c/{d['id']}"})
    return out

def estaduais():
    S = requests.Session(); S.headers.update(UA)
    E = json.load(open(Path(__file__).resolve().parents[1] / "site" / "data" / "est" / "PR.json")); ano = str(E.get("ano") or "22")[-2:]
    chave = {v.get("sapl", "").rstrip("/").split("/")[-1]: k for k, v in E["dep"].items()}
    t = S.get("https://www.assembleia.pr.leg.br/deputados/conheca", timeout=60).text
    out, vis = [], set()
    for sl in re.findall(r'href="https://www\.assembleia\.pr\.leg\.br/deputados/perfil/([a-z0-9-]+)"', t):
        if sl in vis or sl not in chave: continue
        vis.add(sl); time.sleep(0.5)
        p = S.get(f"https://www.assembleia.pr.leg.br/deputados/perfil/{sl}", timeout=60).text
        nome = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", p); nome = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(nome.group(1))).split()) if nome else sl
        nome = re.sub(r"^(PRESIDENTE|\d+º\s+(SECRETÁRI[OA]|VICE-PRESIDENTE)|DEPUTAD[OA])\s+", "", nome, flags=re.I).title()
        ems = [e for e in dict.fromkeys(EMAIL.findall(html.unescape(p))) if "assembleia.pr.leg.br" in e or "alep" in e]
        k = chave[sl]; nome = E["dep"][k].get("nome") or nome
        try: sx = UF["de" + ano][int(k)][4]
        except Exception: sx = ""
        out.append({"k": f"e{sl}", "nome": nome, "sexo": sx, "cargo": "Deputado(a) Estadual",
                    "email": ems[0] if ems else "", "link": f"{SITE}#/p/e/PR/{ano}/{chave[sl]}"})
    return out

def sexo_ver(k):
    if k in FEM: return "F"
    try: return UF["mun"]["75353"][3][int(k)][4]
    except Exception: return ""

def vereadores():
    out = []
    t = saida_br.get("https://www.cmc.pr.gov.br/vereadores/conheca-os-vereadores", headers={**UA, "accept": "text/html"}, timeout=90).text
    X = json.load(open(Path(__file__).resolve().parents[1] / "site" / "data" / "cam" / "75353.json"))["dep"]
    chave = {v.get("sapl", "").rstrip("/").split("/")[-1]: k for k, v in X.items()}
    for sl in dict.fromkeys(re.findall(r'/vereadores/([a-z0-9-]+)"', t)):
        if sl not in chave: continue
        time.sleep(0.4)
        r = saida_br.get(f"https://www.cmc.pr.gov.br/++api++/vereadores/{sl}", headers={**UA, "accept": "application/json"}, timeout=90)
        j = r.json() if r is not None and r.ok else {}
        if j.get("ex_vereador"): continue
        ems = [e for e in dict.fromkeys(EMAIL.findall(json.dumps(j, ensure_ascii=False))) if "cmc.pr.gov.br" in e]
        out.append({"k": f"m{sl}", "nome": j.get("title") or X[chave[sl]]["nome"], "sexo": sexo_ver(chave[sl]),
                    "cargo": "Vereador(a)", "email": ems[0] if ems else "", "link": f"{SITE}#/p/m/PR/75353/{chave[sl]}"})
    return out

def tratamento(p):
    if p["k"] in MASC: p["sexo"] = "M"
    p["nome"] = NOMES.get(p["k"], p["nome"])
    f = p["sexo"] == "F"
    if p["sexo"] not in ("F", "M"): return "Excelentíssimo(a) Senhor(a) " + p["cargo"] + " " + p["nome"], None
    c = {"Deputado(a) Federal": ("Deputada Federal" if f else "Deputado Federal"), "Deputado(a) Estadual": ("Deputada Estadual" if f else "Deputado Estadual"),
         "Vereador(a)": ("Vereadora" if f else "Vereador")}.get(p["cargo"], p["cargo"])
    return ("Excelentíssima Senhora " if f else "Excelentíssimo Senhor ") + c + " " + p["nome"], f

def texto(p):
    saud, f = tratamento(p); sr = "a senhora" if f else "o(a) senhor(a)" if f is None else "o senhor"
    return f"""{saud},

Meu nome é Abraão Nery. Estudo política há 12 anos e criei o Fiscaliza Brasil (fiscalizaja.com.br), uma plataforma gratuita e apartidária que reúne em um só lugar o trabalho dos nossos representantes, a partir de dados oficiais e abertos.

Gravei um vídeo curto explicando como funciona:
https://www.instagram.com/p/DfmgSBVuX7m/

No portal, qualquer cidadão encontra, de forma simples:
- os projetos apresentados por cada parlamentar;
- como cada um votou no Plenário, com a orientação do partido e do governo;
- as emendas enviadas a cada município e quanto já foi pago;
- os gastos de gabinete e da cota parlamentar;
- os dados do TSE: votos, bens declarados e contas de campanha.

Basta digitar o nome de um político, a cidade ou o CEP. Todas as informações vêm das fontes oficiais (Câmara, Senado, Assembleias, Câmaras Municipais, Portal da Transparência e TSE), e cada página mostra a fonte e a data dos dados.

A sua página no portal está aqui:
{p['link']}

O objetivo é aproximar o cidadão do trabalho legislativo e mostrar, com dados, o que cada mandato tem feito. Por isso, gostaria de pedir o seu apoio para divulgar a plataforma nas suas redes e entre os seus eleitores. Também convido {sr} e a sua equipe a conferir a sua página. Se encontrarem qualquer informação incompleta ou incorreta, terei prazer em corrigir.

Observação: vamos criar uma página dedicada a todos os parlamentares que divulgarem o portal, com nome, foto, cargo e redes sociais, como reconhecimento pelo apoio à transparência.

Agradeço pela atenção e fico à disposição.

Atenciosamente,

Abraão Nery
Fundador do Fiscaliza Brasil
fiscalizaja.com.br
Instagram: @oabraaonery"""

def visual(p):
    """Versão em HTML com a identidade do Fiscaliza Brasil: fundo claro, texto preto, faixa verde-amarelo-azul, cartões arredondados e botões pretos.
    Só tabelas e estilos inline (é o que os programas de e-mail aceitam)."""
    saud, f = tratamento(p); sr = "a senhora" if f else "o(a) senhor(a)" if f is None else "o senhor"; E = html.escape
    F = "'Familjen Grotesk','Helvetica Neue',Arial,sans-serif"; T = "'Source Sans 3','Helvetica Neue',Arial,sans-serif"; MONO = "'JetBrains Mono',Menlo,Consolas,monospace"
    item = lambda ic, tx: f'<tr><td width="34" valign="top" style="padding:7px 0;font-size:18px">{ic}</td><td style="padding:7px 0;font:16px/1.45 {T};color:#0B0B0C">{tx}</td></tr>'
    btn = lambda url, tx, preto=True: f'<a href="{url}" style="display:inline-block;background:{"#0B0B0C" if preto else "#ffffff"};color:{"#ffffff" if preto else "#0B0B0C"};border:2px solid #0B0B0C;border-radius:999px;padding:12px 22px;font:700 15px {F};text-decoration:none">{tx}</a>'
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light">
<link href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background:#F3F2EC">
<div style="display:none;max-height:0;overflow:hidden">Uma plataforma gratuita e apartidária com o trabalho de cada parlamentar, a partir de dados oficiais. A sua página já está no ar.</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F3F2EC"><tr><td align="center" style="padding:28px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px">
 <tr><td style="padding:0 6px 16px"><table role="presentation" cellpadding="0" cellspacing="0"><tr>
   <td><img src="https://fiscalizaja.com.br/icon-192.png" width="44" height="44" alt="" style="display:block;border-radius:12px"></td>
   <td style="padding-left:12px;font:800 20px {F};letter-spacing:.02em;color:#0B0B0C">FISCALIZA BRASIL</td></tr></table></td></tr>
 <tr><td style="background:#FFFFFF;border-radius:28px;border:1px solid rgba(11,11,12,.08);padding:34px 32px 30px">
   <div style="font:600 12px {MONO};letter-spacing:.14em;text-transform:uppercase;color:#5E6066">Vamos fiscalizar tudo</div>
   <h1 style="margin:10px 0 14px;font:700 30px/1.15 {F};color:#0B0B0C">Transparência sobre o trabalho de cada parlamentar, num lugar só</h1>
   <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 22px"><tr><td width="44" height="8" style="background:#0E8A4B;font-size:0">&nbsp;</td><td width="44" height="8" style="background:#F7C21B;font-size:0">&nbsp;</td><td width="44" height="8" style="background:#1F4FBF;font-size:0">&nbsp;</td></tr></table>
   <p style="margin:0 0 14px;font:600 17px/1.5 {T};color:#0B0B0C">{E(saud)},</p>
   <p style="margin:0 0 14px;font:16px/1.6 {T};color:#26272B">Meu nome é Abraão Nery. Estudo política há 12 anos e criei o <b>Fiscaliza Brasil</b> (<a href="https://fiscalizaja.com.br" style="color:#0B0B0C">fiscalizaja.com.br</a>), uma plataforma gratuita e apartidária que reúne em um só lugar o trabalho dos nossos representantes, a partir de dados oficiais e abertos.</p>
   <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:18px 0;background:#0B0B0C;border-radius:20px"><tr><td style="padding:20px 22px">
     <div style="font:600 11px {MONO};letter-spacing:.14em;text-transform:uppercase;color:#F7C21B">Vídeo · 1 minuto</div>
     <div style="margin:6px 0 14px;font:700 19px/1.3 {F};color:#FFFFFF">Veja como a plataforma funciona</div>
     {btn("https://www.instagram.com/p/DfmgSBVuX7m/", "▶ Assistir no Instagram", False)}</td></tr></table>
   <p style="margin:6px 0 4px;font:700 18px {F};color:#0B0B0C">No portal, qualquer cidadão encontra:</p>
   <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
     {item("📄", "os projetos apresentados por cada parlamentar;")}
     {item("🗳️", "como cada um votou no Plenário, com a orientação do partido e do governo;")}
     {item("📍", "as emendas enviadas a cada município e quanto já foi pago;")}
     {item("🧾", "os gastos de gabinete e da cota parlamentar;")}
     {item("📊", "os dados do TSE: votos, bens declarados e contas de campanha.")}</table>
   <p style="margin:14px 0;font:16px/1.6 {T};color:#26272B">Basta digitar o nome de um político, a cidade ou o CEP. Tudo vem das fontes oficiais (Câmara, Senado, Assembleias, Câmaras Municipais, Portal da Transparência e TSE), e cada página mostra a fonte e a data dos dados.</p>
   <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;background:#F6F7F4;border:1px solid rgba(11,11,12,.08);border-radius:20px"><tr><td style="padding:20px 22px">
     <div style="font:600 11px {MONO};letter-spacing:.14em;text-transform:uppercase;color:#5E6066">A sua página</div>
     <div style="margin:6px 0 14px;font:700 19px/1.3 {F};color:#0B0B0C">{E(p["nome"])}</div>
     {btn(p["link"], "Ver a minha página no Fiscaliza")}</td></tr></table>
   <p style="margin:0 0 14px;font:16px/1.6 {T};color:#26272B">O objetivo é aproximar o cidadão do trabalho legislativo e mostrar, com dados, o que cada mandato tem feito. Por isso, gostaria de pedir o seu apoio para <b>divulgar a plataforma</b> nas suas redes e entre os seus eleitores. Também convido {sr} e a sua equipe a conferir a sua página. Se encontrarem qualquer informação incompleta ou incorreta, terei prazer em corrigir.</p>
   <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;border-radius:20px;background:#FFF8DC;border:1px solid #F7C21B"><tr><td style="padding:18px 22px;font:16px/1.55 {T};color:#0B0B0C">
     <b style="font-family:{F}">⭐ Reconhecimento</b><br>Vamos criar uma página dedicada a todos os parlamentares que divulgarem o portal, com nome, foto, cargo e redes sociais, como reconhecimento pelo apoio à transparência.</td></tr></table>
   <p style="margin:0 0 22px;font:16px/1.6 {T};color:#26272B">Agradeço pela atenção e fico à disposição.</p>
   <p style="margin:0;font:16px/1.5 {T};color:#26272B">Atenciosamente,</p>
   <p style="margin:4px 0 0;font:700 18px {F};color:#0B0B0C">Abraão Nery</p>
   <p style="margin:2px 0 0;font:15px/1.5 {T};color:#5E6066">Fundador do Fiscaliza Brasil · <a href="https://fiscalizaja.com.br" style="color:#0B0B0C">fiscalizaja.com.br</a> · <a href="https://www.instagram.com/oabraaonery/" style="color:#0B0B0C">@oabraaonery</a></p>
 </td></tr>
 <tr><td align="center" style="padding:20px 10px 0;font:600 12px {MONO};letter-spacing:.06em;color:#8C9097">SIGA: @oabraaonery · VAMOS FISCALIZAR TUDO</td></tr>
</table></td></tr></table></body></html>"""

def envia(para, p, resposta):
    t = texto(p)
    corpo_html = visual(p)
    body = {"from": REMETENTE.replace("nao-responda@", "contato@").replace("Fiscaliza Brasil <", "Abraão Nery · Fiscaliza Brasil <"), "to": [para],
            "subject": "Fiscaliza Brasil: plataforma gratuita de transparência sobre o trabalho dos parlamentares", "text": t, "html": corpo_html}
    if resposta: body["reply_to"] = resposta
    r = requests.post("https://api.resend.com/emails", headers={"Authorization": "Bearer " + os.environ["RESEND_API_KEY"], "Content-Type": "application/json"}, data=json.dumps(body), timeout=30)
    if r.status_code >= 300: print("  Resend", r.status_code, r.text[:200]); return False
    return True

def main():
    modo = os.environ.get("MODO", "lista"); grupos = os.environ.get("GRUPOS", "m e c").split(); lim = int(os.environ.get("LIMITE", "95"))
    resp = os.environ.get("RESPOSTA", "")
    L = []
    for g, f in (("m", vereadores), ("e", estaduais), ("c", federais)):
        if g not in grupos: continue
        try: x = f(); L += x; print(f"{g}: {len(x)} pessoas, {sum(1 for p in x if p['email'])} com e-mail", flush=True)
        except Exception as e: print(g, "falhou:", repr(e)[:200], flush=True)
    feitos = json.load(open(REG)) if REG.exists() else {}
    for p in L:
        dom = p["email"].split("@")[-1] if p["email"] else "SEM E-MAIL"
        print(f"  {p['k']:<40} {tratamento(p)[0][:70]:<70} {dom} {'(já enviado ' + feitos[p['k']] + ')' if p['k'] in feitos else ''}")
    if modo == "lista":
        if L: print("\n--- exemplo do texto ---\n" + texto(L[0]))
        return
    if modo == "previa":   # grava o HTML de um exemplo (para ver como fica)
        open(os.environ.get("SAIDA", "convite_previa.html"), "w").write(visual(L[0])); return
    if modo == "teste":
        vistos = set()
        for p in L:
            g = p["k"][0]
            if g in vistos or not p["email"]: continue
            vistos.add(g); print("teste", p["k"], "→ ALERTA_EMAIL:", envia(resp, p, resp))
        return
    n = 0
    for p in L:
        if n >= lim: print("limite desta execução atingido; o resto vai na próxima"); break
        if not p["email"] or p["k"] in feitos: continue
        if envia(p["email"], p, resp): feitos[p["k"]] = datetime.date.today().isoformat(); n += 1; print("enviado", p["k"])
        time.sleep(0.7)
    json.dump(feitos, open(REG, "w"), ensure_ascii=False, indent=0)
    print(json.dumps({"enviados_agora": n, "total_ja_enviados": len(feitos), "faltam": sum(1 for p in L if p["email"] and p["k"] not in feitos)}))

if __name__ == "__main__":
    main()
