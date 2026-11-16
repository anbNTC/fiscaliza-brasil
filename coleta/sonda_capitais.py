"""Sonda temporária: que sistema cada câmara de capital usa (SAPL do Interlegis, API própria, dados abertos).
Só lê páginas públicas; quem tiver captcha ou bloqueio antirrobô fica de fora."""
import re, sys, requests
sys.path.insert(0, "coleta")
from assembleias_sapl import H
CAP = {"Maceió": "maceio.al.leg.br", "Macapá": "macapa.ap.leg.br", "Manaus": "cmm.am.gov.br", "Salvador": "cms.ba.gov.br", "Vitória": "cmv.es.gov.br",
       "Goiânia": "goiania.go.leg.br", "São Luís": "saoluis.ma.leg.br", "Cuiabá": "cuiaba.mt.leg.br", "Campo Grande": "camara.ms.gov.br", "Belo Horizonte": "cmbh.mg.gov.br",
       "Belém": "cmb.pa.gov.br", "Teresina": "teresina.pi.leg.br", "Recife": "recife.pe.leg.br", "Rio de Janeiro": "camara.rio", "Porto Alegre": "camarapoa.rs.gov.br",
       "Porto Velho": "portovelho.ro.leg.br", "Boa Vista": "boavista.rr.leg.br", "Florianópolis": "cmf.sc.gov.br", "Aracaju": "aracaju.se.leg.br", "Palmas": "palmas.to.leg.br"}
DICA = re.compile(r'href="([^"]*(?:sapl|/api|dados-?abertos|dadosabertos|proposic|materia|legisla|projeto|splegis|consulta)[^"]*)"', re.I)
for cid, dom in CAP.items():
    achou = False
    for b in [f"https://sapl.{dom}", f"https://{dom}", f"https://www.{dom}", f"https://sapl.{dom.split('.', 1)[1]}" if dom.count('.') > 2 else None]:
        if not b: continue
        try:
            r = requests.get(f"{b}/api/materia/materialegislativa/", params={"ano": 2025, "page_size": 1}, headers=H, timeout=15)
            if r.ok and "json" in r.headers.get("content-type", ""):
                print("SAPL", cid, b, r.json().get("pagination", {}).get("total_entries"), flush=True); achou = True; break
        except Exception: pass
    if achou: continue
    for b in [f"https://www.{dom}", f"https://{dom}"]:
        try:
            r = requests.get(b, headers=H, timeout=20)
            t = r.text; bot = bool(re.search(r"captcha|TSPD|cf-chl|challenge-platform|Access Denied", t[:20000], re.I))
            dicas = sorted(set(x for x in DICA.findall(t)))[:14]
            print("SITE", cid, b, r.status_code, len(t), "| antirrobô" if bot else "", "|", dicas, flush=True); break
        except Exception as e: print("SITE", cid, b, "falhou", repr(e)[:90], flush=True)
