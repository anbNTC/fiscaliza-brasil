"""Sonda temporária: estrutura da agenda do Senado (plenário e comissões) de hoje."""
import json, datetime, requests
h = datetime.date.today().strftime("%Y%m%d")
for u in [f"https://legis.senado.leg.br/dadosabertos/plenario/agenda/dia/{h}.json", f"https://legis.senado.leg.br/dadosabertos/comissao/agenda/{h}.json"]:
    j = requests.get(u, headers={"accept": "application/json"}, timeout=30).json()
    s = json.dumps(j, ensure_ascii=False, indent=1)
    print("#####", u); print("\n".join(l[:180] for l in s.splitlines()[:140]))
