"""Sonda 7: BA (lista filtrada por deputado no sistema antigo e o sistema novo NoPaper)."""
import re
from pathlib import Path
import requests
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"}
S = requests.Session(); S.headers.update(H)
O = Path(__file__).resolve().parents[1] / "site" / "data" / "_sonda"; O.mkdir(exist_ok=True)
def salva(nome, u, **kw):
    try:
        r = S.get(u, timeout=40, **kw); (O / f"{nome}.html").write_text(r.text[:600000]); print(nome, r.status_code, len(r.text), r.url)
    except Exception as e: print(nome, "erro", e)
salva("ba_lista_dep", "https://www.al.ba.gov.br/atividade-legislativa-nova/proposicoes", params={"deputado": "4049", "dataInicio": "01/02/2023", "dataFim": "31/12/2026"})
salva("ba_lista_dep_p2", "https://www.al.ba.gov.br/atividade-legislativa-nova/proposicoes", params={"deputado": "4049", "dataInicio": "01/02/2023", "dataFim": "31/12/2026", "page": "2"})
salva("np_home", "https://albalegis.nopapercloud.com.br/spl/")
salva("np_cons", "https://albalegis.nopapercloud.com.br/spl/consulta-producao.aspx")
salva("np_parl", "https://albalegis.nopapercloud.com.br/spl/parlamentar.aspx")
salva("np_robots", "https://albalegis.nopapercloud.com.br/robots.txt")
