"""Sonda temporária: câmaras de capitais que não respondem a acesso de fora do Brasil (pela saída BR) e sistemas próprios."""
import re, sys
sys.path.insert(0, "coleta")
from saida_br import get
from assembleias_sapl import H
DICA = re.compile(r'href="([^"]*(?:sapl|/api|dados-?abertos|dadosabertos|proposic|materia|projeto|consulta|transparen)[^"]*)"', re.I)
for cid, b in [("Rio", "https://www.camara.rio"), ("Rio-sapl", "https://sapl.camara.rio/api/materia/materialegislativa/?ano=2025&page_size=1"),
               ("POA", "https://www.camarapoa.rs.gov.br"), ("POA-sapl", "https://sapl.camarapoa.rs.gov.br/api/materia/materialegislativa/?ano=2025&page_size=1"),
               ("Cuiabá", "https://www.cuiaba.mt.leg.br"), ("Cuiabá-sapl", "https://sapl.cuiaba.mt.leg.br/api/materia/materialegislativa/?ano=2025&page_size=1"),
               ("São Luís", "https://www.saoluis.ma.leg.br"), ("SL-sapl", "https://sapl.saoluis.ma.leg.br/api/materia/materialegislativa/?ano=2025&page_size=1"),
               ("Recife-sapl", "https://sapl.recife.pe.leg.br/api/materia/materialegislativa/?ano=2025&page_size=1"),
               ("Teresina-sapl", "https://sapl.teresina.pi.leg.br/api/materia/materialegislativa/?ano=2025&page_size=1"),
               ("Goiânia-sapl", "https://sapl.goiania.go.leg.br/api/materia/materialegislativa/?ano=2025&page_size=1"),
               ("Salvador", "https://cmsalvador.sys.inf.br/consulta.html"), ("BH", "https://www.cmbh.mg.gov.br/atividade-legislativa/pesquisar-proposicoes")]:
    try:
        r = get(b, headers={**H, "accept": "text/html,application/json"}, timeout=60)
        if r is None: print("CAP", cid, "sem resposta", flush=True); continue
        t = r.text; bot = bool(re.search(r"captcha|TSPD|cf-chl|challenge-platform|Access Denied", t[:30000], re.I))
        print("CAP", cid, r.status_code, len(t), "| antirrobô" if bot else "", "|", t[:160].replace("\n", " ") if "json" in r.headers.get("content-type", "") else sorted(set(DICA.findall(t)))[:16], flush=True)
        if cid in ("Salvador", "BH"): print("SCR", cid, sorted(set(re.findall(r'(?:src|action|fetch\(|url:)\s*=?\s*["\']([^"\']+)', t)))[:30], flush=True)
    except Exception as e: print("CAP", cid, "falhou", repr(e)[:120], flush=True)
