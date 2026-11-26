"""Sonda temporária: Sorocaba e Várzea Grande no Câmara sem Papel."""
import sys, re, requests
sys.path.insert(0, "coleta")
from assembleias_sapl import H
for h in ["https://sorocaba.camarasempapel.com.br", "https://varzeagrande.camarasempapel.com.br", "https://cachoeiro.nopapercloud.com.br"]:
    for p in ["/spl/consulta-autor.aspx", "/", "/spl/"]:
        try:
            r = requests.get(h + p, headers=H, timeout=20)
            print("T", h, p, r.status_code, r.url[:90], len(r.text), "producao" if "consulta-producao" in r.text else "", "| captcha" if re.search("captcha", r.text, re.I) else "", sorted(set(re.findall(r'href="([^"]*\.aspx[^"]*)"', r.text)))[:8], flush=True)
        except Exception as e: print("T", h, p, "falhou", repr(e)[:100], flush=True)
