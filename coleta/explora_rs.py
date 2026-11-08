import re, sys, html
sys.path.insert(0, __import__("os").path.dirname(__file__))
from saida_br import get
t = get("https://ww4.al.rs.gov.br/legislativo").text
sel = re.search(r'<select name="nomeProponente"[\s\S]*?</select>', t).group(0)
ops = [html.unescape(x).strip() for x in re.findall(r'<option value="([^"]*)"', sel) if x.strip()]
print(len(ops), "proponentes; amostra:", ops[:15], ops[-10:])
tipos = re.findall(r'<option value="([A-Z]+)">([^<]+)</option>', re.search(r'<select name="siglaTipoProposicao"[\s\S]*?</select>', t).group(0))
print("tipos:", tipos)
dep = next((o for o in ops if "Valdeci" in o or "Sofia" in o), ops[5])
r = get("https://ww4.al.rs.gov.br/legislativo/pesquisa", {"nomeProponente": dep, "anoProposicao": "2025", "pagina": 1})
t = r.text; print("dep:", dep, "bytes", len(t))
i = t.find("resultado"); j = t.find("pesquisar-form")
m = re.search(r'(<div class="main-content[\s\S]{0,6000})', t)
print(re.sub(r"\n\s*\n", "\n", re.sub(r"<!--[\s\S]*?-->", "", m.group(1) if m else t[-8000:]))[:6000])
