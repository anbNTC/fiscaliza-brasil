"""Sonda (temporária): APIs do Senado para autoria de proposições e discursos."""
import requests, json
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0", "accept": "application/json"}
for u in ("https://legis.senado.leg.br/dadosabertos/processo?codigoParlamentarAutor=345&dataInicioApresentacao=2026-01-01",
          "https://legis.senado.leg.br/dadosabertos/senador/345/autorias.json?ano=2026",
          "https://legis.senado.leg.br/dadosabertos/senador/345/discursos.json?dataInicio=20260101&dataFim=20261111"):
    try:
        r = requests.get(u, headers=H, timeout=120); print("==", u, r.status_code, len(r.content))
        j = r.json(); s = json.dumps(j, ensure_ascii=False)
        print(s[:1800])
        if isinstance(j, list): print("itens", len(j), "chaves", sorted(j[0].keys()) if j else None)
    except Exception as e: print(u, repr(e)[:200])
