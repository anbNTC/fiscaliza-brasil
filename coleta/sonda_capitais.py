"""Sonda temporária: exportação da grade de produtividade parlamentar de Salvador (ScriptCase)."""
import re, sys, html, requests
sys.path.insert(0, "coleta")
from assembleias_sapl import H
B = "http://45.4.247.157/leg/salvador/LEG_SYS_produtividade_parlamentar_proposicao/"
S = requests.Session(); S.headers.update(H)
t = S.get(B, timeout=60).text
print("FORMS", re.findall(r'<form[^>]*name="([^"]+)"[^>]*action="([^"]*)"', t)[:8], flush=True)
print("CAMPOS", sorted(set(re.findall(r'name="(nm\w+|sc_\w+|script_case_\w+)"', t)))[:30], flush=True)
print("AJAX", sorted(set(re.findall(r'["\']([\w./]*index\.php\?[^"\']{0,120})["\']', t)))[:15], flush=True)
for op in ["csv", "json", "xls"]:
    try:
        r = S.post(B + "index.php", data={"nmgp_opcao": op, "script_case_init": re.search(r'script_case_init["\']?\s*(?:value=|:)\s*["\']?(\d+)', t).group(1) if re.search(r'script_case_init["\']?\s*(?:value=|:)\s*["\']?(\d+)', t) else "1"}, timeout=60)
        tx = r.text
        print("EXP", op, r.status_code, r.headers.get("content-type"), len(tx), re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", tx))[:600], "| links:", re.findall(r'["\']([^"\']*\.(?:csv|json|xls)x?)["\']', tx)[:5], flush=True)
    except Exception as e: print("EXP", op, "falhou", repr(e)[:150], flush=True)

import io, openpyxl
r = S.post(B + "index.php", data={"nmgp_opcao": "xls"}, timeout=60)
u = re.search(r"window\.location='([^']+)'", r.text).group(1)
b = S.get("http://45.4.247.157" + u, timeout=120).content
wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True)
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True)); print("XLS", ws.title, len(rows), flush=True)
    for x in rows[:14]: print("ROW", x, flush=True)
print("FILTRO", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t[t.find("FResumo_search"):t.find("FResumo_search") + 3000]))[:800], flush=True)
