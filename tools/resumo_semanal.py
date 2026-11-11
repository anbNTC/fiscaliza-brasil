"""Resumo semanal por e-mail para quem marcou a opção na página Acompanhando.
Lê a lista de envio no Supabase (função resumo_destinatarios, só com a chave de serviço) e envia pelo Resend.
Segredos (só no GitHub): SUPABASE_SERVICE_ROLE_KEY, RESEND_API_KEY. Limite do plano grátis do Resend: 100 e-mails por dia (MAX_ENVIOS).
TESTE=email@x: manda só para esse endereço, com a lista dele, sem tocar nos outros.
MODO=diario: alerta do dia (quem marcou "alerta diário"): votações e projetos desde ontem; só manda se houver novidade."""
import json, os, sys, time, datetime, html, re
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
DIARIO = os.environ.get("MODO", "") == "diario"
hoje = datetime.date.today(); ini = (hoje - datetime.timedelta(days=1 if DIARIO else 7)).isoformat()
vc = [i for i, x in enumerate(VC) if x[1] >= ini]; vs = [i for i, x in enumerate(VS) if x[1] >= ini]
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
    cab = f'<tr><td style="padding:18px 0 6px"><a href="{link}" style="color:#0B0B0C;font-weight:800;font-size:17px;text-decoration:none">{e(nome)}</a><br><span style="color:#5E6066;font-size:13px">{e(re.sub(r"\(a\)", "", d.get("cargo") or ""))}{" · " + e(d.get("part")) if d.get("part") else ""}</span></td></tr>'
    if t in ("m", "e"):  # vereadores e deputados estaduais: projetos novos onde a Câmara ou a Assembleia publica em dados abertos
        partes = rid.split("/"); X = {}
        try:
            if t == "m" and len(partes) == 3: X = (json.load(open(D / "cam" / f"{partes[1]}.json")).get("dep") or {}).get(partes[2]) or {}
            elif t == "e" and len(partes) == 3:
                E = json.load(open(D / "est" / f"{partes[0]}.json"))
                if partes[1] == str(E.get("ano", "22")): X = (E.get("dep") or {}).get(partes[2]) or {}
        except Exception: X = {}
        novos = [p for p in (X.get("props") or []) if len(p) > 2 and str(p[2]) >= ini]
        if novos:
            return cab + '<tr><td style="font-size:14px;padding-bottom:4px"><b>Projetos novos</b></td></tr>' + "".join(f'<tr><td style="font-size:13px;padding:3px 0">{e(p[0])}: {e(str(p[1])[:160])}</td></tr>' for p in novos[:6]), True
        msg = "Sem projeto novo registrado nesta semana." if X.get("props") else "Esta Casa não publica a lista de projetos nem os votos de cada um em dados abertos."
        return cab + f'<tr><td style="font-size:14px;color:#5E6066">{msg} <a href="{link}">Ver a ficha</a></td></tr>', False
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
    res = f"Votou em {votou} de {len(L)} votações nominais do Plenário" + (f", {contra} contra o próprio partido" if contra else "") + "." if L else ("Sem votações nominais no Plenário desde ontem." if DIARIO else "Sem votações nominais no Plenário nesta semana.")
    h = cab + f'<tr><td style="font-size:14px;padding-bottom:4px">{res}</td></tr>' + "".join(linhas)
    if novos: h += '<tr><td style="padding-top:8px;font-size:14px"><b>Projetos novos</b></td></tr>' + "".join(f'<tr><td style="font-size:13px;padding:3px 0">{e(p[1])} {e(p[2])}/{e(p[3])}: {e(str(p[5])[:160])}</td></tr>' for p in novos[:5])
    return h, bool(L or novos)

NOT = None
def noticias():
    """Manchetes do Acontece agora (o mesmo servidor do site), para os temas que a pessoa pediu em "Avise-me quando"."""
    global NOT
    if NOT is None:
        try: NOT = requests.get(f"{SITE}/api/noticias", timeout=60, headers={"user-agent": "FiscalizaBrasil/1.0 (resumo)"}).json()
        except Exception as ex: print("notícias indisponíveis:", repr(ex)[:100]); NOT = {"itens": [], "fontes": []}
    return NOT
