"""Temporário: lista recursos dos conjuntos de emendas estaduais (CKAN) e mostra o cabeçalho de cada CSV."""
import requests, io
H = {"user-agent": "Mozilla/5.0 FiscalizaBrasil/1.0"}
for base, pid in [("https://dados.pe.gov.br", "emendasparlamentaresestaduais"), ("https://www.dados.mg.gov.br", "portal_emendas_estaduais"), ("https://dadosabertos.go.gov.br", "emendas-parlamentares")]:
    r = requests.get(f"{base}/api/3/action/package_show", params={"id": pid}, headers=H, timeout=60).json()["result"]
    print("#####", base, len(r["resources"]))
    for x in r["resources"]:
        print("--", x["name"], "|", x.get("format"), "|", x["url"], "|", x.get("size"))
        if (x.get("format") or "").lower().strip(".") in ("csv", "txt") or x["url"].lower().endswith(".csv"):
            try:
                with requests.get(x["url"], headers=H, timeout=60, stream=True) as g:
                    b = next(g.iter_content(3000))
                for enc in ("utf-8", "latin-1"):
                    try: t = b.decode(enc); break
                    except UnicodeDecodeError: pass
                print("   ", "\n    ".join(t.splitlines()[:3])[:1200])
            except Exception as e: print("   erro", e)
