"""Sonda temporária: busca de proposições na CMBH (POST do formulário) e relatório de produtividade de Salvador."""
import re, sys, html, requests
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
U = "https://www.cmbh.mg.gov.br/atividade-legislativa/pesquisar-proposicoes"
S = requests.Session(); S.headers.update(H)
try:
    t = S.get(U, timeout=60).text; via = "direto"
except Exception: t = get(U, headers=H, timeout=60).text; via = "br"
i = t.find("form_pesquisa_proposicoes"); js = [m for m in re.findall(r"<script[^>]*>([\s\S]*?)</script>", t) if "metodo" in m or "paginaRequerida" in m]
print("BHJS", via, [re.sub(r"\s+", " ", m)[:1800] for m in js][:2], flush=True)
f = {k: v for k, v in re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', t[i:i + 20000])}
print("BHHID", {k: v[:12] for k, v in f.items()}, flush=True)
f.update({"tipo": "2c907f7801d41f2001024943e5ec004a", "ano": "2025", "numero": "", "autor": "", "assunto": "", "assunto2": "", "fase": "[Selecione]", "tramitando": "", "metodo": "pesquisar", "paginaRequerida": "1"})
try:
    r = S.post(U, data=f, timeout=90, headers={"referer": U}); t2 = r.text
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t2))
    j = txt.find("PL "); print("BHPOST", r.status_code, len(t2), txt[max(0, j - 300):j + 1500], flush=True)
    print("BHLINKS", sorted(set(re.findall(r'href="([^"]*(?:proposic|detalhe)[^"]*)"', t2)))[:15], flush=True)
except Exception as e: print("BHPOST falhou", repr(e)[:200], flush=True)
for u in ["https://cmsalvador.sys.inf.br/leg/LEG_SYS_produtividade_parlamentar_proposicao/", "http://45.4.247.157/leg/salvador/LEG_SYS_produtividade_parlamentar_proposicao/"]:
    try:
        r = requests.get(u, headers=H, timeout=40); tt = r.text
        print("SSA", u, r.status_code, len(tt), "| antirrobô" if re.search(r"captcha|recaptcha", tt, re.I) else "", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", tt))[:1500], flush=True)
    except Exception as e: print("SSA", u, "falhou", repr(e)[:150], flush=True)
