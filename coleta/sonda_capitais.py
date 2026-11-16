"""Sonda temporária: formulário de proposições da CMBH e script da consulta de Salvador."""
import re, sys, html
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
def pg(u, acc="text/html"):
    r = get(u, headers={**H, "accept": acc}, timeout=60); return (r.status_code, r.text) if r is not None else (None, "")
st, t = pg("https://www.cmbh.mg.gov.br/atividade-legislativa/pesquisar-proposicoes")
i = t.find('name="autor"'); print("BHAUTOR", re.sub(r"\s+", " ", t[i - 200:i + 1500]), flush=True)
i = t.find('name="tipo"'); print("BHTIPO", re.sub(r"\s+", " ", t[i - 100:i + 900]), flush=True)
for k in ("buscaViaUrl", "stormCodex", "metodo", "paginaRequerida", "urlProposicao"):
    i = t.find(f'name="{k}"'); print("BHF", k, re.sub(r"\s+", " ", t[max(0, i - 150):i + 150]), flush=True)
print("BHJS", sorted(set(re.findall(r'src="([^"]*\.js[^"]*)"', t)))[-12:], flush=True)
st, t = pg("https://cmsalvador.sys.inf.br/con-files/scripts.js", "*/*")
print("SSAJS", t.replace("\n", " "), flush=True)
st, t = pg("https://cmsalvador.sys.inf.br/consulta.html")
print("SSAHTML", re.sub(r"\s+", " ", t)[:3300], flush=True)