sa = lambda x: __import__("unicodedata").normalize("NFKD", str(x or "")).encode("ascii", "ignore").decode().lower()
def bloco_tema(it):
    N = noticias(); nomes = {f["id"]: f["nome"] for f in N.get("fontes", [])}; termo = it["ref"]; t0 = sa(termo)
    lim = (datetime.datetime.utcnow() - datetime.timedelta(days=1 if DIARIO else 3)).isoformat()
    hits = [i for i in N.get("itens", []) if i.get("d", "") >= lim and re.search(r"(^|\W)" + re.escape(t0) + r"(\W|$)", sa(i.get("t")))]
    cab = f'<tr><td style="padding:18px 0 6px"><span style="color:#0B0B0C;font-weight:800;font-size:17px">🔔 {e(termo)}</span></td></tr>'
    if not hits: return cab + '<tr><td style="font-size:14px;color:#5E6066">Nenhuma manchete sobre este tema nos veículos que acompanhamos.</td></tr>', False
    return cab + "".join(f'<tr><td style="padding:5px 0;border-top:1px solid #eee;font-size:14px"><a href="{e(i["l"])}" style="color:#0B0B0C">{e(i["t"])}</a> <span style="color:#5E6066;font-size:12px">· {e(nomes.get(i["s"], i["s"]))}</span></td></tr>' for i in hits[:6]), True

def email(r):
    pols = [it for it in r["lista"] if it.get("tipo") == "p"]; temas = [it for it in r["lista"] if it.get("tipo") == "tema"]
    if not pols and not temas: return None
    blocos = [bloco(it) for it in pols[:20]] + [bloco_tema(it) for it in temas[:10]]
    if not any(b[1] for b in blocos): return None
    sair = f"{SITE}/fiscalize#/sair/{r['token']}"
    tit = "alerta do dia" if DIARIO else "resumo da semana"; per = f"Desde {dt(ini)}" if DIARIO else f'Semana até {hoje.strftime("%d/%m/%Y")}'
    corpo = f'''<div style="font-family:Arial,Helvetica,sans-serif;max-width:600px;margin:0 auto;color:#0B0B0C"><h2 style="margin:0 0 4px">Fiscaliza Brasil · {tit}</h2>
<p style="color:#5E6066;margin:0 0 6px">{per}: o que fizeram os políticos e os temas que você acompanha. Dados oficiais.</p>
<table width="100%" cellpadding="0" cellspacing="0">{"".join(b[0] for b in blocos)}</table>
<p style="margin-top:22px"><a href="{SITE}/fiscalize#/acompanho" style="background:#0B0B0C;color:#fff;padding:10px 16px;border-radius:999px;text-decoration:none;font-weight:700">Ver tudo no site</a></p>
<p style="color:#8C9097;font-size:12px;margin-top:24px">"Não registrou voto" inclui ausência, licença e falta de registro: os dados abertos não dizem o motivo.<br>Você recebe porque marcou {"o alerta diário" if DIARIO else "o resumo semanal"} no Fiscaliza Brasil. <a href="{sair}">Parar de receber</a>.<br>Vamos fiscalizar tudo · fiscalizaja.com.br</p></div>'''
    return corpo, sair

def main():
    teste = os.environ.get("TESTE", "").strip()
    R = [r for r in destinatarios() if (r.get("diario") if DIARIO else r.get("semanal", True))]; print(len(R), "inscritos;", len(vc), "votações na Câmara e", len(vs), "no Senado desde", ini)
    if teste: R = [r for r in R if r["email"].lower() == teste.lower()]; print("teste: só", len(R))
    n = 0
    for r in R:
        if n >= MAX: print("limite de envios do dia atingido; faltaram", len(R) - n); break
        m = email(r)
        if not m: continue
        assunto = f"{'Alerta do dia' if DIARIO else 'Resumo da semana'} · {hoje.strftime('%d/%m')} · Fiscaliza Brasil"
        if envia(r["email"], assunto, m[0], cabecalhos={"List-Unsubscribe": f"<{m[1]}>"}): n += 1
        time.sleep(0.6)
    print("enviados:", n)

if __name__ == "__main__":
    main()
