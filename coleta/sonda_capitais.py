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
