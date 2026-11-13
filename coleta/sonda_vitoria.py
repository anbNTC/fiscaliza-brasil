"""Sonda temporária: nova tentativa na transparência de Vitória (ES), direto e pela saída do Brasil."""
import sys, re, requests
sys.path.insert(0, "coleta")
from prefeituras_abertas import H
from saida_br import get as gbr
for u in ["https://transparencia.vitoria.es.gov.br/", "https://transparencia.vitoria.es.gov.br/Pessoal.aspx", "https://transparencia.vitoria.es.gov.br/DadosAbertos.aspx",
          "https://dados.vitoria.es.gov.br/api/3/action/package_search?q=servidores&rows=5", "https://www.vitoria.es.gov.br/"]:
    for nome, f in (("direto", lambda u: requests.get(u, headers=H, timeout=30)), ("br", lambda u: gbr(u, headers=H, timeout=60))):
        try:
            r = f(u)
            t = r.text if r is not None else ""
            print("VIT", nome, u, r.status_code if r is not None else None, len(t), re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))[:200], flush=True)
            links = sorted(set(re.findall(r'href="([^"]*(?:[Pp]essoal|[Ss]ervidor|[Ff]olha|[Rr]emunera|[Dd]ados|\.csv)[^"]*)"', t)))[:25]
            if links: print("LNK", links, flush=True)
        except Exception as e: print("VIT", nome, u, "falhou", repr(e)[:150], flush=True)
