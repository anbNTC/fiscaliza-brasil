"""Sonda (temporária): botão Exportar da consulta de remuneração de Curitiba."""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
import prefeitura_curitiba as P
t = P.S.get(P.U, timeout=90).text
d = P.ocultos(t); d.update({P.P + "ddlAno": "2026", P.P + "ddlMes": "10", P.P + "rblAtivoInativo": "0", P.P + "txtNome": "", P.P + "ddlCargo": "", "__EVENTTARGET": P.P + "lnbExportar", "__EVENTARGUMENT": ""})
r = P.S.post(P.U, data=d, timeout=600)
print(r.status_code, r.headers.get("content-type"), r.headers.get("content-disposition"), len(r.content))
b = r.content
print(b[:600])
if b[:2] == b"PK": print("zip/xlsx")
else:
    t2 = b.decode("utf-8", "ignore") if b"\xc3" in b[:20000] else b.decode("latin-1")
    L = t2.splitlines(); print("linhas", len(L)); print("\n".join(L[:5]))
    g = [l for l in L if re.search("GABINETE DO PREFEITO|VICE-PREFEIT|VICE PREFEIT", l, re.I)]; print("gabinete:", len(g)); print("\n".join(g[:8]))
