import json, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from saida_br import get
j = get("https://www3.al.es.gov.br/api/publico/parlamentar/", {"parlamentarID": 40}, timeout=180).json()
p = j["parlamentares"][0] if "parlamentares" in j else j
print("chaves:", list(p.keys()))
for k, v in p.items():
    if isinstance(v, list): print(k, len(v), json.dumps(v[:2], ensure_ascii=False)[:700])
    elif isinstance(v, dict): print(k, json.dumps(v, ensure_ascii=False)[:500])
r = get("https://www3.al.es.gov.br/api/publico/proposicao/", {"pag": 1, "qtd": 100, "dataInicio": "2023-02-01"}, timeout=180)
d = r.json(); print("total desde 2023:", d.get("total"), "bytes pág 100:", len(r.content), "itens:", len(d.get("Data", [])))
print({k: (v if not isinstance(v, (list, dict)) else "...") for k, v in d["Data"][-1].items()})
