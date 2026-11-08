import re, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from saida_br import get
from assembleia_rs import lista
for pg in (1, 2, 3):
    t = get("https://ww4.al.rs.gov.br/legislativo/pesquisa", {"nomeProponente": "Sofia Cavedon", "anoProposicao": 2025, "pagina": pg}).text
    L = lista(t); print(pg, len(L), [x["siglaTipoProposicao"].strip() + x["nroProposicao"] for x in L[:3]], "linhas tabela:", t.count('<td> <a href="/proposicao/') + t.count('href="/proposicao/'))
    print("  pag:", sorted(set(re.findall(r'pagina[=\'":\s]+(\d+)', t)))[:20], re.findall(r'(\d+)\s*(?:registros|resultados|proposi[cç][oõ]es encontradas)', t)[:3])
