"""Sonda 5: estrutura das páginas de proposições da ALESC (SC) e da ALBA (BA), robots.txt e APIs usadas pelas páginas novas."""
import json, re
from pathlib import Path
from urllib.parse import urljoin
import requests
H = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"}
U = ["https://portalelegis.alesc.sc.gov.br/robots.txt", "https://portalelegis.alesc.sc.gov.br/proposicoes/processo-legislativo",
     "https://portalelegis.alesc.sc.gov.br/proposicoes/atividade-parlamentar", "https://portalelegis.alesc.sc.gov.br/proposicoes/5GR8Z",
     "https://www.al.ba.gov.br/robots.txt", "https://www.al.ba.gov.br/atividade-legislativa/proposicoes-por-ano",
     "https://www.al.ba.gov.br/atividade-legislativa/proposicao/PL.-24.054-2021", "https://www.al.ba.gov.br/atividade-legislativa-nova/proposicoes",
     "https://www.al.ba.gov.br/deputados/legislatura-atual"]
R = []
for u in U:
    try:
        r = requests.get(u, headers=H, timeout=40); t = r.text
        body = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", t)
        js = [urljoin(r.url, s) for s in re.findall(r'<script[^>]+src="([^"]+)"', t)]
        api = set(re.findall(r'["\'`](/?(?:api|ws|rest|graphql)[^"\'`\s]{2,120})["\'`]', t))
        for j in js[:10]:
            try: api |= set(re.findall(r'["\'`](/?(?:api|ws|rest)/[^"\'`\s]{2,120}|https?://[^"\'`\s]*(?:api|/ws/)[^"\'`\s]{0,120})["\'`]', requests.get(j, headers=H, timeout=20).text))
            except Exception: pass
        R.append({"u": u, "st": r.status_code, "final": r.url, "ct": r.headers.get("content-type"), "api": sorted(api)[:80], "js": js[:15],
                  "forms": re.findall(r"<form[\s\S]{0,1500}?</form>", t)[:2], "html": body[:14000]})
    except Exception as e: R.append({"u": u, "erro": str(e)[:200]})
json.dump(R, open(Path(__file__).resolve().parents[1] / "site" / "data" / "_sonda_assembleias.json", "w"), ensure_ascii=False, indent=1)
