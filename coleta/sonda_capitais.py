"""Sonda temporária: pesquisar.php da CMBH e conteúdo da grade de produtividade de Salvador."""
import re, sys, html, requests
sys.path.insert(0, "coleta")
from assembleias_sapl import H
U = "https://www.cmbh.mg.gov.br/atividade-legislativa/pesquisar-proposicoes"
S = requests.Session(); S.headers.update(H)
t = S.get(U, timeout=60).text; i = t.find("form_pesquisa_proposicoes")
f = {k: v for k, v in re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', t[i:i + 20000])}
f.update({"tipo": "2c907f7801d41f2001024943e5ec004a", "ano": "2025", "numero": "", "autor": "[autor]", "assunto": "[assunto]", "assunto2": "[assunto2]", "fase": "[Selecione]", "paginaRequerida": "1", "buscarPorProtocolo": "false"})
r = S.post("https://www.cmbh.mg.gov.br/sites/all/modules/proposicoes/pesquisar.php", data=f, timeout=90, headers={"referer": U, "x-requested-with": "XMLHttpRequest"})
txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", html.unescape(r.text)))
print("BHR", r.status_code, len(r.text), txt[:2500], flush=True)
print("BHA", sorted(set(re.findall(r'data-caminho="([^"]+)"', r.text)))[:5], re.findall(r"(?:de|total)\s*(\d+)\s*(?:resultado|proposi|registro)", txt, re.I)[:5], flush=True)
r = requests.get("http://45.4.247.157/leg/salvador/LEG_SYS_produtividade_parlamentar_proposicao/", headers=H, timeout=60); t = r.text
i = t.find("scGridTabela") if "scGridTabela" in t else 0
body = t[t.find("<body"):]
print("SSA", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", html.unescape(re.sub(r"<(script|style)[\s\S]*?</\1>", "", body))))[:3000], flush=True)
print("SSAEXP", sorted(set(re.findall(r"nmgp_opcao=(\w+)|(csv|xls|json|pdf)_", t, re.I)))[:20], flush=True)
