"""Resumo semanal por e-mail para quem marcou a opção na página Acompanhando.
Lê a lista de envio no Supabase (função resumo_destinatarios, só com a chave de serviço) e envia pelo Resend.
Segredos (só no GitHub): SUPABASE_SERVICE_ROLE_KEY, RESEND_API_KEY. Limite do plano grátis do Resend: 100 e-mails por dia (MAX_ENVIOS).
TESTE=email@x: manda só para esse endereço, com a lista dele, sem tocar nos outros."""
import json, os, sys, time, datetime, html
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parent))
from email_resend import envia

D = Path(__file__).resolve().parents[1] / "site" / "data"; SITE = "https://fiscalizaja.com.br"
SB_URL = "https://qdkraamzxgydvhqshgql.supabase.co"; MAX = int(os.environ.get("MAX_ENVIOS", "95"))
e = lambda s: html.escape(str(s or ""))
dt = lambda d: "/".join(reversed(str(d).split("-")))
VOTO = {"S": "Sim", "N": "Não", "A": "Abstenção", "O": "Obstrução", "P": "Presidiu", "R": "Presidiu"}

def destinatarios():
    k = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    r = requests.post(f"{SB_URL}/rest/v1/rpc/resumo_destinatarios", headers={"apikey": k, "Content-Type": "application/json", **({} if k.startswith("sb_") else {"Authorization": "Bearer " + k})}, data="{}", timeout=60)
    r.raise_for_status(); return r.json()

BR = json.load(open(D / "br.json")); S = json.load(open(D / "semana.json")); VC = json.load(open(D / "camara_votacoes.json")); VS = json.load(open(D / "senado_votacoes.json"))
hoje = datetime.date.today(); ini = (hoje - datetime.timedelta(days=7)).isoformat()
semana = [w for w in S["semanas"] if w["seg"] >= (hoje - datetime.timedelta(days=13)).isoformat()]
vc = sorted({i for w in semana for i in w["c"] if VC[i][1] >= ini}); vs = sorted({i for w in semana for i in w["s"] if VS[i][1] >= ini})
CACHE = {}
def dados(casa, uf):
    k = casa + uf
    if k not in CACHE:
        try: CACHE[k] = json.load(open(D / ("c" if casa == "C" else "s") / f"{uf}.json"))
        except Exception: CACHE[k] = {}
    return CACHE[k]
dep = {str(d[0]): d for d in BR["dep"]}; sen = {str(x[0]): x for x in BR["sen"]}

