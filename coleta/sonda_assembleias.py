"""Sonda 6: guarda o HTML completo das páginas de proposições de SC e BA."""
import json, re
from pathlib import Path
import requests
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"}
S = requests.Session(); S.headers.update(H)
O = Path(__file__).resolve().parents[1] / "site" / "data" / "_sonda"; O.mkdir(exist_ok=True)
def salva(nome, u, **kw):
    try:
        r = S.get(u, timeout=40, **kw); (O / f"{nome}.html").write_text(r.text[:600000]); print(nome, r.status_code, len(r.text), r.url)
    except Exception as e: print(nome, "erro", e)
salva("sc_lista", "https://portalelegis.alesc.sc.gov.br/proposicoes/processo-legislativo")
salva("sc_lista_p2", "https://portalelegis.alesc.sc.gov.br/proposicoes/processo-legislativo?page=2")
salva("sc_ativ", "https://portalelegis.alesc.sc.gov.br/proposicoes/atividade-parlamentar")
salva("sc_prop", "https://portalelegis.alesc.sc.gov.br/proposicoes/5GR8Z/tramitacoes")
salva("sc_sessoes", "https://portalelegis.alesc.sc.gov.br/sessoes-plenarias")
salva("ba_ano", "https://www.al.ba.gov.br/atividade-legislativa/proposicoes-por-ano")
salva("ba_prop", "https://www.al.ba.gov.br/atividade-legislativa/proposicao/PL.-24.054-2021")
salva("ba_nova", "https://www.al.ba.gov.br/atividade-legislativa-nova/proposicoes")
salva("ba_deps", "https://www.al.ba.gov.br/deputados/legislatura-atual")
