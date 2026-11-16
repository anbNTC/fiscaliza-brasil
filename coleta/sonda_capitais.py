"""Sonda temporária: como BH, Salvador e Cuiabá entregam as proposições (formulário, JSON por trás da página)."""
import re, sys, html
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
def pg(u, acc="text/html"):
    r = get(u, headers={**H, "accept": acc}, timeout=60); return (r.status_code, r.text) if r is not None else (None, "")
# BH: formulário de pesquisa de proposições
st, t = pg("https://www.cmbh.mg.gov.br/atividade-legislativa/pesquisar-proposicoes")
print("BHFORM", st, sorted(set(re.findall(r'<(?:input|select)[^>]*name="([^"]+)"', t)))[:40], re.findall(r'<form[^>]*action="([^"]*)"', t)[:4], flush=True)
st, t = pg("https://www.cmbh.mg.gov.br/transparencia/atuacao-dos-vereadores")
print("BHATU", st, len(t), sorted(set(re.findall(r'href="([^"]*(?:vereador|atuacao|csv|xls|json|proposic)[^"]*)"', t, re.I)))[:30], flush=True)
print("BHATUTXT", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))[3000:4500], flush=True)
# Salvador: script da consulta
st, t = pg("https://cmsalvador.sys.inf.br/con-files/scripts.js", "*/*")
print("SSA", st, len(t), sorted(set(re.findall(r'["\']((?:https?:)?/?[\w./-]*(?:\.php|\.asp|\.json|/api/|ajax|LEG_SYS)[\w./?=&-]*)["\']', t)))[:40], flush=True)
print("SSATXT", t[:1500].replace("\n", " "), flush=True)
# Cuiabá
st, t = pg("https://legislativo.camaracuiaba.mt.gov.br/")
print("CBA", st, len(t), "| antirrobô" if re.search(r"captcha|TSPD|challenge", t[:30000], re.I) else "", sorted(set(re.findall(r'href="([^"]*(?:proposi|materia|projeto|consulta|vereador)[^"]*)"', t, re.I)))[:25], flush=True)
