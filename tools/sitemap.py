"""Gera site/sitemap.xml para o Google: páginas fixas, partidos, fichas (federais, senadores, governadores, deputados estaduais)
e as páginas de cada estado e cidade (/uf/PR, /cidade/PR/75353), servidas pelo _worker.js com título e descrição próprios."""
import json, urllib.parse
from pathlib import Path
S = Path(__file__).resolve().parents[1] / "site"; D = S / "data"; O = "https://fiscalizaja.com.br"
q = lambda s: urllib.parse.quote(str(s), safe="/")
u = ["/", "/fiscalize", "/distrital", "/links"]
try: u += ["/partido/" + q(p["s"]) for p in json.load(open(D / "partidos.json"))["partidos"]]
except Exception: pass
BR = json.load(open(D / "br.json"))
u += [f"/p/c/{d[0]}" for d in BR["dep"]] + [f"/p/s/{x[0]}" for x in BR["sen"]]
for uf in sorted(BR["ufs"]):
    u.append(f"/uf/{uf}")
    if BR["ufs"][uf].get("gov"): u.append(f"/p/g/{uf}/0/22")
    try: U = json.load(open(D / "uf" / f"{uf}.json"))
    except Exception: continue
    u += [f"/p/e/{uf}/22/{i}" for i in range(len(U.get("de22", [])))]
    u += [f"/cidade/{uf}/{ue}" for ue in sorted(U.get("mun", {}))]
x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{O}{p}</loc></url>\n" for p in dict.fromkeys(u)) + "</urlset>\n"
(S / "sitemap.xml").write_text(x); print("sitemap:", len(set(u)), "endereços")