def bloco(it):
    d = it.get("dados") or {}; ref = it["ref"]; t, _, rid = ref.partition("/"); nome = d.get("nome") or ref; link = f"{SITE}/p/{ref}"
    cab = f'<tr><td style="padding:18px 0 6px"><a href="{link}" style="color:#0B0B0C;font-weight:800;font-size:17px;text-decoration:none">{e(nome)}</a><br><span style="color:#5E6066;font-size:13px">{e(d.get("cargo") or "")}{" · " + e(d.get("part")) if d.get("part") else ""}</span></td></tr>'
    if t not in ("c", "s"):
        return cab + f'<tr><td style="font-size:14px;color:#5E6066">Para este cargo, o voto de cada um não é publicado em dados abertos toda semana. <a href="{link}">Ver a ficha</a></td></tr>', False
    C = t == "c"; info = dep.get(rid) if C else sen.get(rid)
    if not info: return cab + f'<tr><td style="font-size:14px;color:#5E6066">Não está mais em exercício. <a href="{link}">Ver a ficha</a></td></tr>', False
    X = dados("C" if C else "S", info[3] if C else info[4]).get(rid) or {}; v = X.get("v", ""); fp = X.get("fp", "")
    L = vc if C else vs; VL = VC if C else VS; linhas = []; votou = 0; contra = 0
    for i in L:
        x = VL[i]; c = v[i] if i < len(v) else "-"; tit = (x[5] if C else x[2]) or "Votação"; em = str((x[7] or x[6]) if C else (x[4] or x[3]) or "")[:140]
        if c in VOTO: votou += 1
        f = fp[i] if i < len(fp) else "-"; contra += f == "r"
        cor = "#14703C" if c == "S" else "#B3261E" if c == "N" else "#5E6066"
        linhas.append(f'<tr><td style="padding:6px 0;border-top:1px solid #eee;font-size:14px"><b style="color:{cor}">{VOTO.get(c, "Não registrou voto")}</b>{" · <span style=\'color:#B3261E\'>contra o partido</span>" if f == "r" else ""} — {e(tit)} ({dt(x[1])})<br><span style="color:#5E6066;font-size:13px">{e(em)}{"…" if len(em) >= 140 else ""}</span> <a href="{SITE}/votacao/{"C" if C else "S"}/{i}/{info[3] if C else info[4]}" style="font-size:13px">como votou cada um</a></td></tr>')
    novos = [p for p in (X.get("au") or {}).get("l", []) if C and len(p) > 4 and str(p[4]) >= ini and p[1] in ("PL", "PLP", "PEC", "PDL")]
    res = f"Votou em {votou} de {len(L)} votações nominais do Plenário" + (f", {contra} contra o próprio partido" if contra else "") + "." if L else "Sem votações nominais no Plenário nesta semana."
    h = cab + f'<tr><td style="font-size:14px;padding-bottom:4px">{res}</td></tr>' + "".join(linhas)
    if novos: h += '<tr><td style="padding-top:8px;font-size:14px"><b>Projetos novos</b></td></tr>' + "".join(f'<tr><td style="font-size:13px;padding:3px 0">{e(p[1])} {e(p[2])}/{e(p[3])}: {e(str(p[5])[:160])}</td></tr>' for p in novos[:5])
    return h, bool(L or novos)

def email(r):
    pols = [it for it in r["lista"] if it.get("tipo") == "p"]
    if not pols: return None
    blocos = [bloco(it) for it in pols[:20]]
    if not any(b[1] for b in blocos): return None
    sair = f"{SITE}/fiscalize#/sair/{r['token']}"
    corpo = f'''<div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;margin:0 auto;color:#0B0B0C"><h2 style="margin:0 0 4px">Fiscaliza Brasil · resumo da semana</h2>
<p style="color:#5E6066;margin:0 0 6px">Semana até {hoje.strftime("%d/%m/%Y")}: o que fizeram os políticos que você acompanha. Dados oficiais da Câmara e do Senado.</p>
<table width="100%" cellpadding="0" cellspacing="0">{"".join(b[0] for b in blocos)}</table>
<p style="margin-top:22px"><a href="{SITE}/fiscalize#/acompanho" style="background:#0B0B0C;color:#fff;padding:10px 16px;border-radius:999px;text-decoration:none;font-weight:700">Ver tudo no site</a></p>
<p style="color:#8C9097;font-size:12px;margin-top:24px">"Não registrou voto" inclui ausência, licença e falta de registro: os dados abertos não dizem o motivo.<br>Você recebe porque marcou o resumo semanal no Fiscaliza Brasil. <a href="{sair}">Parar de receber</a>.<br>Vamos fiscalizar tudo · fiscalizaja.com.br</p></div>'''
    return corpo, sair

def main():
    teste = os.environ.get("TESTE", "").strip()
    R = destinatarios(); print(len(R), "inscritos;", len(vc), "votações na Câmara e", len(vs), "no Senado desde", ini)
    if teste: R = [r for r in R if r["email"].lower() == teste.lower()]; print("teste: só", len(R))
    n = 0
    for r in R:
        if n >= MAX: print("limite de envios do dia atingido; faltaram", len(R) - n); break
        m = email(r)
        if not m: continue
        if envia(r["email"], f"Resumo da semana · {hoje.strftime('%d/%m')} · Fiscaliza Brasil", m[0], cabecalhos={"List-Unsubscribe": f"<{m[1]}>"}): n += 1
        time.sleep(0.6)
    print("enviados:", n)

if __name__ == "__main__":
    main()
