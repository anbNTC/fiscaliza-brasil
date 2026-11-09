"""Temporário: olha o CSV de funcionários da Câmara."""
import requests, csv, io, collections
t = requests.get("https://dadosabertos.camara.leg.br/arquivos/funcionarios/csv/funcionarios.csv", timeout=120).content.decode("utf-8-sig", "replace")
print(len(t)); print(t[:1500])
L = list(csv.DictReader(io.StringIO(t), delimiter=";")); print(len(L), list(L[0].keys()))
for k in L[0]: print(k, collections.Counter(r[k] for r in L).most_common(4))
x = [r for r in L if "204396" in " ".join(r.values())]; print(len(x)); [print(r) for r in x[:5]]
