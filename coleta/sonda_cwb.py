"""Sonda (temporária): conjunto "Relações de servidores, cargos e encargos" do portal de dados abertos de Curitiba."""
import requests, re, html
S = requests.Session(); S.headers.update({"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"})
B = "https://dadosabertos.curitiba.pr.gov.br"
t = S.get(B + "/conjuntodado/", timeout=60).text
i = t.find("servidores, cargos"); bloco = t[max(0, i - 1500): i + 300]
print(bloco); ch = re.findall(r"(?:chave=|/)([a-f0-9]{8}-[a-f0-9-]{27})", bloco); print("chaves perto do título:", ch)
for c in ch[-1:]:
    d = S.get(B + "/conjuntodado/detalhe/?chave=" + c, timeout=60).text
    print(" ".join(re.sub(r"<[^>]+>", " ", html.unescape(d.split("<body", 1)[-1])).split())[:2500])
    for u in sorted(set(re.findall(r'href="([^"]+\.(?:csv|zip|xlsx?|json)[^"]*)"', d, re.I)))[:40]: print("ARQ", u)
    for u in sorted(set(re.findall(r'href="(/[^"]*(?:download|arquivo|recurso)[^"]*)"', d, re.I)))[:40]: print("LINK", u)
