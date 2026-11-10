"""Sonda (temporária): formato do CSV mensal de remuneração dos servidores da Câmara."""
import requests, re, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import saida_br
U = "https://www2.camara.leg.br/transparencia/recursos-humanos/remuneracao/relatorios-consolidados-por-ano-e-mes/2026/outubro-de-2026-csv"
for via in ("direto", "br"):
    try:
        r = requests.get(U, timeout=180, headers={"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}) if via == "direto" else saida_br.get(U, timeout=180, tentativas=1)
    except Exception as e: print(via, "erro", repr(e)[:200]); continue
    if r is None: print(via, "sem resposta"); continue
    print("==", via, r.status_code, r.headers.get("content-type"), len(r.content), r.url)
    b = r.content
    t = b.decode("utf-8", "ignore") if b[:3] == b"\xef\xbb\xbf" or b"\xc3" in b[:5000] else b.decode("latin-1")
    if "<html" in t[:2000].lower():
        print(re.findall(r'href="([^"]+(?:csv|download|@@)[^"]*)"', t)[:20]); print(t[:1500]); continue
    L = t.splitlines(); print("linhas:", len(L)); print("\n".join(L[:6]))
    sp = [l for l in L if re.search("SECRET.RIO PARLAMENTAR", l, re.I)]; print("SP:", len(sp)); print("\n".join(sp[:4]))
    break
