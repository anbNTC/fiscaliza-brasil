"""Sonda (temporária): Exportar depois de uma pesquisa (Curitiba)."""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
import prefeitura_curitiba as P
t = P.S.get(P.U, timeout=90).text
base = {P.P + "ddlAno": "2026", P.P + "ddlMes": "10", P.P + "rblAtivoInativo": "0", P.P + "txtNome": "", P.P + "ddlCargo": ""}
d = P.ocultos(t); d.update(base); d.update({"__EVENTTARGET": P.P + "lnkPesquisarModal", "__EVENTARGUMENT": ""})
t1 = P.S.post(P.U, data=d, timeout=300).text; print("pesquisa", len(t1), len(P.linhas(t1)))
for alvo in ("lnbExportar",):
    d = P.ocultos(t1); d.update(base); d.update({"__EVENTTARGET": P.P + alvo, "__EVENTARGUMENT": ""})
    r = P.S.post(P.U, data=d, timeout=900)
    print(alvo, r.status_code, r.headers.get("content-type"), r.headers.get("content-disposition"), len(r.content)); b = r.content; print(b[:300])
    if b[:2] == b"PK": open("/tmp/x.xlsx", "wb").write(b); print("xlsx/zip salvo")
    elif b"<html" not in b[:500].lower():
        t2 = b.decode("utf-8", "ignore") if b"\xc3" in b[:20000] else b.decode("latin-1"); L = t2.splitlines(); print("linhas", len(L)); print("\n".join(L[:4]))
        g = [l for l in L if re.search("GABINETE DO PREFEITO|VICE", l, re.I)]; print("gabinete:", len(g)); print("\n".join(g[:10]))
    else:
        m = re.search(r"VIEWSTATE\" value=\"([^\"]+)", b.decode("latin-1")); import base64
        try: print("erro:", base64.b64decode(m.group(1) + "==")[:200])
        except Exception: pass
d = P.ocultos(t1); d.update(base); d.update({"__EVENTTARGET": P.P + "ucPaginadorBaixo$2_pg2", "__EVENTARGUMENT": ""})
t3 = P.S.post(P.U, data=d, timeout=300).text; print("página 2:", P.linhas(t3)[:2])
